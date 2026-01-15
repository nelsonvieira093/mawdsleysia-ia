import os
import logging
import requests
from  datetime import datetime

# IMPORTAÇÃO CORRETA (com backend antes de 'integrations' e 'database')
from integrations.whatsapp.models import Conversation, WAmessage
from database.session import SessionLocal

logger = logging.getLogger("whatsapp_service")

# ==============================
#  CONFIGURAÇÕES DO PROVEDOR
# ==============================
PROVIDER = os.getenv("WHATSAPP_PROVIDER", "mock")

# 🔥 Correção: variáveis certas para Zenvia
ZENVIA_API_KEY = os.getenv("ZENVIA_API_KEY", "")
ZENVIA_CHANNEL_ID = os.getenv("ZENVIA_CHANNEL_ID", "")

# 🔥 Correção: API_KEY usada no /status do router.py
API_KEY = ZENVIA_API_KEY


def get_db():
    return SessionLocal()

# ==============================
#  Criar ou localizar conversa
# ==============================
def find_or_create_conversation(external_id: str, name: str = None):
    db = get_db()
    try:
        conv = db.query(Conversation).filter(
            Conversation.external_id == external_id
        ).first()

        if conv:
            return conv

        conv = Conversation(
            external_id=external_id,
            name=name or external_id,
            updated_at=datetime.utcnow(),
        )

        db.add(conv)
        db.commit()
        db.refresh(conv)
        return conv
    finally:
        db.close()

# ==============================
#  Salvar mensagem recebida
# ==============================
def save_incoming_message(external_id: str, message_id: str, text: str, media_url=None):
    db = get_db()
    try:
        conv = db.query(Conversation).filter(
            Conversation.external_id == external_id
        ).first()

        if not conv:
            conv = Conversation(
                external_id=external_id,
                name=external_id,
                updated_at=datetime.utcnow(),
                unread=True
            )
            db.add(conv)
            db.flush()

        msg = WAmessage(
            conversation_id=conv.id,
            external_id=message_id,
            direction="in",
            text=text,
            media_url=media_url,
            created_at=datetime.utcnow(),
            status="received"
        )

        conv.last_message = text
        conv.unread = True
        conv.updated_at = datetime.utcnow()

        db.add(msg)
        db.commit()
        db.refresh(msg)
        db.refresh(conv)

        return conv, msg

    finally:
        db.close()

# ==============================
#  Salvar mensagem enviada
# ==============================
def save_outgoing_message(conversation_id: int, provider_msg_id: str, text: str):
    db = get_db()
    try:
        msg = WAmessage(
            conversation_id=conversation_id,
            external_id=provider_msg_id,
            direction="out",
            text=text,
            created_at=datetime.utcnow(),
            status="sent"
        )

        conv = db.query(Conversation).get(conversation_id)
        conv.last_message = text
        conv.unread = False
        conv.updated_at = datetime.utcnow()

        db.add(msg)
        db.commit()
        db.refresh(msg)

        return msg
    finally:
        db.close()

# ==============================
#  Enviar mensagem via Zenvia
# ==============================
def send_message_to_provider(to: str, text: str):
    # Modo de testes / desenvolvimento
    if PROVIDER == "mock":
        return {"ok": True, "provider_id": f"mock-{datetime.utcnow().timestamp()}"}

    if PROVIDER != "zenvia":
        raise RuntimeError("Provider desconhecido")

    url = "https://api.zenvia.com/v2/channels/whatsapp/messages"

    headers = {
        "X-API-TOKEN": ZENVIA_API_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "from ": ZENVIA_CHANNEL_ID,
        "to": to,
        "contents": [
            {
                "type": "text",
                "text": text
            }
        ]
    }

    r = requests.post(url, json=payload, headers=headers)

    if r.status_code >= 300:
        logger.error(r.text)
        return {"ok": False}

    provider_id = r.json().get("id") or f"zenvia-{datetime.utcnow()}"

    return {"ok": True, "provider_id": provider_id}
