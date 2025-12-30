# backend/create_admin.py (VERSÃO CORRIGIDA)

#!/usr/bin/env python
"""
Script para criar usuário admin - ESTRUTURA CORRIGIDA
"""

import sys
import os
from  pathlib import Path
from  datetime import datetime

# Adicionar diretório atual ao path (importante!)
sys.path.insert(0, str(Path(__file__).parent))

print("🔍 Importando módulos...")

try:
    # Importar do seu projeto REAL
    from  database.session import SessionLocal, engine
    from  database.base_class import Base
    from  models.user import User
    from  models.role import Role
    from  security.password import get_password_hash
    
    print("✅ Módulos importados com sucesso!")
    
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    print("\n📋 Tentando importações alternativas...")
    
    # Tentar importações alternativas
    try:
        # Verificar se security/password.py existe
        from  security import password
        get_password_hash = password.get_password_hash
        print("✅ security.password importado")
    except:
        print("⚠️  security.password não encontrado, usando bcrypt direto")
        import bcrypt
        def get_password_hash(pwd):
            salt = bcrypt.gensalt()
            return bcrypt.hashpw(pwd.encode(), salt).decode()
    
    try:
        from  database.session import SessionLocal, engine
        print("✅ database.session importado")
    except ImportError as e:
        print(f"❌ Erro database.session: {e}")
        sys.exit(1)
    
    # Verificar modelos
    try:
        from  models.user import User
        from  models.role import Role
        print("✅ models.user e models.role importados")
    except ImportError as e:
        print(f"⚠️  Modelos não encontrados: {e}")
        User = Role = None

def create_tables_if_needed():
    """Cria tabelas se não existirem"""
    print("\n🗄️  Verificando tabelas...")
    try:
        # Importar todos os modelos para que SQLAlchemy os reconheça
        from  models import user, role, activity_log, session, setting
        from  models import wa_conversation, wa_message
        
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas verificadas/criadas com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False

def setup_admin():
    """Configura usuário administrador"""
    db = SessionLocal()
    
    try:
        print("\n👤 Configurando sistema...")
        
        # 1. Criar roles padrão
        default_roles = [
            {"name": "admin", "description": "Administrador do sistema"},
            {"name": "user", "description": "Usuário comum"},
            {"name": "manager", "description": "Gerente"},
            {"name": "viewer", "description": "Apenas visualização"},
            {"name": "editor", "description": "Editor de conteúdo"}
        ]
        
        for role_data in default_roles:
            # Verificar se role já existe
            role = db.query(Role).filter(Role.name == role_data["name"]).first()
            if not role:
                role = Role(**role_data)
                db.add(role)
                print(f"   ✅ Role '{role_data['name']}' criada")
            else:
                print(f"   ⏭️  Role '{role_data['name']}' já existe")
        
        db.commit()
        
        # 2. Criar usuário admin
        print("\n👑 Criando usuário administrador...")
        
        # 🚨 ALTERE ESTES VALORES COM SEUS DADOS REAIS! 🚨
        ADMIN_EMAIL = "nelsonronnyr40@gmail.com"    # SEU EMAIL
        ADMIN_NAME = "Nelson Vieira"            # SEU NOME
        ADMIN_PASSWORD = "Admin@2024"           # SENHA FORTE
        
        # Perguntar dados interativamente
        use_default = input(f"Usar configuração padrão? (Email: {ADMIN_EMAIL}) (s/n): ")
        
        if use_default.lower() != 's':
            ADMIN_EMAIL = input("Email do administrador: ")
            ADMIN_NAME = input("Nome do administrador: ")
            ADMIN_PASSWORD = input("Senha: ")
        
        # Verificar se usuário já existe
        admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()
        
        if admin:
            print(f"\n⚠️  Usuário '{ADMIN_EMAIL}' já existe!")
            print(f"   ID: {admin.id}")
            print(f"   Nome: {admin.name}")
            print(f"   Ativo: {admin.is_active}")
            
            update = input("Deseja redefinir a senha? (s/n): ")
            if update.lower() == 's':
                new_pass = input("Nova senha: ") or ADMIN_PASSWORD
                admin.password_hash = get_password_hash(new_pass)
                admin.is_active = True
                db.commit()
                print("✅ Senha atualizada!")
        else:
            # Criar novo usuário admin
            admin = User(
                email=ADMIN_EMAIL,
                name=ADMIN_NAME,
                password_hash=get_password_hash(ADMIN_PASSWORD),
                is_active=True
            )
            db.add(admin)
            db.commit()
            print(f"✅ Usuário '{ADMIN_EMAIL}' criado")
        
        # 3. Adicionar role admin
        admin_role = db.query(Role).filter(Role.name == 'admin').first()
        if admin_role:
            # Verificar relação many-to-many
            if hasattr(admin, 'roles'):
                # Verificar se já tem a role
                db.refresh(admin)
                if admin_role not in admin.roles:
                    admin.roles.append(admin_role)
                    db.commit()
                    print("✅ Role 'admin' atribuída")
                else:
                    print("⏭️  Usuário já tem role 'admin'")
            else:
                # Se não houver relação many-to-many, usar campo direto
                if hasattr(admin, 'role_id'):
                    admin.role_id = admin_role.id
                    db.commit()
                    print("✅ Role 'admin' atribuída (campo direto)")
                else:
                    print("⚠️  Não foi possível atribuir role (estrutura não suportada)")
        
        # 4. Mostrar resumo
        print("\n" + "=" * 60)
        print("🎉 CONFIGURAÇÃO COMPLETADA!")
        print("=" * 60)
        print("👤 USUÁRIO ADMINISTRADOR:")
        print(f"   📧 Email: {ADMIN_EMAIL}")
        print(f"   👤 Nome: {ADMIN_NAME}")
        print(f"   🔑 Senha: {ADMIN_PASSWORD}")
        print("\n📊 BANCO DE DADOS:")
        print(f"   Conector: PostgreSQL")
        print(f"   Tabelas: Users, Roles, etc.")
        print("\n⚠️  RECOMENDAÇÕES:")
        print("   1. Altere esta senha no primeiro login!")
        print("   2. Verifique security/jwt.py para SECRET_KEY")
        print("   3. Use variáveis de ambiente (.env) em produção")
        print("=" * 60)
        
        # 5. Criar usuários de teste?
        create_test = input("\n🧪 Criar usuários de teste? (s/n): ")
        if create_test.lower() == 's':
            create_test_users(db)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()

