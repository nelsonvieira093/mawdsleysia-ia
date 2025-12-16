# backend/whatsapp/utils.py
import hmac
import hashlib
import os
from typing import Optional
from integrations.whatsapp.models import Conversation


def get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    return os.getenv(name, default)

def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verifica assinatura webhook (se o provedor usar HMAC SHA256)"""
    if not signature or not secret:
        return False
    computed = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    # alguns provedores usam header em base64 ou prefixed - adapte conforme necessário
    return hmac.compare_digest(computed, signature)
