# backend/api/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from database.session import get_db
from services.auth_service import register_user
from security.jwt import create_access_token, decode_access_token
from security.password import verify_password

router = APIRouter(tags=["Auth"])
security = HTTPBearer(auto_error=False)

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
# DEPENDENCY / MIDDLEWARE
# ==========================
async def require_any_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Dependency para rotas que requerem autenticação.
    Valida o token JWT e retorna o usuário autenticado.
    """
    # Se não houver credenciais, lança erro 401
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação não fornecido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        # Decodifica o token JWT
        payload = decode_access_token(token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido ou expirado"
            )
        
        # Importa aqui para evitar circular imports
        from models.user import User
        
        # Busca o usuário no banco
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado"
            )
        
        # Verifica se o usuário está ativo
        if hasattr(user, 'is_active') and not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário inativo"
            )
        
        return {
            "authenticated": True,
            "user_id": user.id,
            "user_email": user.email,
            "user_name": user.name,
            "token": token
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Erro na autenticação: {str(e)}"
        )


# Versão simplificada para desenvolvimento
async def require_any_auth_dev(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    Versão simplificada para desenvolvimento.
    Aceita qualquer token ou mesmo falta de token.
    """
    if credentials is None:
        # Em desenvolvimento, permite continuar sem token
        return {
            "authenticated": False,
            "user_id": None,
            "user_email": "anonymous@dev.com",
            "user_name": "Anonymous",
            "token": None,
            "dev_mode": True
        }
    
    token = credentials.credentials
    
    # Tenta decodificar o token real
    payload = decode_access_token(token)
    if payload:
        return {
            "authenticated": True,
            "user_id": payload.get("sub", 1),
            "user_email": payload.get("email", "dev@example.com"),
            "user_name": "Developer",
            "token": token,
            "dev_mode": True
        }
    
    # Em desenvolvimento, aceita qualquer token
    return {
        "authenticated": True,
        "user_id": 1,
        "user_email": "dev@example.com",
        "user_name": "Developer",
        "token": token,
        "dev_mode": True
    }

# ==========================
# SIGNUP
# ==========================
@router.post("/auth/signup", status_code=status.HTTP_201_CREATED)
def signup(data: SignupIn, db: Session = Depends(get_db)):
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
# LOGIN
# ==========================
@router.post("/auth/login", response_model=TokenResponse)
def login(data: LoginIn, db: Session = Depends(get_db)):
    from models.user import User

    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
        )

    if not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
        )

    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )

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