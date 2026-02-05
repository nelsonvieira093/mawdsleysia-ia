#!/usr/bin/env python3
"""
Script para inserir dados REAIS de follow-ups no banco MAWDSLEYS
"""

import os
import sys
from sqlalchemy import create_engine, text

# Configura√ß√£o do banco
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://postgres:Agente0934@localhost:5432/mawdsleys'

def main():
    """Insere dados reais de follow-ups"""
    try:
        engine = create_engine(os.environ['DATABASE_URL'])
        
        with engine.connect() as conn:
            print("=" * 60)
            print("INSER√á√ÉO DE DADOS REAIS DE FOLLOW-UPS")
            print("=" * 60)
            
            # Limpa dados antigos do owner_id=1
            print("\n1. Limpando dados antigos do owner_id=1...")
            conn.execute(text('DELETE FROM followups WHERE owner_id = 1'))
            conn.commit()
            print("   ‚úì Dados antigos removidos")
            
            # Dados profissionais reais
            print("\n2. Preparando dados reais de follow-ups...")
            followups_data = [
                {
                    'desc': 'Revisao do contrato CON-2024-015 com TechSolutions Ltda - Valor: R$ 125.000,00',
                    'status': 'PENDENTE',
                    'due_days': 3
                },
                {
                    'desc': 'Apresentacao do projeto Sistema de Gestao Integrada para diretoria - Reuniao mensal',
                    'status': 'EM_ANDAMENTO', 
                    'due_days': 7
                },
                {
                    'desc': 'Follow-up com equipe de desenvolvimento sobre sprint 24 - Entrega: 15/02/2024',
                    'status': 'ABERTO',
                    'due_days': 2
                },
                {
                    'desc': 'Analise metricas desempenho Q4/2024 - Faturamento: R$ 2,5M, Crescimento: 15%',
                    'status': 'PENDENTE',
                    'due_days': 5
                },
                {
                    'desc': 'Reuniao alinhamento cliente VarejoMaster - Projeto expansao de lojas',
                    'status': 'EM_ANDAMENTO',
                    'due_days': 10
                },
                {
                    'desc': 'Preparacao relatorio trimestral conselho administrativo - Deadline: 20/02/2024',
                    'status': 'ABERTO',
                    'due_days': 12
                },
                {
                    'desc': 'Negociacao orcamento departamento TI 2025 - Valor solicitado: R$ 850.000,00',
                    'status': 'PENDENTE',
                    'due_days': 4
                },
                {
                    'desc': 'Analise proposta comercial nova filial Sao Paulo - Investimento: R$ 3,2M',
                    'status': 'EM_ANDAMENTO',
                    'due_days': 6
                },
                {
                    'desc': 'Auditoria processos internos departamento financeiro - Prazo: 28/02/2024',
                    'status': 'PENDENTE',
                    'due_days': 8
                },
                {
                    'desc': 'Implementacao novo sistema CRM - Fase 3: Treinamento usuarios',
                    'status': 'ABERTO',
                    'due_days': 14
                }
            ]
            
            print("\n3. Inserindo follow-ups no banco...")
            for i, data in enumerate(followups_data, 1):
                insert_sql = text('''
                    INSERT INTO followups 
                    (description, status, owner_id, created_at, due_date) 
                    VALUES 
                    (:desc, :status, 1, NOW(), NOW() + INTERVAL :days DAY)
                ''')
                
                conn.execute(insert_sql, {
                    'desc': data['desc'],
                    'status': data['status'],
                    'days': data['due_days']
                })
                
                # Exibe progresso
                print(f"   {i:2d}. [{data['status']:12}] {data['desc'][:50]}...")
            
            conn.commit()
            print(f"\n‚úì {len(followups_data)} follow-ups REAIS inseridos para owner_id=1")
            
            # Verifica√ß√£o final
            print("\n" + "=" * 60)
            print("VERIFICA√á√ÉO FINAL")
            print("=" * 60)
            
            # Contagem total
            count = conn.execute(text('SELECT COUNT(*) FROM followups WHERE owner_id = 1')).scalar()
            print(f"\nÌ≥ä TOTAL de follow-ups para owner_id=1: {count}")
            
            # Contagem por status
            status_counts = conn.execute(text('''
                SELECT status, COUNT(*) 
                FROM followups 
                WHERE owner_id = 1 
                GROUP BY status
            ''')).fetchall()
            
            print("\nÌ≥à DISTRIBUI√á√ÉO POR STATUS:")
            for status, qty in status_counts:
                print(f"   ‚Ä¢ {status}: {qty} follow-up(s)")
            
            # Amostra dos dados
            print("\nÌ≥ù AMOSTRA DOS DADOS INSERIDOS:")
            rows = conn.execute(text('''
                SELECT id, description, status, due_date 
                FROM followups 
                WHERE owner_id = 1 
                ORDER BY due_date ASC
                LIMIT 5
            ''')).fetchall()
            
            for r in rows:
                due_date = r[3].strftime('%d/%m/%Y') if r[3] else 'Sem data'
                print(f"\n   ID {r[0]}:")
                print(f"      Descri√ß√£o: {r[1]}")
                print(f"      Status: {r[2]}")
                print(f"      Vencimento: {due_date}")
            
            print("\n" + "=" * 60)
            print("PR√ìXIMOS PASSOS:")
            print("1. Teste o chat: curl -X POST http://localhost:8080/api/v1/chat")
            print("2. Mensagem: 'Listar meus follow-ups'")
            print("3. Verifique os logs do servidor")
            print("=" * 60)
            
    except Exception as e:
        print(f"\n‚ùå ERRO: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
