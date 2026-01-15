# fix_user_duplicate.py
import os
import sys
from pathlib import Path

def fix_models():
    """Corrige a duplicação da classe User"""
    print("🔧 CORRIGINDUPLICAÇÃO DA CLASSE USER")
    print("="*50)
    
    # 1. Corrigir backend/database/models.py
    old_models_path = Path("backend/database/models.py")
    
    if old_models_path.exists():
        with open(old_models_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remover APENAS a classe User
        lines = content.split('\n')
        new_lines = []
        in_user_class = False
        indent_level = 0
        
        for line in lines:
            if line.strip().startswith('class User(Base):'):
                print("✅ Encontrada classe User duplicada - removendo...")
                in_user_class = True
                indent_level = len(line) - len(line.lstrip())
                continue
            
            if in_user_class:
                current_indent = len(line) - len(line.lstrip()) if line.strip() else 0
                if current_indent <= indent_level and line.strip() and not line.startswith(' ' * (indent_level + 1)):
                    in_user_class = False
                    new_lines.append(line)  # Adiciona a próxima classe
                # Não adiciona linhas da classe User
                continue
            
            new_lines.append(line)
        
        # Salvar arquivo corrigido
        with open(old_models_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print("✅ backend/database/models.py corrigido (classe User removida)")
    else:
        print("ℹ️  backend/database/models.py não encontrado")
    
    # 2. Atualizar backend/models/user.py com relacionamentos
    user_model_path = Path("backend/models/user.py")
    
    if user_model_path.exists():
        with open(user_model_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se já tem os relacionamentos antigos
        if 'followups = relationship' not in content:
            # Encontrar onde adicionar os relacionamentos
            lines = content.split('\n')
            new_lines = []
            
            for i, line in enumerate(lines):
                new_lines.append(line)
                
                # Adicionar após os campos de coluna
                if 'created_at = Column(DateTime(timezone=True)' in line:
                    # Adicionar relacionamentos com tabelas antigas
                    new_lines.append('')
                    new_lines.append('    # 🔄 RELACIONAMENTOS COM TABELAS ANTIGAS (frontend existe)')
                    new_lines.append('    followups = relationship(')
                    new_lines.append('        "FollowUp", ')
                    new_lines.append('        back_populates="user",')
                    new_lines.append('        cascade="all, delete-orphan",')
                    new_lines.append('        lazy="dynamic"')
                    new_lines.append('    )')
                    new_lines.append('    ')
                    new_lines.append('    kpis = relationship(')
                    new_lines.append('        "KPI", ')
                    new_lines.append('        back_populates="user",')
                    new_lines.append('        cascade="all, delete-orphan",')
                    new_lines.append('        lazy="dynamic"')
                    new_lines.append('    )')
                    new_lines.append('    ')
                    new_lines.append('    meetings = relationship(')
                    new_lines.append('        "Meeting", ')
                    new_lines.append('        back_populates="user",')
                    new_lines.append('        cascade="all, delete-orphan",')
                    new_lines.append('        lazy="dynamic"')
                    new_lines.append('    )')
                    new_lines.append('    ')
            
            # Salvar
            with open(user_model_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            
            print("✅ backend/models/user.py atualizado com relacionamentos antigos")
        else:
            print("ℹ️  backend/models/user.py já tem os relacionamentos")
    
    # 3. Limpar cache
    print("\n🧹 LIMPANDO CACHE...")
    for root, dirs, files in os.walk("."):
        if "__pycache__" in root:
            import shutil
            shutil.rmtree(root)
        for file in files:
            if file.endswith(".pyc"):
                os.remove(os.path.join(root, file))
    
    print("✅ Cache limpo")
    
    return True

def verify_fix():
    """Verifica se a correção funcionou"""
    print("\n" + "="*50)
    print("🧪 VERIFICANDO CORREÇÃO")
    print("="*50)
    
    sys.path.insert(0, "backend")
    
    try:
        # Testar import do User
        from models.user import User
        print("✅ User importado de backend/models/user.py")
        print(f"   Tabela: {User.__tablename__}")
        
        # Verificar relacionamentos
        rel_names = [rel.key for rel in User.__mapper__.relationships]
        print(f"   Relacionamentos: {len(rel_names)}")
        
        # Verificar se tem os relacionamentos antigos
        old_rels = ['followups', 'kpis', 'meetings']
        for rel in old_rels:
            if rel in rel_names:
                print(f"   ✅ {rel}")
            else:
                print(f"   ❌ {rel} (faltando)")
        
        # Testar import dos modelos antigos
        try:
            from database.models import FollowUp, KPI, Meeting
            print(f"\n✅ Modelos antigos importados:")
            print(f"   • FollowUp: {FollowUp.__tablename__ if FollowUp else 'N/A'}")
            print(f"   • KPI: {KPI.__tablename__ if KPI else 'N/A'}")
            print(f"   • Meeting: {Meeting.__tablename__ if Meeting else 'N/A'}")
        except ImportError as e:
            print(f"\n⚠️  Modelos antigos não importados: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False

def check_database():
    """Verifica tabelas no banco"""
    print("\n" + "="*50)
    print("🔍 VERIFICANDO BANCO DE DADOS")
    print("="*50)
    
    try:
        from database.session import engine
        from sqlalchemy import inspect
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"📊 Total de tabelas: {len(tables)}")
        
        # Categorizar
        categories = {
            "👤 Usuários/Auth": ['users', 'roles', 'user_roles', 'sessions'],
            "📱 WhatsApp": ['wa_conversations', 'wa_messages'],
            "📝 Sistema Antigo": ['followups', 'kpis', 'meetings'],
            "⚙️  Outras": ['activity_logs', 'settings', 'posts', 'comments']
        }
        
        for category, table_list in categories.items():
            print(f"\n{category}:")
            for table in table_list:
                if table in tables:
                    print(f"   ✅ {table}")
                else:
                    print(f"   ❌ {table}")
        
        return tables
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")
        return []

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔄 CORREÇÃO: DUPLICAÇÃO DA CLASSE USER")
    print("="*60)
    
    # Aplicar correção
    if fix_models():
        # Verificar
        if verify_fix():
            # Verificar banco
            tables = check_database()
            
            print("\n" + "="*60)
            print("🎉 CORREÇÃO APLICADA COM SUCESSO!")
            print(f"📊 {len(tables)} tabelas no banco")
            print("="*60)