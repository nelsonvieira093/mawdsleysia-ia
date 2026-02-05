#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from sqlalchemy import create_engine, text

# Configuração do banco
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://postgres:Agente0934@localhost:5432/mawdsleys'

def main():
    """Insere dados reais de follow-ups"""
    try:
        engine = create_engine(os.environ['DATABASE_URL'])
        
        with engine.connect() as conn:
            print("=" * 60)
            print("INSERCAO DE DADOS REAIS DE FOLLOW-UPS")
            print("=" * 60)
            
            # Limpa dados antigos do owner_id=1
            print("\n1. Limpando dados antigos do owner_id=1...")
            conn.execute(text('DELETE FROM followups WHERE owner_id = 1'))
            conn.commit()
            print("   OK - Dados antigos removidos")
            
            # Dados profissionais reais (SEM acentos)
            print("\n2. Preparando dados reais de follow-ups...")
            followups_data = [
                "Revisao contrato CON-2024-015 TechSolutions - Valor: R$ 125.000,00",
                "Apresentacao projeto Sistema Gestao Integrada para diretoria",
                "Follow-up equipe desenvolvimento sprint 24 - Entrega: 15/02/2024",
                "Analise metricas Q4/2024 - Faturamento: R$ 2,5M, Crescimento: 15%",
                "Reuniao cliente VarejoMaster - Projeto expansao lojas",
                "Preparacao relatorio trimestral conselho - Deadline: 20/02/2024",
                "Negociacao orcamento TI 2025 - Valor: R$ 850.000,00",
                "Analise proposta filial Sao Paulo - Investimento: R$ 3,2M",
                "Auditoria processos financeiro - Prazo: 28/02/2024",
                "Implementacao sistema CRM - Fase 3: Treinamento"
            ]
            
            statuses = ['PENDENTE', 'EM_ANDAMENTO', 'ABERTO', 'PENDENTE', 
                       'EM_ANDAMENTO', 'ABERTO', 'PENDENTE', 'EM_ANDAMENTO', 
                       'PENDENTE', 'ABERTO']
            
            due_days = [3, 7, 2, 5, 10, 12, 4, 6, 8, 14]
            
            print("\n3. Inserindo follow-ups no banco...")
            for i, (desc, status, days) in enumerate(zip(followups_data, statuses, due_days), 1):
                insert_sql = text('''
                    INSERT INTO followups 
                    (description, status, owner_id, created_at, due_date) 
                    VALUES (:desc, :status, 1, NOW(), NOW() + INTERVAL :days DAY)
                ''')
                
                conn.execute(insert_sql, {
                    'desc': desc,
                    'status': status,
                    'days': days
                })
                
                print(f"   {i:2d}. [{status:12}] {desc[:50]}...")
            
            conn.commit()
            print(f"\nOK - {len(followups_data)} follow-ups inseridos para owner_id=1")
            
            # Verificacao final
            print("\n" + "=" * 60)
            print("VERIFICACAO FINAL")
            print("=" * 60)
            
            # Contagem total
            count = conn.execute(text('SELECT COUNT(*) FROM followups WHERE owner_id = 1')).scalar()
            print(f"\nTOTAL follow-ups owner_id=1: {count}")
            
            # Contagem por status
            status_counts = conn.execute(text('''
                SELECT status, COUNT(*) 
                FROM followups 
                WHERE owner_id = 1 
                GROUP BY status
            ''')).fetchall()
            
            print("\nDISTRIBUICAO POR STATUS:")
            for status, qty in status_counts:
                print(f"   * {status}: {qty} follow-up(s)")
            
            # Amostra dados
            print("\nAMOSTRA DOS DADOS:")
            rows = conn.execute(text('''
                SELECT id, description, status, due_date 
                FROM followups 
                WHERE owner_id = 1 
                ORDER BY due_date ASC
                LIMIT 3
            ''')).fetchall()
            
            for r in rows:
                due_date = r[3].strftime('%d/%m/%Y') if r[3] else 'Sem data'
                print(f"\nID {r[0]}:")
                print(f"   Descricao: {r[1]}")
                print(f"   Status: {r[2]}")
                print(f"   Vencimento: {due_date}")
            
            print("\n" + "=" * 60)
            print("PROXIMOS PASSOS:")
            print("Teste: curl -X POST http://localhost:8080/api/v1/chat")
            print("Mensagem: 'Listar meus follow-ups'")
            print("=" * 60)
            
    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
