#!/bin/bash
echo "��� CORRIGINDO UVICORN PARA FLY.IO"

cd /e/MAWDSLEYS-AGENTE/backend

echo "[1] Criando backup..."
cp main.py main.py.backup.$(date +%s)

echo "[2] Encontrando e corrigindo bloco uvicorn..."
# Usa Python com encoding correto
python3 -c "
import sys

try:
    # Tenta diferentes encodings
    for encoding in ['utf-8', 'latin-1', 'cp1252']:
        try:
            with open('main.py', 'r', encoding=encoding) as f:
                content = f.read()
            print(f'✅ Arquivo lido com encoding: {encoding}')
            break
        except UnicodeDecodeError:
            continue
    else:
        print('❌ Não consegui ler o arquivo com nenhum encoding')
        sys.exit(1)
    
    # Encontra o bloco problemático
    import re
    
    # Padrão para encontrar
    pattern = r'if __name__ == \"__main__\":\s*uvicorn\.run\(\s*\"main:app\",\s*host=\"0\.0\.0\.0\",\s*port=int\(os\.getenv\(\"PORT\", 8080\)\),\s*reload=False\s*\)'
    
    if re.search(pattern, content, re.DOTALL):
        print('✅ Encontrou bloco uvicorn.run')
        
        # Substitui por versão segura
        new_block = '''if __name__ == \"__main__\"\:
    # Fly.io inicia via Dockerfile
    pass'''
        
        new_content = re.sub(pattern, new_block, content, flags=re.DOTALL)
        
        with open('main.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print('✅ Bloco corrigido')
    else:
        print('⚠️  Bloco uvicorn.run não encontrado, adicionando versão segura')
        # Adiciona no final
        safe_block = '''
# =====================================================
# MAIN FOR FLY.IO
# =====================================================
if __name__ == \"__main__\"\:
    # Fly.io starts via: uvicorn main:app --host 0.0.0.0 --port 8080
    pass
'''
        with open('main.py', 'a', encoding='utf-8') as f:
            f.write(safe_block)
        
        print('✅ Versão segura adicionada')
        
except Exception as e:
    print(f'❌ Erro: {e}')
    sys.exit(1)
"

echo "[3] Verificando correção..."
echo "--- Últimas 15 linhas ---"
tail -n 15 main.py
echo "----------------------"

echo "[4] Deploy..."
flyctl deploy -a backend-silent-snowflake-7300 --detach

echo ""
echo "✅ CORREÇÃO APLICADA!"
echo "⏳ Aguarde deploy completar (2-3 minutos)"
echo "��� Depois teste: curl https://backend-silent-snowflake-7300.fly.dev/health"
