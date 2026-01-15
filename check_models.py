# check_models.py - VERSÃO COMPLETA PARA SEU BANCO
from backend.database.session import engine, Base
from backend.models import User, Role, Session, ActivityLog, Setting, Post, Comment, WAConversation, WAMessage
from sqlalchemy import inspect

def check_all_tables():
    """Verifica se todas as tabelas existem e estão corretas"""
    inspector = inspect(engine)
    
    print("🔍 VERIFICAÇÃO COMPLETA DO BANCO MAWDSLEYS")
    print("=" * 60)
    
    # Listar todas as tabelas
    tables = inspector.get_table_names()
    print(f"📊 Total de tabelas encontradas: {len(tables)}")
    
    # Tabelas esperadas (baseado no seu banco)
    expected_tables = [
        'users', 'roles', 'user_roles', 'sessions',
        'activity_logs', 'settings', 'posts', 'comments',
        'wa_conversations', 'wa_messages'
    ]
    
    print(f"📋 Tabelas esperadas: {len(expected_tables)}")
    print()
    
    # Verificar cada tabela esperada
    found_all = True
    for table_name in expected_tables:
        if table_name in tables:
            print(f"✅ {table_name.upper():20} - ENCONTRADA")
            columns = inspector.get_columns(table_name)
            print(f"   Colunas: {len(columns)}")
            
            # Mostrar estrutura resumida
            for col in columns[:3]:  # Mostrar apenas 3 primeiras colunas
                pk = " (PK)" if col.get('primary_key') else ""
                nullable = "" if col.get('nullable', True) else " NOT NULL"
                print(f"   • {col['name']}: {col['type']}{pk}{nullable}")
            
            if len(columns) > 3:
                print(f"   ... e mais {len(columns) - 3} colunas")
            
        else:
            print(f"❌ {table_name.upper():20} - NÃO ENCONTRADA!")
            found_all = False
        print()  # Linha em branco entre tabelas
    
    # Verificar tabelas extras (não esperadas)
    extra_tables = [t for t in tables if t not in expected_tables]
    if extra_tables:
        print(f"⚠️  Tabelas extras no banco: {extra_tables}")
    
    print("=" * 60)
    
    # Verificar modelos vs tabelas
    print("\n🧪 VERIFICAÇÃO DOS MODELS SQLALCHEMY")
    print("-" * 40)
    
    models_to_check = [
        ("User", User, "users"),
        ("Role", Role, "roles"),
        ("Session", Session, "sessions"),
        ("ActivityLog", ActivityLog, "activity_logs"),
        ("Setting", Setting, "settings"),
        ("Post", Post, "posts"),
        ("Comment", Comment, "comments"),
        ("WAConversation", WAConversation, "wa_conversations"),
        ("WAMessage", WAMessage, "wa_messages"),
    ]
    
    for model_name, model, table_name in models_to_check:
        try:
            # Verificar se a tabela existe para o modelo
            if table_name in tables:
                # Contar colunas no modelo vs banco
                model_columns = len(model.__table__.columns)
                db_columns = len(inspector.get_columns(table_name))
                
                status = "✅" if model_columns == db_columns else "⚠️"
                match = "CORRESPONDENTE" if model_columns == db_columns else f"DIFERENÇA: modelo={model_columns}, banco={db_columns}"
                
                print(f"{status} {model_name:20} - {match}")
            else:
                print(f"❌ {model_name:20} - TABELA NÃO EXISTE NO BANCO")
        except Exception as e:
            print(f"❌ {model_name:20} - ERRO: {str(e)[:50]}...")
    
    print("\n" + "=" * 60)
    
    if found_all and len(tables) == len(expected_tables):
        print("🎉 TODAS AS TABELAS ESTÃO ALINHADAS COM O BANCO!")
    else:
        print(f"⚠️  Atenção: {len(tables)}/{len(expected_tables)} tabelas encontradas")
    
    # Estatísticas finais
    print("\n📈 ESTATÍSTICAS DO BANCO:")
    print("-" * 30)
    
    total_columns = 0
    for table in tables:
        total_columns += len(inspector.get_columns(table))
    
    print(f"• Tabelas: {len(tables)}")
    print(f"• Colunas totais: {total_columns}")
    print(f"• Tabelas de usuários: {len([t for t in tables if 'user' in t])}")
    print(f"• Tabelas WhatsApp: {len([t for t in tables if 'wa_' in t])}")
    
    return found_all

def check_data_counts():
    """Verifica quantidade de dados em cada tabela"""
    print("\n📊 CONTAGEM DE DADOS NAS TABELAS")
    print("-" * 40)
    
    from sqlalchemy.orm import Session as DBSession
    from sqlalchemy import text
    
    with DBSession(engine) as session:
        tables = inspect(engine).get_table_names()
        
        for table in tables:
            try:
                result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"📋 {table:20} - {count:5} registros")
            except Exception as e:
                print(f"❌ {table:20} - Erro na contagem")

def main():
    """Função principal"""
    print("\n" + "=" * 60)
    print("🔧 VERIFICADOR DE BANCO DE DADOS MAWDSLEYS")
    print("=" * 60)
    
    # 1. Verificar conexão
    try:
        with engine.connect() as conn:
            version = conn.execute(text("SELECT version()")).scalar()
            db_name = conn.execute(text("SELECT current_database()")).scalar()
            print(f"🐘 PostgreSQL: {version.split(',')[0]}")
            print(f"📁 Banco: {db_name}")
    except:
        print("❌ Não foi possível conectar ao banco")
        return
    
    # 2. Verificar tabelas
    print("\n" + "=" * 60)
    all_good = check_all_tables()
    
    # 3. Verificar dados (opcional)
    print("\n" + "=" * 60)
    try:
        check_data_counts()
    except Exception as e:
        print(f"⚠️  Não foi possível verificar dados: {e}")
    
    print("\n" + "=" * 60)
    if all_good:
        print("✅ SISTEMA PRONTO PARA DESENVOLVIMENTO!")
    else:
        print("⚠️  ALGUNS AJUSTES SÃO NECESSÁRIOS")
    print("=" * 60)

if __name__ == "__main__":
    # Adicionar import necessário
    from sqlalchemy import text
    
    # Não criar tabelas automaticamente (elas já existem)
    # Base.metadata.create_all(bind=engine)  # Comente esta linha
    
    # Executar verificação
    main()