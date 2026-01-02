# backend/database/session.py
import os
import logging
from typing import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, text, event
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.pool import QueuePool

# ======================================================
# LOGGING
# ======================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("database")

# ======================================================
# DATABASE URL (Fly FIRST, .env ONLY LOCAL)
# ======================================================

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # 🚨 LOCAL DEVELOPMENT ONLY
    from dotenv import load_dotenv
    from pathlib import Path

    BASE_DIR = Path(__file__).resolve().parents[2]
    load_dotenv(BASE_DIR / ".env")

    DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("❌ DATABASE_URL não definido")

# Normalizar dialect (Fly às vezes injeta postgres://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)

logger.info("🔗 Conectando ao PostgreSQL via DATABASE_URL")

# ======================================================
# ENGINE
# ======================================================

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=5,
    pool_pre_ping=True,
    pool_recycle=1800,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
)

# Ajustes de sessão PostgreSQL
@event.listens_for(engine, "connect")
def on_connect(dbapi_connection, _):
    cursor = dbapi_connection.cursor()
    cursor.execute("SET TIME ZONE 'America/Sao_Paulo'")
    cursor.execute("SET client_encoding TO 'UTF8'")
    cursor.close()

# ======================================================
# SESSION / BASE
# ======================================================

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=Session,
)

Base = declarative_base()

# ======================================================
# DEPENDENCY (FASTAPI)
# ======================================================

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("❌ Erro de banco", exc_info=e)
        raise
    finally:
        db.close()

@contextmanager
def db_session(commit: bool = True):
    session = SessionLocal()
    try:
        yield session
        if commit:
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# ======================================================
# UTILIDADES
# ======================================================

def test_postgres_connection() -> dict:
    try:
        with engine.connect() as conn:
            version = conn.execute(text("SELECT version()")).scalar()
            db = conn.execute(text("SELECT current_database()")).scalar()

            return {
                "status": "connected",
                "database": db,
                "version": version.split(",")[0],
            }
    except OperationalError as e:
        logger.error("❌ Falha na conexão PostgreSQL", exc_info=e)
        return {"status": "error", "message": str(e)}

def create_tables():
    Base.metadata.create_all(bind=engine)

def initialize_database():
    logger.info("🚀 Inicializando banco de dados...")
    info = test_postgres_connection()
    if info["status"] != "connected":
        raise RuntimeError(info)
    create_tables()
    logger.info("✅ Banco pronto")

# ======================================================
# EXPORTS
# ======================================================

__all__ = [
    "engine",
    "SessionLocal",
    "Base",
    "get_db",
    "db_session",
    "test_postgres_connection",
    "create_tables",
    "initialize_database",
]
