# E:\MAWDSLEYS-AGENTE\backend\api\routes\auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any

from security.jwt import create_access_token, decode_access_token, get_user_id_from_token
from security.admin_users import ADMIN_USERS

router = APIRouter(tags=["Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# ==========================
# SCHEMAS
# ==========================
class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    ok: bool
    access_token: str
    token_type: str
    user: dict


# ==========================
# AUTH DEPENDENCY (JWT)
# ==========================
async def require_any_auth(
    token: str = Depends(oauth2_scheme),
) -> Dict[str, Any]:

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Token de autenticação não fornecido",
        )

    # token is provided directly by the oauth2_scheme dependency
    user_id = get_user_id_from_token(token)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )

    # 🔴 CORREÇÃO CRÍTICA (AQUI)
    try:
        user_id = int(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido (user_id inválido)",
        )

    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido (payload ausente)",
        )

    return {
        "authenticated": True,
        "user_id": user_id,  # ✅ AGORA É INT
        "role": payload.get("role"),
        "is_admin": payload.get("is_admin"),
        "token": token,
    }


# ==========================
# LOGIN — ADMIN FIXO
# ==========================
@router.post("/login", response_model=TokenResponse)
def login(data: LoginIn):

    user = next(
        (
            u for u in ADMIN_USERS
            if u["email"] == data.email and u["password"] == data.password
        ),
        None
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
        )

    access_token = create_access_token(
        data={
            "sub": str(user["id"]),
            "user_id": user["id"],
            "email": user["email"],
            "role": user["role"],
            "is_admin": user["is_admin"],
        }
    )

    return {
        "ok": True,
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "is_admin": user["is_admin"],
        },
    }


# ==========================
# LOGIN ALTERNATIVO
# ==========================
@router.post("/admin-login", response_model=TokenResponse)
def admin_login(data: LoginIn):
    return login(data)
