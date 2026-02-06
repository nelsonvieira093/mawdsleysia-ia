# E:\MAWDSLEYS-AGENTE\backend\security\jwt.py

from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from jose import jwt, JWTError

# ⚠️ EM PRODUÇÃO: usar variável de ambiente
SECRET_KEY = "YOUR_SUPER_SECRET_KEY_CHANGE_IN_PRODUCTION"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 *  180 # 180 dias


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Cria um token JWT válido
    """
    to_encode = data.copy()

    expire = (
        datetime.utcnow() + expires_delta
        if expires_delta
        else datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodifica token JWT e valida assinatura + expiração
    """
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Alias semântico para decode_access_token
    """
    return decode_access_token(token)


def get_user_id_from_token(token: str) -> Optional[int]:
    """
    Extrai o user_id do token JWT - CORRIGIDO
    """
    payload = decode_access_token(token)
    if not payload:
        return None
    
    # 1. Tenta user_id (que está no token do login)
    user_id = payload.get("user_id")
    if user_id is not None:
        try:
            return int(user_id)
        except (TypeError, ValueError):
            pass
    
    # 2. Tenta sub (compatibilidade)
    sub = payload.get("sub")
    if sub is not None:
        try:
            return int(sub)
        except (TypeError, ValueError):
            pass
    
    return None