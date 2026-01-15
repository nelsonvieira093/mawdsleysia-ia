#E:\MAWDSLEYS-AGENTE\backend\api\routes\ingest_audio.py

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import tempfile
import os
import openai

from database.session import get_db
from services.ingest_service import process_ingest

router = APIRouter(tags=["Ingest Audio"])


@router.post("/ingest/audio")
async def ingest_audio(
    audio: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Recebe áudio, transcreve com Whisper e executa o ingest padrão:
    áudio -> texto -> capture -> note -> followups
    """

    temp_path = None

    try:
        # =====================================================
        # 1. Salva áudio temporário
        # =====================================================
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            tmp.write(await audio.read())
            temp_path = tmp.name

        if not os.path.exists(temp_path):
            raise HTTPException(status_code=400, detail="Falha ao salvar áudio")

        # =====================================================
        # 2. Transcrição (Whisper)
        # =====================================================
        with open(temp_path, "rb") as audio_file:
            transcript = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file,
                language="pt"
            )

        text = transcript.get("text", "").strip()

        if not text:
            raise HTTPException(
                status_code=400,
                detail="Não foi possível reconhecer texto no áudio"
            )

        # =====================================================
        # 3. Pipeline normal de ingest
        # =====================================================
        result = process_ingest(
            db=db,
            raw_text=text,
            source="audio"
        )

        return {
            "status": "ok",
            "transcription": text,
            "result": result
        }

    except HTTPException:
        raise

    except Exception as e:
        print("❌ ERRO INGEST AUDIO:", e)
        raise HTTPException(
            status_code=500,
            detail="Erro ao processar áudio"
        )

    finally:
        # =====================================================
        # 4. Limpeza do arquivo temporário
        # =====================================================
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

