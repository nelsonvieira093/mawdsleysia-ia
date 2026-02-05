print("Ì¥ß Criando tabelas no PostgreSQL...")

import sys
sys.path.append('/e/MAWDSLEYS-AGENTE/backend')

try:
    from database.session import Base, engine, SessionLocal
    from database.db_models import FollowUp
    
    # Cria todas as tabelas
    Base.metadata.create_all(bind=engine)
    print("‚úÖ Tabelas criadas!")
    
    # Verifica e cria dados
    db = SessionLocal()
    count = db.query(FollowUp).count()
    
    if count == 0:
        print("Ì≥ù Criando follow-ups de teste...")
        
        # Dados b√°sicos
        test_data = [
            ("Revisar relatorio financeiro", "PENDENTE", "1"),
            ("Agendar reuniao com equipe", "EM_ANDAMENTO", "1"),
            ("Finalizar proposta comercial", "CONCLUIDO", "1"),
            ("Atualizar documentacao", "PENDENTE", "1"),
            ("Analisar metricas de performance", "PENDENTE", "1")
        ]
        
        for desc, status, owner in test_data:
            fup = FollowUp(description=desc, status=status, owner_id=owner)
            db.add(fup)
        
        db.commit()
        print(f"‚úÖ {len(test_data)} follow-ups criados!")
    else:
        print(f"‚úÖ Ja existem {count} follow-ups")
    
    # Mostra exemplo
    print("\nÌ≥ã EXEMPLO:")
    for fup in db.query(FollowUp).limit(2).all():
        print(f"   ‚Ä¢ {fup.description[:40]}... | Status: {fup.status}")
    
    db.close()
    
except Exception as e:
    print(f"‚ùå Erro: {e}")
    import traceback
    traceback.print_exc()
