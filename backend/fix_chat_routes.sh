#!/bin/bash

echo "Ì¥ß CORRIGINDO CONFLITOS DE ROTAS NO main.py"
echo "=========================================="

# Backup do arquivo original
if [ ! -f "main.py.backup" ]; then
    cp main.py main.py.backup
    echo "Ì≥Å Backup criado: main.py.backup"
fi

# 1. Remover import do chat_web (linha 13)
echo "1. Removendo import do chat_web..."
sed -i '13d' main.py

# 2. Comentar endpoints de chat p√∫blico
echo "2. Comentando endpoints de chat p√∫blico..."
sed -i '896,949s/^@app\./# @app./' main.py
sed -i '896,949s/^async def/# async def/' main.py

# 3. Comentar chat_router_legacy
echo "3. Comentando chat_router_legacy..."
sed -i '1052s/^app\.include_router(chat_router_legacy)/# app.include_router(chat_router_legacy)/' main.py

# 4. Verificar tamb√©m a linha 838 (j√° comentada, mas garantir)
echo "4. Verificando linha 838..."
sed -i '838s/^app\.include_router(chat_web\.router)/# app.include_router(chat_web.router)/' main.py

echo ""
echo "‚úÖ CORRE√á√ïES APLICADAS!"
echo ""
echo "Ì≥ã RESUMO DAS ALTERA√á√ïES:"
echo "========================="
echo "- ‚ùå Removido: import chat_web"
echo "- ‚ùå Comentado: /api/v1/chat/public"
echo "- ‚ùå Comentado: /api/v1/chat/public/health"
echo "- ‚ùå Comentado: chat_router_legacy"
echo ""
echo "Ì¥Ñ Reinicie o servidor para aplicar as mudan√ßas:"
echo "   pkill -f uvicorn"
echo "   uvicorn main:app --reload --port 8080"
