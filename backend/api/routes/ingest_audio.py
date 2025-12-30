from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
import tempfile
import openai

from database.session import get_db
from services.ingest_service import process_ingest

router = APIRouter(tags=["Ingest Audio"])

@router.post("/ingest/audio")
async def ingest_audio(
    audio: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 1. Salva áudio temporariamente
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await audio.read())
        audio_path = tmp.name

    # 2. Transcrição (Whisper)
    with open(audio_path, "rb") as f:
        transcript = openai.Audio.transcribe(
            model="whisper-1",
            file=f
        )

    text = transcript["text"]

    # 3. Usa o MESMO ingest de texto
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
