import os
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://postgres:Agente0934@localhost:5432/mawdsleys'

from sqlalchemy import create_engine, text

engine = create_engine(os.environ['DATABASE_URL'])

with engine.connect() as conn:
    # 1. Verifica se a tabela existe
    try:
        count = conn.execute(text('SELECT COUNT(*) FROM followups WHERE user_id = 1')).scalar()
        
        if count == 0:
            print('Inserindo 5 follow-ups de teste para user_id=1...')
            
            # Insere dados de teste
            insert_sql = """
            INSERT INTO followups (description, status, priority, user_id, created_at, due_date) 
            VALUES 
                ('Revisar contrato anual com Cliente XYZ Corporation', 'PENDENTE', 'ALTA', 1, NOW(), NOW() + INTERVAL '7 days'),
                ('Preparar apresentacao para reuniao de diretoria trimestral', 'EM_ANDAMENTO', 'MEDIA', 1, NOW(), NOW() + INTERVAL '3 days'),
                ('Enviar relatorio mensal de desempenho para o conselho', 'ABERTO', 'BAIXA', 1, NOW(), NOW() + INTERVAL '10 days'),
                ('Follow-up com equipe de desenvolvimento sobre novo sistema', 'PENDENTE', 'ALTA', 1, NOW(), NOW() + INTERVAL '2 days'),
                ('Analisar metricas do ultimo trimestre e preparar dashboard', 'EM_ANDAMENTO', 'MEDIA', 1, NOW(), NOW() + INTERVAL '5 days')
            """
            conn.execute(text(insert_sql))
            conn.commit()
            print('5 follow-ups inseridos com sucesso!')
        else:
            print(f'Ja existem {count} follow-ups para user_id=1')
        
        # 2. Mostra todos os follow-ups
        print('\nTODOS OS FOLLOW-UPS NO BANCO:')
        results = conn.execute(text('''
            SELECT id, description, status, priority, user_id, created_at, due_date 
            FROM followups 
            ORDER BY created_at DESC
        ''')).fetchall()
        
        for row in results:
            print(f'ID: {row[0]}')
            print(f'   Descricao: {row[1][:60]}...')
            print(f'   Status: {row[2]} | Prioridade: {row[3]} | User: {row[4]}')
            if row[6]:
                print(f'   Vence: {row[6].strftime("%d/%m/%Y")}')
            print()
            
    except Exception as e:
        print(f'ERRO: {e}')
        print('Tentando criar a tabela...')
        
        # Tenta verificar se a tabela existe
        tables = conn.execute(text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema='public' 
            AND table_name LIKE '%follow%'
        """)).fetchall()
        
        print(f'Tabelas encontradas: {tables}')
