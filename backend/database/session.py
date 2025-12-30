# backend/database/session.py - VERSÃO CORRIGIDA
import os
import logging
from pathlib import Path
from typing import Generator, Optional
from contextlib import contextmanager
from dotenv import load_dotenv

from sqlalchemy import create_engine, text, event, pool
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.orm import sessionmaker, declarative_base, Session, scoped_session
from sqlalchemy.pool import QueuePool

# Configurar logging para PostgreSQL
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carrega o .env da raiz do projeto
BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=BASE_DIR / ".env", override=True)

# ============================================
# CONFIGURAÇÃO DO BANCO MAWDSLEYS
# ============================================

# Use DATABASE_URL ou construa a partir de variáveis individuais
DATABASE_URL = os.getenv("DATABASE_URL")

# Variáveis individuais (definir independentemente)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "mawdsleys")
DB_USER = os.getenv("DB_USER", "mawdsleys_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

if not DATABASE_URL:
    # Construir URL a partir de variáveis individuais
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# LOG APENAS DEPOIS DE DEFINIR AS VARIÁVEIS
logger.info(f"🔗 Conectando ao PostgreSQL: {DB_HOST}:{DB_PORT}/{DB_NAME}")

# ============================================
# ENGINE OTIMIZADO PARA POSTGRESQL PRODUCTION
# ============================================

def create_postgres_engine(database_url: str, echo: bool = False):
    """Cria engine otimizado para PostgreSQL"""
    
    # Configurações específicas para PostgreSQL
    engine_params = {
        "poolclass": QueuePool,
        "pool_size": 20,
        "max_overflow": 10,
        "pool_pre_ping": True,
        "pool_recycle": 3600,
        "pool_timeout": 30,
        "echo": echo,
        "echo_pool": echo,
        "future": True,
    }
    
    # Parâmetros de conexão específicos do PostgreSQL
    connect_args = {
        "connect_timeout": 10,
        "application_name": "mawdsleys_backend",
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    }
    
    # Criar engine
    engine = create_engine(
        database_url,
        **engine_params,
        connect_args=connect_args
    )
    
    # Event listeners para otimização
    @event.listens_for(engine, "connect")
    def connect(dbapi_connection, connection_record):
        """Configurações na conexão"""
        cursor = dbapi_connection.cursor()
        
        # Otimizações para PostgreSQL
        cursor.execute("SET TIME ZONE 'America/Sao_Paulo'")
        cursor.execute("SET client_encoding TO 'UTF8'")
        cursor.execute("SET statement_timeout = 30000")
        
        cursor.close()
        logger.debug("🔧 Conexão PostgreSQL configurada")
    
    return engine

# Criar engine
engine = create_postgres_engine(
    DATABASE_URL, 
    echo=os.getenv("SQL_ECHO", "False").lower() == "true"
)

# ============================================
# SESSION FACTORY
# ============================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
    class_=Session,
    info=None
)

Base = declarative_base()

# ============================================
# DEPENDENCY INJECTION E CONTEXT MANAGERS
# ============================================

def get_db() -> Generator[Session, None, None]:
    """
    Dependency injection para FastAPI/contextos assíncronos
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ Erro de banco de dados: {e}", exc_info=True)
        raise
    finally:
        db.close()

@contextmanager
def db_session(commit: bool = True) -> Generator[Session, None, None]:
    """
    Context manager para sessões de banco
    """
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

# ============================================
# FUNÇÕES DE TESTE E UTILITÁRIAS (SIMPLIFICADAS)
# ============================================

def test_postgres_connection() -> dict:
    """Testa conexão e retorna informações do PostgreSQL"""
    try:
        with engine.connect() as conn:
            # Informações do servidor
            version_result = conn.execute(text("SELECT version()"))
            version = version_result.scalar()
            
            # Informações do banco
            db_info = conn.execute(text("""
                SELECT 
                    current_database() as database,
                    current_user as user,
                    inet_server_addr() as server_address,
                    inet_server_port() as server_port
            """)).first()
            
            return {
                "status": "connected",
                "database": db_info.database,
                "user": db_info.user,
                "server": f"{db_info.server_address}:{db_info.server_port}",
                "version": version.split(',')[0].split('on')[0].strip(),
            }
            
    except OperationalError as e:
        logger.error(f"❌ Falha na conexão PostgreSQL: {e}")
        return {
            "status": "error",
            "message": str(e),
        }

def create_tables():
    """Cria todas as tabelas definidas nos models"""
    try:
        Base.metadata.create_all(bind=engine)
        
        # Verificar tabelas criadas
        with engine.connect() as conn:
            tables = conn.execute(text("""
                SELECT table_name 
                from  information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)).fetchall()
        
        table_list = [table[0] for table in tables]
        logger.info(f"✅ {len(table_list)} tabelas no banco: {', '.join(table_list[:5])}{'...' if len(table_list) > 5 else ''}")
        
        return True, table_list
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabelas: {e}")
        return False, []

def initialize_database():
    """Inicializa o banco com configurações básicas"""
    logger.info("🚀 Inicializando banco de dados PostgreSQL...")
    
    # Testar conexão
    connection_info = test_postgres_connection()
    if connection_info.get("status") != "connected":
        raise RuntimeError(f"Falha na conexão: {connection_info}")
    
    # Criar tabelas
    success, tables = create_tables()
    if not success:
        raise RuntimeError("Falha ao criar tabelas")
    
    logger.info("✅ Banco de dados inicializado com sucesso!")
    return {
        "connection": connection_info,
        "tables": tables,
    }

# ============================================
# EXPORTS
# ============================================

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

# Teste automático ao importar (apenas em desenvolvimento)
if __name__ == "__main__":
    print("🔧 Testando conexão com PostgreSQL...")
    info = test_postgres_connection()
    print(f"Status: {info.get('status', 'unknown')}")