# backend/integrations/whatsapp/router.py

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

# IMPORTAÇÕES CORRETAS (antes estavam erradas!)
from backend.integrations.whatsapp.models import Conversation, WAmessage
from backend.integrations.whatsapp import service
from backend.database.session import SessionLocal

from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])


class SendIn(BaseModel):
    to: str
    text: str


@router.get("/conversations")
def list_conversations():
    db = SessionLocal()
    try:
        data = db.query(Conversation).order_by(Conversation.updated_at.desc()).all()
        return [
            {
                "id": c.id,
                "external_id": c.external_id,
                "name": c.name,
                "last_message": c.last_message,
                "unread": c.unread,
                "updated_at": c.updated_at.isoformat() if c.updated_at else None,
            }
            for c in data
        ]
    finally:
        db.close()


@router.get("/messages/{conversation_id}")
def list_messages(conversation_id: int):
    db = SessionLocal()
    try:
        msgs = (
            db.query(WAmessage)
            .filter(WAmessage.conversation_id == conversation_id)
            .order_by(WAmessage.created_at.asc())
            .all()
        )
        return [
            {
                "id": m.id,
                "external_id": m.external_id,
                "direction": m.direction,
                "text": m.text,
                "media_url": m.media_url,
                "created_at": m.created_at.isoformat() if m.created_at else None,
                "status": m.status,
            }
            for m in msgs
        ]
    finally:
        db.close()


@router.post("/send")
def send(payload: SendIn):
    try:
        conv = service.find_or_create_conversation(payload.to, name=payload.to)

        provider_res = service.send_message_to_provider(payload.to, payload.text)
        if not provider_res.get("ok"):
            raise HTTPException(status_code=500, detail="Provider error")

        msg = service.save_outgoing_message(conv.id, provider_res["provider_id"], payload.text)
        return {"ok": True, "message_id": msg.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def zenvia_webhook(request: Request):
    body = await request.json()

    try:
        msg = body["message"]
        sender = msg["from"]
        msg_id = msg["id"]

        text = ""
        media = None

        content = msg["contents"][0]
        if content["type"] == "text":
            text = content["text"]
        elif content["type"] == "media":
            media = content["url"]

        conv, saved = service.save_incoming_message(
            sender, msg_id, text, media
        )

        return {"ok": True}

    except Exception as e:
        return JSONResponse(
            {"ok": False, "error": str(e)},
            status_code=400
        )


@router.get("/status")
def status():
    return {
        "provider": service.PROVIDER,
        "configured": bool(service.API_KEY),
        "timestamp": datetime.utcnow().isoformat(),
    }
