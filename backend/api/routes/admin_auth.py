from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import timedelta
from passlib.context import CryptContext

from security.jwt import create_access_token

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


class AdminLoginRequest(BaseModel):
    email: str
    password: str


# 🔐 ADMINS FIXOS (COM HASH)
ADMIN_USERS = [
    {
        "id": 1,
        "name": "Nelson Vieira",
        "email": "nelsonronnyr40@gmail.com",
        "password": hash_password("Admin@2024"),
        "is_admin": True,
        "role": "super_admin",
    },
    {
        "id": 2,
        "name": "Daniela M. Carraro",
        "email": "danielac@mbbpharma.com.br",
        "password": hash_password("Daniela@123"),
        "is_admin": True,
        "role": "admin",
    },
]


@router.post("/admin-login")
async def admin_login(login_data: AdminLoginRequest):
    """Login especial para administradores fixos"""

    for user in ADMIN_USERS:
        if login_data.email == user["email"] and verify_password(
            login_data.password, user["password"]
        ):
            token_data = {
                "sub": str(user["id"]),   # OBRIGATÓRIO NO JWT
                "user_id": user["id"],
                "email": user["email"],
                "role": user["role"],
                "is_admin": user["is_admin"],
            }

            access_token = create_access_token(
                data=token_data,
                expires_delta=timedelta(hours=8),
            )

            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user["id"],
                    "name": user["name"],
                    "email": user["email"],
                    "is_admin": user["is_admin"],
                    "role": user["role"],
                },
            }

    raise HTTPException(
        status_code=401,
        detail="Credenciais inválidas. Acesso restrito aos administradores.",
    )


@router.get("/admin-users")
async def get_admin_users():
    """Lista admins (sem senha)"""
    return {
        "admins": [
            {k: v for k, v in user.items() if k != "password"}
            for user in ADMIN_USERS
        ]
    }
