print("Adicionando endpoint simples...")

# Le o main.py
with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Encontra onde adicionar (depois do endpoint /health)
# Procura por: @app.get("/health") ... } e adiciona depois

# Divide o conteudo em linhas
lines = content.split('\n')
new_lines = []

for i, line in enumerate(lines):
    new_lines.append(line)
    
    # Se encontrou o fim da funcao health
    if line.strip() == '}' and i > 2:
        # Verifica se as 3 linhas anteriores sao da funcao health
        if '@app.get("/health")' in lines[i-3]:
            # Adiciona novo endpoint
            new_lines.append('')
            new_lines.append('# =====================================================')
            new_lines.append('# ENDPOINT DE TESTE SIMPLES')
            new_lines.append('# =====================================================')
            new_lines.append('')
            new_lines.append('@app.post("/test-simple")')
            new_lines.append('async def test_simple():')
            new_lines.append('    from datetime import datetime')
            new_lines.append('    return {')
            new_lines.append('        "status": "success",')
            new_lines.append('        "message": "Teste simples funcionando",')
            new_lines.append('        "timestamp": datetime.utcnow().isoformat(),')
            new_lines.append('        "endpoint": "/test-simple"')
            new_lines.append('    }')
            new_lines.append('')
            print("✅ Endpoint /test-simple adicionado!")

# Escreve de volta
with open('main.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines))

print("✅ Arquivo atualizado!")