def create_test_users(db):
    """Cria usuários de teste"""
    from  models.user import User
    from  models.role import Role
    
    test_users = [
        {"email": "gerente@mawdsleys.com", "name": "Gerente Teste", "password": "Gerente123!", "role": "manager"},
        {"email": "usuario@mawdsleys.com", "name": "Usuário Teste", "password": "Usuario123!", "role": "user"},
        {"email": "suporte@mawdsleys.com", "name": "Suporte Teste", "password": "Suporte123!", "role": "editor"}
    ]
    
    created = 0
    for user_data in test_users:
        # Verificar se já existe
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing:
            user = User(
                email=user_data["email"],
                name=user_data["name"],
                password_hash=get_password_hash(user_data["password"]),
                is_active=True
            )
            db.add(user)
            db.commit()
            
            # Adicionar role
            role = db.query(Role).filter(Role.name == user_data["role"]).first()
            if role and hasattr(user, 'roles'):
                user.roles.append(role)
                db.commit()
            
            print(f"   ✅ {user_data['email']} ({user_data['role']})")
            created += 1
        else:
            print(f"   ⏭️  {user_data['email']} já existe")
    
    if created > 0:
        print(f"\n🧪 {created} usuários de teste criados!")
    else:
        print("\n⏭️  Todos os usuários de teste já existem")

def test_database():
    """Testa conexão com banco"""
    print("\n🔗 Testando conexão com banco de dados...")
    db = SessionLocal()
    try:
        result = db.execute("SELECT version()")
        db_version = result.fetchone()[0]
        print(f"✅ PostgreSQL conectado: {db_version.split(',')[0]}")
        
        # Verificar tabelas
        result = db.execute("""
            SELECT table_name 
            from  information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = [row[0] for row in result.fetchall()]
        print(f"📊 Tabelas existentes: {len(tables)}")
        if tables:
            print(f"   {', '.join(tables[:5])}{'...' if len(tables) > 5 else ''}")
        
        return True
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False
    finally:
        db.close()

def check_security_config():
    """Verifica configurações de segurança"""
    print("\n🔐 Verificando configurações de segurança...")
    
    try:
        from  security.jwt import SECRET_KEY, ALGORITHM
        
        if SECRET_KEY == "YOUR_SUPER_SECRET_KEY_CHANGE_IN_PRODUCTION":
            print("⚠️  AVISO: SECRET_KEY está com valor padrão!")
            print("   Altere em: security/jwt.py")
        else:
            print(f"✅ SECRET_KEY configurada (primeiros chars: {SECRET_KEY[:10]}...)")
        
        print(f"✅ Algoritmo: {ALGORITHM}")
        
    except ImportError:
        print("⚠️  Módulo security.jwt não encontrado")
    
    try:
        from  security.password import get_password_hash, verify_password
        print("✅ Módulo de senhas encontrado")
    except ImportError:
        print("⚠️  Módulo security.password não encontrado")

def main():
    """Função principal"""
    print("=" * 60)
    print("🚀 MAWDSLEYS - Configuração do Sistema")
    print("=" * 60)
    
    # Verificar segurança
    check_security_config()
    
    # Testar banco
    if not test_database():
        print("\n❌ Não foi possível conectar ao banco.")
        print("   Execute: python test_postgres_connection.py")
        return
    
    # Criar tabelas
    if not create_tables_if_needed():
        print("\n❌ Erro ao criar tabelas.")
        return
    
    # Configurar admin
    setup_admin()
    
    print("\n" + "=" * 60)
    print("✅ CONFIGURAÇÃO FINALIZADA!")
    print("=" * 60)
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Inicie o servidor:")
    print("   python main.py")
    print("\n2. Acesse a documentação:")
    print("   http://localhost:8000/docs")
    print("\n3. Faça login com:")
    print("   Email: [o que você configurou]")
    print("   Senha: [a senha que você definiu]")
    print("\n4. Altere a senha no primeiro acesso!")
    print("=" * 60)

if __name__ == "__main__":
    main()