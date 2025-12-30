# backend/security/jwt.py
from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Optional, Dict, Any

SECRET_KEY = "YOUR_SUPER_SECRET_KEY_CHANGE_IN_PRODUCTION"  # Mude para algo seguro!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24h

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Cria token JWT"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodifica e valida token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_token(token: str) -> Dict[str, Any]:
    """Verifica se o token é válido (alias para decode_access_token)"""
    return decode_access_token(token)


def get_user_id_from_token(token: str) -> Optional[str]:
    """Extrai o user_id do token"""
    payload = decode_access_token(token)
    if payload:
        return payload.get("sub")
    return None