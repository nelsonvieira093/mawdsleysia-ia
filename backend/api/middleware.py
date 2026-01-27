#E:\MAWDSLEYS-AGENTE\backend\api\middleware.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

JWT_SECRET = os.getenv("JWT_SECRET", "CHANGE_ME")
JWT_ALGORITHM = "HS256"


def require_any_auth(token: str = Depends(oauth2_scheme)):
    """
    Dependency de autenticação REAL.
    Compatível com TODO o backend atual.
    NÃO consome body.
    NÃO quebra parsing.
    """

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )

    return {
        "user_id": int(payload.get("user_id")),
        "id": int(payload.get("user_id")),
        "email": payload.get("email"),
        "name": payload.get("email", "Executivo"),
        "role": payload.get("role"),
        "is_admin": payload.get("is_admin", False),
    }

