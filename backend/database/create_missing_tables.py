# backend/database/create_missing_tables.py
from database.session import engine
from sqlalchemy import text

def create_missing_tables():
    """Cria as tabelas faltantes do MAWDSLEYS"""
    
    print("🔧 CRIANDO TABELAS FALTANTES DO MAWDSLEYS")
    print("=" * 50)
    
    with engine.connect() as conn:
        # 1. Tabela memory_entries (Memory Engine)
        print("📝 Criando tabela memory_entries...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS memory_entries (
                id VARCHAR(50) PRIMARY KEY,
                user_id VARCHAR(50) NOT NULL,
                entity_type VARCHAR(100) NOT NULL,
                entity_id VARCHAR(100) NOT NULL,
                content TEXT NOT NULL,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Índices para memory_entries
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_memory_user ON memory_entries(user_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_memory_entity ON memory_entries(entity_type, entity_id)"))
        print("✅ Tabela memory_entries criada")
        
        # 2. Tabela alerts (Alert Engine)
        print("📝 Criando tabela alerts...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS alerts (
                id VARCHAR(50) PRIMARY KEY,
                type VARCHAR(100) NOT NULL,
                severity VARCHAR(50) NOT NULL,
                title VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                entity VARCHAR(100) NOT NULL,
                entity_id VARCHAR(100) NOT NULL,
                actor VARCHAR(100),
                metadata JSONB,
                read BOOLEAN DEFAULT FALSE,
                resolved BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP
            )
        """))
        
        # Índices para alerts
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_alerts_entity ON alerts(entity, entity_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_alerts_created ON alerts(created_at DESC)"))
        print("✅ Tabela alerts criada")
        
        # 3. Adiciona coluna type à activity_logs (opcional)
        print("📝 Verificando colunas de activity_logs...")
        conn.execute(text("""
            DO $$ 
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name='activity_logs' AND column_name='type') THEN
                    ALTER TABLE activity_logs ADD COLUMN type VARCHAR(100);
                    UPDATE activity_logs SET type = action;
                    RAISE NOTICE 'Coluna type adicionada à activity_logs';
                ELSE
                    RAISE NOTICE 'Coluna type já existe em activity_logs';
                END IF;
            END $$;
        """))
        
        conn.commit()
    
    print("=" * 50)
    print("🎯 TODAS AS TABELAS DO MAWDSLEYS ESTÃO PRONTAS!")
    print("=" * 50)

if __name__ == "__main__":
    create_missing_tables()