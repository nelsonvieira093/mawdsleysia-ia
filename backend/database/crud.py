# backend/database/crud.py
from datetime import datetime

# Import somente o que precisamos; se outros models existirem, adicione-os em backend/models/
try:
    from backend.models.user import User
except ImportError:
    User = None

# IMPORTS opcionais — se seus outros modelos existirem, mova-os para backend/models/ e descomente
# try:
#     from backend.models.followup import FollowUp
#     from backend.models.kpi import KPI
#     from backend.models.meeting import Meeting
# except ImportError:
#     FollowUp = None
#     KPI = None
#     Meeting = None

# -------- USERS --------
def get_user_by_email(db, email: str):
    if User is None:
        return None
    return db.query(User).filter(User.email == email).first()

def create_user(db, name: str, email: str, hashed_password: str):
    if User is None:
        raise RuntimeError("Model User não encontrado. Verifique backend/models/user.py")
    user = User(name=name, email=email, hashed_password=hashed_password, created_at=datetime.utcnow())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# -------- FOLLOWUPS --------
def list_followups(db, limit: int = 100):
    # Implementar quando FollowUp estiver disponível
    return []

def create_followup(db, user_id: int, title: str, message: str):
    raise NotImplementedError("FollowUp model não encontrado")

# -------- KPIs --------
def list_kpis(db, limit: int = 100):
    return []

def create_kpi(db, user_id: int, title: str, description: str = "", progress: int = 0, deadline=None):
    raise NotImplementedError("KPI model não encontrado")

# -------- MEETINGS --------
def list_meetings(db, limit: int = 100):
    return []

def create_meeting(db, user_id: int, topic: str, scheduled_for, notes: str = ""):
    raise NotImplementedError("Meeting model não encontrado")
