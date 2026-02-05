#!/usr/bin/env python3
import os
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta

# Banco
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://postgres:Agente0934@localhost:5432/mawdsleys'

engine = create_engine(os.environ['DATABASE_URL'])

with engine.connect() as conn:
    print("=== INSERINDO DADOS REAIS ===")
    
    # Limpa dados antigos SIMPLES
    try:
        conn.execute(text("DELETE FROM followups WHERE owner_id = 1"))
        conn.commit()
        print("1. Dados antigos removidos")
    except:
        print("1. Nada para limpar")
        conn.rollback()
    
    # Dados reais
    dados = [
        ("Contrato CON-2024-015 TechSolutions - Valor R$ 125.000,00", "PENDENTE", 3),
        ("Projeto Sistema Gestao Integrada - Apresentacao diretoria", "EM_ANDAMENTO", 7),
        ("Sprint 24 desenvolvimento - Entrega 15/02/2024", "ABERTO", 2),
        ("Metricas Q4/2024 - Faturamento R$ 2,5M - Crescimento 15%", "PENDENTE", 5),
        ("Cliente VarejoMaster - Projeto expansao lojas", "EM_ANDAMENTO", 10),
        ("Relatorio trimestral conselho - Deadline 20/02/2024", "ABERTO", 12),
        ("Orcamento TI 2025 - Valor R$ 850.000,00", "PENDENTE", 4),
        ("Proposta filial Sao Paulo - Investimento R$ 3,2M", "EM_ANDAMENTO", 6),
        ("Auditoria financeiro - Prazo 28/02/2024", "PENDENTE", 8),
        ("Sistema CRM - Fase 3 Treinamento", "ABERTO", 14)
    ]
    
    print("\n2. Inserindo 10 follow-ups...")
    
    for i, (desc, status, dias) in enumerate(dados, 1):
        vencimento = datetime.now() + timedelta(days=dias)
        
        sql = text("""
            INSERT INTO followups (description, status, owner_id, created_at, due_date)
            VALUES (:desc, :status, 1, NOW(), :vencimento)
        """)
        
        conn.execute(sql, {
            'desc': desc,
            'status': status,
            'vencimento': vencimento
        })
        
        print(f"   {i:2d}. {status:12} {desc[:45]}...")
    
    conn.commit()
    print(f"\n3. {len(dados)} follow-ups inseridos!")
    
    # Verifica
    result = conn.execute(text("SELECT COUNT(*) FROM followups WHERE owner_id = 1"))
    total = result.scalar()
    print(f"\n4. Total no banco: {total} follow-ups")
    
    # Amostra
    print("\n5. Amostra (3 primeiros):")
    result = conn.execute(text("""
        SELECT id, description, status, due_date 
        FROM followups 
        WHERE owner_id = 1 
        ORDER BY due_date 
        LIMIT 3
    """))
    
    for id_num, desc, status, venc in result:
        venc_str = venc.strftime("%d/%m/%Y") if venc else "Sem data"
        print(f"\n   ID {id_num}: {status}")
        print(f"      {desc}")
        print(f"      Vence: {venc_str}")
    
    print("\n=== PRONTO PARA TESTAR ===")
    print('Comando: curl -X POST "http://localhost:8080/api/v1/chat" \\')
    print('  -H "Authorization: Bearer TOKEN" \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"message":"Listar meus follow-ups"}\'')
