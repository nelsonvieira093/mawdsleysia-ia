# backend/database/base_class.py
# Faz com que todos os modelos importem o mesmo Base definido em session.py

from backend.database.session import Base



# Expõe Base para os modelos do projeto:
__all__ = ["Base"]
