import sys
import os
from pathlib import Path

# Configura paths
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

print("🚀 INICIANDO BACKEND MAWDSLEYS")
print("=" * 50)
print(f"📂 Diretório: {BASE_DIR}")
print(f"🐍 Python: {sys.executable}")
print(f"📦 Path: {sys.path[0]}")

# Carrega .env
env_file = BASE_DIR / ".env"
if env_file.exists():
    print(f"✅ .env encontrado: {env_file}")
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=env_file)
else:
    print(f"❌ .env não encontrado")
    print("💡 Crie um arquivo .env na raiz com:")
    print('''
DATABASE_URL=postgresql://postgres:sua_senha@localhost:5432/mawdsleys_db
SECRET_KEY=sua-chave-secreta
    ''')

# Importa e inicia o FastAPI
try:
    print("\n📦 Importando módulos...")
    from backend.main import app
    import uvicorn
    
    print("✅ Módulos importados com sucesso!")
    print("\n🌐 Servidor disponível em:")
    print("   http://localhost:8000")
    print("   http://localhost:8000/docs")
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
    
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("\n💡 Soluções:")
    print("1. Execute de: E:\\MAWDSLEYS-AGENTE\\")
    print("2. Verifique se existe backend/__init__.py")
    print("3. Instale dependências: pip install -r requirements.txt")
except Exception as e:
    print(f"❌ Erro: {e}")