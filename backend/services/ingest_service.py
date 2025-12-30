#E:\MAWDSLEYS-AGENTE\backend\services\ingest_service.py

from sqlalchemy.orm import Session
from datetime import date, timedelta

from services.ai_service import analyze_text

# MODELS
from models.capture import Capture
from models.note import Note
from models.followup import FollowUp
from models.tag import Tag
from models.ritual import Ritual
from models.person import Person
from models.note_tag import NoteTag



def process_ingest(db: Session, raw_text: str, source: str = "api"):
    """
    Pipeline completo de ingestão:
    raw_text -> capture -> note -> tags -> followups
    """

    try:
        print("🔹 Iniciando ingest")

        # =====================================================
        # 1. IA ANALISA TEXTO
        # =====================================================
        analysis = analyze_text(raw_text)
        print("🔹 Analysis:", analysis)

        # =====================================================
        # 2. CAPTURE
        # =====================================================
        capture = Capture(
            source=source,
            raw_text=raw_text,
            summary=analysis.get("summary"),
            processed=False,
        )
        db.add(capture)
        db.flush()
        print("✅ Capture criado:", capture.id)

        # =====================================================
        # 3. RITUAL
        # =====================================================
        ritual = None
        ritual_code = analysis.get("ritual_code")
        if ritual_code:
            ritual = db.query(Ritual).filter(Ritual.code == ritual_code).first()
            print("🔹 Ritual:", ritual_code)

        # =====================================================
        # 4. NOTE
        # =====================================================
        note = Note(
            capture_id=capture.id,
            ritual_id=ritual.id if ritual else None,
            content=analysis.get("summary") or raw_text,
        )
        db.add(note)
        db.flush()
        print("✅ Note criada:", note.id)

        # =====================================================
        # 5. TAGS
        # =====================================================
        for tag_name in analysis.get("tags", []):
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if tag:
                db.add(NoteTag(note_id=note.id, tag_id=tag.id))
                print("🏷️ Tag associada:", tag_name)

        # =====================================================
        # 6. FOLLOW-UPS
        # =====================================================
        followups_created = 0

        for fu in analysis.get("followups", []):
            owner = None
            owner_name = fu.get("owner")

            if owner_name:
                owner = db.query(Person).filter(
                    Person.name.ilike(owner_name)
                ).first()

            followup = FollowUp(
                description=fu.get("description"),
                owner_id=owner.id if owner else None,
                ritual_id=ritual.id if ritual else None,
                source_note_id=note.id,
                due_date=date.today() + timedelta(days=7),
                status="ABERTO",
            )
            db.add(followup)
            followups_created += 1
            print("📌 Follow-up criado")

        # =====================================================
        # 7. FINALIZA
        # =====================================================
        capture.processed = True
        db.commit()

        print("✅ Ingest finalizado com sucesso")

        return {
            "capture_id": str(capture.id),
            "note_id": str(note.id),
            "ritual": ritual.code if ritual else None,
            "followups_created": followups_created,
        }

    except Exception as e:
        print("❌ ERRO NO INGEST:", e)
        db.rollback()
        raise
