#E:\MAWDSLEYS-AGENTE\backend\api\routes\admin_auth.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import timedelta
from passlib.context import CryptContext

from security.jwt import create_access_token

# 🔴 PREFIXO /api (OBRIGATÓRIO PARA BATER COM O FRONTEND)
router = APIRouter(prefix="/api", tags=["Admin Auth"])

# Contexto de hash (usado SOMENTE em runtime, nunca no import)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


class AdminLoginRequest(BaseModel):
    email: str
    password: str


# 🔐 ADMINS FIXOS (HASH JÁ GERADO — NÃO HASHAR NO IMPORT)
ADMIN_USERS = [
    {
        "id": 1,
        "name": "Nelson Vieira",
        "email": "nelsonronnyr40@gmail.com",
        # hash de "Admin@2024"
        "password": "$2b$12$7eJk7H0pZxCq0U1J7JZyV.4xKzW8Z0U3P0F2N1W6nQZ7FZyY9m5eK",
        "is_admin": True,
        "role": "super_admin",
    },
    {
        "id": 2,
        "name": "Daniela M. Carraro",
        "email": "danielac@mbbpharma.com.br",
        # hash de "Daniela@123"
        "password": "$2b$12$M4nZ4CwX3Xk9z2Kp5MZ1wO3s9z4F7XH2G8A2Z3ZxF7Yw1mJQ6L8a2",
        "is_admin": True,
        "role": "super_admin",
    },
]


@router.post("/admin-login")
async def admin_login(login_data: AdminLoginRequest):
    """
    Login especial para administradores fixos.
    """

    for user in ADMIN_USERS:
        if (
            login_data.email == user["email"]
            and verify_password(login_data.password, user["password"])
        ):
            token_data = {
                "sub": str(user["id"]),  # obrigatório no JWT
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
