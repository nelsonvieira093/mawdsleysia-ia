# verify_fix.py - Crie este arquivo na raiz
import sys
from pathlib import Path

# Adicionar backend ao path
sys.path.append(str(Path(__file__).parent / "backend"))

print("🔍 VERIFICAÇÃO DA CORREÇÃO")
print("="*50)

# 1. Testar import do User
try:
    from models.user import User
    print("✅ 1. User importado de models.user")
    print(f"   Módulo: {User.__module__}")
    print(f"   Tabela: {User.__tablename__}")
except Exception as e:
    print(f"❌ 1. Erro ao importar User: {e}")
    sys.exit(1)

# 2. Verificar relacionamentos
print("\n✅ 2. Relacionamentos do User:")
rels = [rel.key for rel in User.__mapper__.relationships]
for rel in rels:
    print(f"   • {rel}")

# 3. Verificar específicos
required_rels = ['followups', 'kpis', 'meetings', 'roles', 'sessions']
print(f"\n✅ 3. Relacionamentos obrigatórios:")
for rel in required_rels:
    if rel in rels:
        print(f"   ✅ {rel}")
    else:
        print(f"   ❌ {rel} (faltando)")

# 4. Testar import dos modelos antigos
print(f"\n✅ 4. Modelos antigos:")
try:
    from database.models import FollowUp, KPI, Meeting
    print(f"   ✅ FollowUp importado: {FollowUp.__tablename__}")
    print(f"   ✅ KPI importado: {KPI.__tablename__}")
    print(f"   ✅ Meeting importado: {Meeting.__tablename__}")
except Exception as e:
    print(f"   ⚠️  Erro ao importar modelos antigos: {e}")

# 5. Verificar banco
print(f"\n✅ 5. Verificando banco de dados...")
try:
    from database.session import engine
    from sqlalchemy import inspect
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"   📊 {len(tables)} tabelas no banco")
    
    # Verificar tabelas importantes
    important_tables = ['users', 'followups', 'kpis', 'meetings', 'roles']
    for table in important_tables:
        if table in tables:
            print(f"   ✅ {table}")
        else:
            print(f"   ⚠️  {table} (não encontrada)")
            
except Exception as e:
    print(f"   ⚠️  Erro ao verificar banco: {e}")

print("\n" + "="*50)
print("🎉 VERIFICAÇÃO COMPLETA!")
print("="*50)