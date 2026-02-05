#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta

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
            result = conn.execute(text('DELETE FROM followups WHERE owner_id = 1 RETURNING COUNT(*)'))
            deleted = result.scalar() or 0
            conn.commit()
            print(f"   OK - {deleted} dados antigos removidos")
            
            # Dados profissionais reais (SEM acentos)
            print("\n2. Preparando 10 follow-ups reais...")
            
            followups = [
                ("Revisao contrato CON-2024-015 TechSolutions - Valor: R$ 125.000,00", "PENDENTE", 3),
                ("Apresentacao projeto Sistema Gestao Integrada para diretoria", "EM_ANDAMENTO", 7),
                ("Follow-up equipe desenvolvimento sprint 24 - Entrega: 15/02/2024", "ABERTO", 2),
                ("Analise metricas Q4/2024 - Faturamento: R$ 2,5M, Crescimento: 15%", "PENDENTE", 5),
                ("Reuniao cliente VarejoMaster - Projeto expansao lojas", "EM_ANDAMENTO", 10),
                ("Preparacao relatorio trimestral conselho - Deadline: 20/02/2024", "ABERTO", 12),
                ("Negociacao orcamento TI 2025 - Valor: R$ 850.000,00", "PENDENTE", 4),
                ("Analise proposta filial Sao Paulo - Investimento: R$ 3,2M", "EM_ANDAMENTO", 6),
                ("Auditoria processos financeiro - Prazo: 28/02/2024", "PENDENTE", 8),
                ("Implementacao sistema CRM - Fase 3: Treinamento usuarios", "ABERTO", 14)
            ]
            
            print("\n3. Inserindo follow-ups no banco...")
            inserted = 0
            
            for desc, status, days in followups:
                # Calcula data de vencimento
                due_date = datetime.now() + timedelta(days=days)
                
                # Insere usando parâmetros seguros
                sql = text('''
                    INSERT INTO followups 
                    (description, status, owner_id, created_at, due_date) 
                    VALUES (:desc, :status, 1, NOW(), :due_date)
                ''')
                
                conn.execute(sql, {
                    'desc': desc,
                    'status': status,
                    'due_date': due_date
                })
                
                inserted += 1
                print(f"   {inserted:2d}. [{status:12}] {desc[:50]}...")
            
            conn.commit()
            print(f"\nOK - {inserted} follow-ups inseridos para owner_id=1")
            
            # Verificacao final
            print("\n" + "=" * 60)
            print("VERIFICACAO FINAL")
            print("=" * 60)
            
            # Contagem total
            result = conn.execute(text('SELECT COUNT(*) FROM followups WHERE owner_id = 1'))
            count = result.scalar()
            print(f"\nTOTAL follow-ups owner_id=1: {count}")
            
            if count > 0:
                # Amostra dados
                print("\nAMOSTRA DOS DADOS:")
                result = conn.execute(text('''
                    SELECT id, description, status, due_date 
                    FROM followups 
                    WHERE owner_id = 1 
                    ORDER BY due_date ASC
                    LIMIT 3
                '''))
                
                for row in result:
                    id_num, desc, status, due = row
                    due_str = due.strftime('%d/%m/%Y') if due else 'Sem data'
                    print(f"\nID {id_num}:")
                    print(f"   Descricao: {desc}")
                    print(f"   Status: {status}")
                    print(f"   Vencimento: {due_str}")
            
            print("\n" + "=" * 60)
            print("PROXIMOS PASSOS:")
            print("1. Teste o chat com: curl -X POST http://localhost:8080/api/v1/chat")
            print("2. Mensagem: 'Listar meus follow-ups'")
            print("3. Verifique os logs do servidor")
            print("=" * 60)
            
            return True
            
    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
