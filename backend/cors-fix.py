# Script para adicionar CORS universal ao main.py
import re

with open('app/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Substitui a seção CORS
new_cors_section = '''app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ TEMPORÁRIO - permite todas origens
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)'''

# Encontra e substitui a seção CORS
pattern = r'app\.add_middleware\(\s*CORSMiddleware,[^)]+\)'
new_content = re.sub(pattern, new_cors_section, content, flags=re.DOTALL)

with open('app/main.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ CORS corrigido para permitir todas origens")
