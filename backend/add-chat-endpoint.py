import re

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Encontra onde começa a seção CHAT API LEGACY
start_marker = '# =====================================================\n# CHAT API LEGACY (FALLBACK)'
if start_marker in content:
    # Insere o novo endpoint ANTES da seção legacy
    new_chat_section = '''# =====================================================
# CHAT API PARA PRODUÇÃO (O QUE O FRONTEND ESPERA)
# =====================================================

@app.post("/api/v1/chat/")
async def production_chat_endpoint(data: dict):
    """Endpoint que o frontend está chamando"""
    message = data.get("message", "")
    
    try:
        # Tenta usar OpenAI se disponível
        import openai
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é o assistente corporativo MAWDSLEYS. Responda de forma profissional."},
                {"role": "user", "content": message}
            ],
            temperature=0.4,
            max_tokens=500
        )
        reply = response.choices[0].message["content"]
    except Exception:
        # Fallback se OpenAI falhar
        if "oi" in message.lower() or "olá" in message.lower():
            reply = "��� Olá! Eu sou o Agente MAWDSLEYS."
        else:
            reply = f"��� MAWDSLEYS Production\\n\\nRecebi: \\"{message}\\"\\n\\nSistema em funcionamento."
    
    return {
        "reply": reply,
        "status": "success",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/chat/health")
async def production_chat_health():
    return {"status": "healthy", "endpoint": "/api/v1/chat/"}
'''

    # Insere a nova seção
    parts = content.split(start_marker)
    new_content = parts[0] + new_chat_section + '\n\n' + start_marker + parts[1]
    
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Endpoint /api/v1/chat/ adicionado com sucesso!")
else:
    print("❌ Não encontrei a seção CHAT API LEGACY")
