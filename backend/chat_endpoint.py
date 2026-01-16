# =====================================================
# CHAT API PARA PRODU√á√ÉO (O QUE O FRONTEND ESPERA)
# =====================================================

@app.post("/api/v1/chat/")
async def production_chat_endpoint(data: dict):
    """Endpoint que o frontend est√° chamando"""
    message = data.get("message", "")
    
    try:
        # Tenta usar OpenAI se dispon√≠vel
        import openai
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Voc√™ √© o assistente corporativo MAWDSLEYS. Responda de forma profissional."},
                {"role": "user", "content": message}
            ],
            temperature=0.4,
            max_tokens=500
        )
        reply = response.choices[0].message["content"]
    except Exception:
        # Fallback se OpenAI falhar
        if "oi" in message.lower() or "ol√°" in message.lower():
            reply = "Ì±ã Ol√°! Eu sou o Agente MAWDSLEYS."
        else:
            reply = f"Ì¥ñ MAWDSLEYS Production\n\nRecebi: '{message}'\n\nSistema em funcionamento."
    
    return {
        "reply": reply,
        "status": "success",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/chat/health")
async def production_chat_health():
    return {"status": "healthy", "endpoint": "/api/v1/chat/"}
