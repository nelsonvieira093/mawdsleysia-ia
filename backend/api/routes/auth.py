# backend/api/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from datetime import timedelta

from backend.database.session import get_db
from backend.services.auth_service import register_user
from backend.security.jwt import create_access_token
from backend.security.password import verify_password

router = APIRouter(tags=["Auth"])

# ==========================
# SCHEMAS
# ==========================
class SignupIn(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    ok: bool
    access_token: str
    token_type: str
    user: dict

# ==========================
# SIGNUP
# ==========================
@router.post("/auth/signup", status_code=status.HTTP_201_CREATED)
def signup(data: SignupIn, db: Session = Depends(get_db)):
    """
    Cria um novo usuário no sistema.
    Recebe JSON: {"name": "...", "email": "...", "password": "..."}
    """
    try:
        user = register_user(
            db=db,
            name=data.name,
            email=data.email,
            password=data.password,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

    return {
        "ok": True,
        "message": "Usuário criado com sucesso",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "is_active": getattr(user, "is_active", True),
        },
    }

# ==========================
# LOGIN - VERSÃO CORRIGIDA
# ==========================
@router.post("/auth/login", response_model=TokenResponse)
def login(data: LoginIn, db: Session = Depends(get_db)):
    """
    Autentica o usuário e retorna JWT.
    Recebe JSON: {"email": "...", "password": "..."}
    """
    # 1. Busca o usuário pelo email
    from backend.models.user import User  # Ajuste conforme seu modelo
    
    user = db.query(User).filter(User.email == data.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
        )
    
    # 2. Verifica a senha
    if not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
        )
    
    # 3. Cria o token JWT
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )
    
    # 4. Retorna no formato que o frontend espera
    return {
        "ok": True,
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "is_active": getattr(user, "is_active", True),
        },
    }