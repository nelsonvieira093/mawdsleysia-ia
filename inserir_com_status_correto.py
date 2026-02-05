#!/usr/bin/env python3
import os
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta

os.environ['DATABASE_URL'] = 'postgresql+psycopg2://postgres:Agente0934@localhost:5432/mawdsleys'

engine = create_engine(os.environ['DATABASE_URL'])

with engine.connect() as conn:
    print("=== INSERINDO COM STATUS CORRETOS ===")
    
    # Primeiro, descobre os valores do ENUM
    result = conn.execute(text("SELECT unnest(enum_range(NULL::followup_status))"))
    enum_values = [row[0] for row in result]
    print(f"Valores ENUM encontrados: {enum_values}")
    
    # Usa valores que provavelmente existem
    if 'pending' in enum_values:
        status_pendente = 'pending'
    elif 'open' in enum_values:
        status_pendente = 'open'
    else:
        status_pendente = enum_values[0] if enum_values else 'pending'
    
    if 'in_progress' in enum_values:
        status_andamento = 'in_progress'
    elif 'progress' in enum_values:
        status_andamento = 'progress'
    else:
        status_andamento = enum_values[1] if len(enum_values) > 1 else 'in_progress'
    
    if 'completed' in enum_values:
        status_aberto = 'completed'
    elif 'closed' in enum_values:
        status_aberto = 'closed'
    else:
        status_aberto = enum_values[2] if len(enum_values) > 2 else 'completed'
    
    print(f"\nUsando status:")
    print(f"  PENDENTE → {status_pendente}")
    print(f"  EM_ANDAMENTO → {status_andamento}")
    print(f"  ABERTO → {status_aberto}")
    
    # Limpa dados antigos
    try:
        conn.execute(text("DELETE FROM followups WHERE owner_id = 1"))
        conn.commit()
        print("\n1. Dados antigos removidos")
    except:
        conn.rollback()
        print("\n1. Nada para limpar")
    
    # Dados reais com status CORRETOS
    dados = [
        ("Contrato CON-2024-015 TechSolutions - Valor R$ 125.000,00", status_pendente, 3),
        ("Projeto Sistema Gestao Integrada - Apresentacao diretoria", status_andamento, 7),
        ("Sprint 24 desenvolvimento - Entrega 15/02/2024", status_aberto, 2),
        ("Metricas Q4/2024 - Faturamento R$ 2,5M - Crescimento 15%", status_pendente, 5),
        ("Cliente VarejoMaster - Projeto expansao lojas", status_andamento, 10),
        ("Relatorio trimestral conselho - Deadline 20/02/2024", status_aberto, 12),
        ("Orcamento TI 2025 - Valor R$ 850.000,00", status_pendente, 4),
        ("Proposta filial Sao Paulo - Investimento R$ 3,2M", status_andamento, 6),
        ("Auditoria financeiro - Prazo 28/02/2024", status_pendente, 8),
        ("Sistema CRM - Fase 3 Treinamento", status_aberto, 14)
    ]
    
    print("\n2. Inserindo 10 follow-ups...")
    
    for i, (desc, status, dias) in enumerate(dados, 1):
        vencimento = datetime.now() + timedelta(days=dias)
        
        sql = text("""
            INSERT INTO followups (description, status, owner_id, created_at, due_date)
            VALUES (:desc, :status, 1, NOW(), :vencimento)
        """)
        
        conn.execute(sql, {'desc': desc, 'status': status, 'vencimento': vencimento})
        print(f"   {i:2d}. {status:12} {desc[:45]}...")
    
    conn.commit()
    print(f"\n3. {len(dados)} follow-ups inseridos!")
    
    # Verifica
    result = conn.execute(text("SELECT COUNT(*) FROM followups WHERE owner_id = 1"))
    total = result.scalar()
    print(f"\n4. Total no banco: {total} follow-ups")
    
    print("\n=== PRONTO PARA TESTAR ===")
    print('Comando: curl -X POST "http://localhost:8080/api/v1/chat" \\')
    print('  -H "Authorization: Bearer TOKEN" \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"message":"Listar meus follow-ups"}\'')
