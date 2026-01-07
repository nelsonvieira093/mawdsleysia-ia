with open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontra onde adicionar (depois do endpoint /health)
new_lines = []
added = False

for i, line in enumerate(lines):
    new_lines.append(line)
    
    # Se encontrou o fim da funcao health (linha com apenas })
    if line.strip() == '}' and not added:
        # Verifica se e o fim da funcao health
        # Procura para tras por @app.get("/health")
        for j in range(max(0, i-10), i):
            if '@app.get("/health")' in lines[j]:
                # Adiciona novo endpoint aqui
                new_lines.append('')
                new_lines.append('# =====================================================')
                new_lines.append('# ENDPOINT DE TESTE FUNCIONAL')
                new_lines.append('# =====================================================')
                new_lines.append('')
                new_lines.append('@app.post("/test-auto")')
                new_lines.append('async def test_auto_endpoint():')
                new_lines.append('    from datetime import datetime')
                new_lines.append('    return {')
                new_lines.append('        "status": "success",')
                new_lines.append('        "message": "Endpoint de teste funcional",')
                new_lines.append('        "timestamp": datetime.utcnow().isoformat(),')
                new_lines.append('        "system": "MAWDSLEYS",')
                new_lines.append('        "endpoint": "/test-auto",')
                new_lines.append('        "test": "automation-ready"')
                new_lines.append('    }')
                new_lines.append('')
                added = True
                print(f"Endpoint /test-auto adicionado na linha {i+1}")
                break

# Escreve de volta
with open('main.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Arquivo atualizado com sucesso!")
print("Para testar:")
print("   curl -X POST http://localhost:8000/test-auto -H 'Content-Type: application/json' -d '{}'")
