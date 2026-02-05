import os
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://postgres:Agente0934@localhost:5432/mawdsleys'
from sqlalchemy import create_engine, text

engine = create_engine(os.environ['DATABASE_URL'])
conn = engine.connect()

try:
    conn.execute(text('ROLLBACK'))
    
    # Colunas
    cols = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='followups'")).fetchall()
    print('COLUNAS DA TABELA followups:')
    for c in cols:
        print(f'  {c[0]}')
    
    # Contagem
    count = conn.execute(text('SELECT COUNT(*) FROM followups')).fetchone()[0]
    print(f'\nTOTAL REGISTROS: {count}')
    
    # Primeiros registros
    if count > 0:
        rows = conn.execute(text('SELECT id, description, status, priority FROM followups LIMIT 3')).fetchall()
        print('\nPRIMEIROS 3 REGISTROS:')
        for r in rows:
            print(f'  ID:{r[0]} - {r[1][:40]}... - Status:{r[2]}')
            
except Exception as e:
    print(f'ERRO: {e}')
finally:
    conn.close()
