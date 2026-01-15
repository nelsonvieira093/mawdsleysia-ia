# backend/reset_postgres.py
import sys
import os
from  pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.session import engine, Base
from security.password import hash_password
from  sqlalchemy import text

def reset_database():
    """Recria banco do zero (PERIGO: apaga todos os dados!)"""
    print("🔥 RESET COMPLETO DO BANCO POSTGRESQL")
    print("=" * 60)
    
    resposta = input("❌ ISSO APAGARÁ TODOS OS DADOS! Continuar? (s/n): ")
    
    if resposta.lower() != 's':
        print("Operação cancelada.")
        return
    
    try:
        # 1. Apaga todas as tabelas
        print("\n🗑️  Apagando tabelas...")
        Base.metadata.drop_all(bind=engine)
        
        # 2. Cria tabelas
        print("🔄 Criando tabelas...")
        Base.metadata.create_all(bind=engine)
        
        # 3. Cria admin
        print("👤 Criando admin...")
        with engine.connect() as conn:
            hashed = hash_password("Admin@123")
            conn.execute(text("""
                INSERT INTO users (name, email, password, is_active, created_at)
                VALUES ('Administrador', 'admin@cliente.com', :pwd, TRUE, NOW())
            """), {"pwd": hashed})
            conn.commit()
        
        print("\n✅ Banco resetado com sucesso!")
        print(f"   Admin: admin@cliente.com / Admin@123")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    reset_database()