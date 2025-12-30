# backend/services/auth_service.py - VERSÃO COMPLETA
from  sqlalchemy.orm import Session
from  models.user import User
from  security.password import hash_password, verify_password
from  security.jwt import create_access_token

def register_user(db: Session, name: str, email: str, password: str):
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise ValueError("Email já cadastrado")

    user = User(
        name=name,
        email=email,
        password=hash_password(password),
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return None

    if not verify_password(password, user.password):
        return None

    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )

    return {
        "access_token": access_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
        },
    }