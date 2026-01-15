# E:\MAWDSLEYS-AGENTE\test_database.py
import sys
import os
from pathlib import Path

# Adiciona o diretório 'backend' ao path
sys.path.append(str(Path(__file__).parent / "backend"))

try:
    from backend.database.session import (
        test_postgres_connection, 
        initialize_database
    )
except ImportError as e:
    print(f"❌ Erro na importação: {e}")
    sys.exit(1)

def main():
    print("\n" + "="*50)
    print("🧪 TESTE DE CONEXÃO POSTGRESQL")
    print("="*50)
    
    # 1. Testar conexão
    print("\n🔗 Testando conexão...")
    conn_info = test_postgres_connection()
    
    if conn_info.get("status") == "connected":
        print(f"✅ CONECTADO!")
        print(f"   Banco: {conn_info['database']}")
        print(f"   Servidor: {conn_info['server']}")
        print(f"   Usuário: {conn_info['user']}")
        print(f"   Versão: {conn_info['version']}")
    else:
        print(f"❌ FALHA: {conn_info.get('message')}")
        return
    
    # 2. Inicializar banco
    print("\n🚀 Inicializando banco...")
    try:
        result = initialize_database()
        print(f"✅ SUCESSO!")
        print(f"   Tabelas: {len(result['tables'])} criadas")
        for table in result['tables']:
            print(f"   • {table}")
    except Exception as e:
        print(f"⚠️  Atenção: {e}")
        print("(Tabelas podem já existir)")
    
    print("\n" + "="*50)
    print("🎉 BANCO PRONTO PARA USO!")
    print("="*50)

if __name__ == "__main__":
    main()