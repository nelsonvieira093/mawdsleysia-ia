from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class AdminLoginRequest(BaseModel):
    email: str
    password: str

# DOIS ADMINS FIXOS
ADMIN_USERS = [
    {
        "id": 1,
        "name": "Nelson Vieira",
        "email": "nelsonronnyr40@gmail.com",
        "password": "Admin@2024",
        "is_admin": True,
        "role": "super_admin"
    },
    {
        "id": 2,
        "name": "Daniela M. Carraro",
        "email": "danielac@mbbpharma.com.br",
        "password": "Daniela@123",
        "is_admin": True,
        "role": "admin"
    }
]

@router.post("/admin-login")
async def admin_login(login_data: AdminLoginRequest):
    """Login especial para os dois administradores"""
    
    # Procura o usuário
    for user in ADMIN_USERS:
        if (login_data.email == user["email"] and 
            login_data.password == user["password"]):
            
            return {
                "access_token": f"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.admin_token_{user['id']}_{user['name'].replace(' ', '_')}",
                "token_type": "bearer",
                "user": {
                    "id": user["id"],
                    "name": user["name"],
                    "email": user["email"],
                    "is_admin": user["is_admin"],
                    "role": user["role"],
                    "created_at": "2024-01-01T00:00:00Z"
                }
            }
    
    # Se não encontrar
    raise HTTPException(
        status_code=401,
        detail="Credenciais inválidas. Acesso restrito aos administradores cadastrados."
    )

@router.post("/admin-signup")
async def admin_signup(user_data: dict):
    """Signup que cria apenas os dois administradores"""
    
    email = user_data.get("email", "")
    password = user_data.get("password", "")
    
    # Verifica se é um dos admins
    for user in ADMIN_USERS:
        if email == user["email"] and password == user["password"]:
            return {
                "message": f"Administrador {user['name']} criado/autenticado com sucesso!",
                "user": {
                    "id": user["id"],
                    "name": user["name"],
                    "email": user["email"],
                    "is_admin": user["is_admin"],
                    "role": user["role"],
                    "created_at": "2024-01-01T00:00:00Z"
                }
            }
    
    # Não permite criar outros usuários
    raise HTTPException(
        status_code=403,
        detail="Apenas os administradores previamente cadastrados podem acessar."
    )

@router.get("/admin-users")
async def get_admin_users():
    """Retorna lista dos administradores (sem senhas)"""
    safe_users = []
    for user in ADMIN_USERS:
        safe_user = user.copy()
        safe_user.pop("password", None)  # Remove a senha
        safe_users.append(safe_user)
    
    return {"admins": safe_users}
