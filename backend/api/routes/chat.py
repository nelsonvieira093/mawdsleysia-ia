# E:\MAWDSLEYS-AGENTE\backend\api\routes\chat.py - VERSÃO CORRIGIDA COM MODO EXECUTIVO
import os
import json
import re
import unicodedata
from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text, desc, or_
from database.session import get_db
from api.routes.auth import require_any_auth
# REMOVA este import problemático e use SQL direto
# from database.db_models import FollowUp
import openai

# 🔥 IMPORTE A NOVA FUNÇÃO
from services.ai_service import analyze_text, analyze_executive_text

# OpenAI - config segura
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
openai.api_key = OPENAI_API_KEY if OPENAI_API_KEY else None

router = APIRouter(prefix="/api/v1/chat", tags=["Chat MAWDSLEYS"])

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None
    mode: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    timestamp: str
    intent: Optional[str] = None
    source: Optional[str] = None

@router.get("/health")
def chat_health():
    return {
        "status": "online",
        "service": "MAWDSLEYS Chat Inteligente",
        "openai_configured": bool(OPENAI_API_KEY),
        "timestamp": datetime.utcnow().isoformat(),
        "capabilities": ["followups", "bullet_journal_ceo"]  # 🔥 ADICIONADO
    }

def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    return text.lower()

def detect_intent(message: str) -> Dict[str, Any]:
    msg = normalize(message)
    
    followup_patterns = [
        r"\bfollow[-\s]?ups?\b", r"\bpendente", r"\bacoes?\b", 
        r"\btarefa", r"\bprazo", r"\bdevo", r"\btenho que fazer",
        r"\blista de (tarefas|afazeres)", r"\bo que falta", r"\bpróximos passos",
        r"\bmostrar (meus )?followups?", r"\bver (meus )?followups?",
        r"\bquais (são|sao) (meus )?followups?", r"\btodos os followups?",
        r"\blistar (meus )?followups?"
    ]
    
    for pattern in followup_patterns:
        if re.search(pattern, msg, re.IGNORECASE):
            return {"intent": "FOLLOWUPS", "confidence": 0.95}
    
    return {"intent": "GENERIC", "confidence": 0.5}

def format_followup_response(followups: List[dict]) -> str:  # MUDANÇA: aceita dict em vez de FollowUp
    if not followups:
        return "📭 **Não há follow-ups registrados no sistema.**\n\n💡 **Dica:** Adicione follow-ups primeiro para visualizá-los aqui."
    
    response = "📋 **SEUS FOLLOW-UPS:**\n\n"
    
    for i, fup in enumerate(followups, 1):
        description = fup.get("description", "Sem descrição")
        if len(description) > 70:
            title = description[:70] + "..."
        else:
            title = description
        
        status = fup.get("status", "PENDENTE")
        status_icon = "🟡" if status.upper() in ["PENDENTE", "EM ANDAMENTO"] else "🟢"
        
        due_info = ""
        if fup.get("due_date"):
            try:
                due_date = fup["due_date"].strftime('%d/%m/%Y')
                due_info = f" | 📅 {due_date}"
            except:
                pass
        
        response += f"{i}. **{title}**\n"
        response += f"   {status_icon} **Status:** {status}{due_info}\n"
        
        if fup.get('owner_name'):
            response += f"   👤 **Responsável:** {fup['owner_name']}\n"
        
        if i < len(followups):
            response += "\n"
    
    response += f"\n---\n📊 **Total encontrado:** {len(followups)} follow-up(s)"
    return response

# ADICIONE esta função nova para buscar com SQL direto
def get_followups_sql_direct(db: Session, user_id: str) -> List[dict]:
    """Busca follow-ups usando SQL DIRETO para evitar conflito de models"""
    try:
        # Query SQL segura com parâmetros
        query = text("""
            SELECT 
                id,
                description,
                status,
                owner_id,
                owner_name,
                due_date,
                created_at,
                priority,
                tags
            FROM follow_ups 
            WHERE owner_id = :user_id 
               OR :user_id = '1'  -- Admin vê tudo
            ORDER BY 
                CASE 
                    WHEN status = 'PENDENTE' THEN 1
                    WHEN status = 'EM_ANDAMENTO' THEN 2 
                    WHEN status = 'CONCLUIDO' THEN 3
                    ELSE 4
                END,
                created_at DESC
            LIMIT 20
        """)
        
        result = db.execute(query, {"user_id": str(user_id)})
        rows = result.fetchall()
        
        # Converte para lista de dicionários
        followups = []
        for row in rows:
            followups.append({
                "id": row[0],
                "description": row[1],
                "status": row[2],
                "owner_id": row[3],
                "owner_name": row[4],
                "due_date": row[5],
                "created_at": row[6],
                "priority": row[7],
                "tags": row[8]
            })
        
        return followups
        
    except Exception as e:
        print(f"[SQL ERROR] {e}")
        # Fallback: busca simples
        try:
            result = db.execute(
                text("SELECT description, status FROM follow_ups LIMIT 10")
            )
            rows = result.fetchall()
            return [{"description": r[0], "status": r[1]} for r in rows]
        except:
            return []

@router.get("/debug/followups")
async def debug_followups(
    current_user: dict = Depends(require_any_auth),
    db: Session = Depends(get_db),
):
    """Endpoint de debug para ver todos os follow-ups"""
    try:
        user_id = current_user.get("user_id")
        
        print(f"🔍 [DEBUG] Buscando follow-ups para user_id: {user_id}")
        
        # MODIFICAÇÃO: Use SQL direto aqui também
        followups = get_followups_sql_direct(db, str(user_id))
        print(f"🔍 [DEBUG] Follow-ups encontrados: {len(followups)}")
        
        # Formata resultado
        result = []
        for fup in followups[:20]:
            result.append({
                "id": fup["id"],
                "description": fup["description"],
                "status": fup["status"],
                "owner_id": fup["owner_id"],
                "owner_id_type": type(fup["owner_id"]).__name__ if fup["owner_id"] else None,
                "due_date": fup["due_date"].isoformat() if fup["due_date"] else None,
                "created_at": fup["created_at"].isoformat() if fup["created_at"] else None
            })
        
        return {
            "success": True,
            "user_id": user_id,
            "user_id_type": type(user_id).__name__,
            "total_followups": len(followups),
            "followups": result,
            "debug_info": {
                "searched_by": "SQL direto",
                "database_connected": True
            }
        }
        
    except Exception as e:
        print(f"❌ [DEBUG] Erro: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e), "success": False}

@router.get("/test-followups")
async def test_followups(
    current_user: dict = Depends(require_any_auth),
    db: Session = Depends(get_db),
):
    """Teste simples de follow-ups - MODIFICADO para SQL direto"""
    try:
        user_id = current_user.get("user_id")
        
        print(f"🔍 [TEST] Testando follow-ups para user_id: {user_id}")
        
        # MODIFICAÇÃO: Use SQL direto
        # Total no banco
        result = db.execute(text("SELECT COUNT(*) FROM follow_ups"))
        total_in_db = result.scalar()
        
        # Follow-ups do usuário
        result = db.execute(
            text("SELECT COUNT(*) FROM follow_ups WHERE owner_id = :user_id"),
            {"user_id": str(user_id)}
        )
        user_followups_count = result.scalar()
        
        # Amostra
        result = db.execute(
            text("SELECT id, description, status, owner_id FROM follow_ups LIMIT 5")
        )
        sample_data = []
        for row in result:
            sample_data.append({
                "id": row[0],
                "description": row[1][:50] if row[1] else None,
                "status": row[2],
                "owner_id": row[3],
                "owner_id_type": type(row[3]).__name__ if row[3] else None
            })
        
        return {
            "success": True,
            "user_id": user_id,
            "total_followups_in_db": total_in_db,
            "user_followups_count": user_followups_count,
            "database_info": {
                "table_exists": True,
                "total_records": total_in_db
            },
            "sample_data": sample_data
        }
        
    except Exception as e:
        print(f"❌ [TEST] Erro: {e}")
        return {"error": str(e), "success": False}

@router.post("", response_model=ChatResponse)
async def chat_inteligente(
    data: ChatRequest,
    current_user: dict = Depends(require_any_auth),
    db: Session = Depends(get_db),
):
    """Endpoint principal do chat - COM MODO BULLET JOURNAL (CEO)"""
    try:
        user_id = current_user.get("user_id")
        user_email = current_user.get("email", "executivo")
        
        print(f"🔍 [CHAT] Iniciando para usuário: {user_email} (ID: {user_id})")
        print(f"   📝 Mensagem: {data.message}")
        print(f"   🎚️  Modo solicitado: {data.mode}")
        
        # =============================
        # 🔥 MODO BULLET JOURNAL (CEO)
        # =============================
        if data.mode == "bullet_journal_ceo":
            print("   🎯 Modo executivo ativado - analisando texto...")
            
            try:
                # Usa a nova função analyze_executive_text
                executive_analysis = analyze_executive_text(data.message)
                
                print(f"   ✅ Análise executiva concluída:")
                print(f"     - Hashtags: {executive_analysis.get('hashtags', [])}")
                print(f"     - Prioridade: {executive_analysis.get('priority')}")
                print(f"     - Deadline: {executive_analysis.get('deadline')}")
                print(f"     - Budget: {executive_analysis.get('budget_impact')}")
                print(f"     - Ações: {len(executive_analysis.get('actions', []))}")
                
                # 🔥 Retorna como JSON string para o frontend
                # O frontend espera 'reply' contendo o JSON ou texto
                reply_json = json.dumps(executive_analysis, ensure_ascii=False)
                
                return ChatResponse(
                    reply=reply_json,
                    timestamp=datetime.utcnow().isoformat(),
                    intent="EXECUTIVE_ANALYSIS",
                    source="ai_service"
                )
                
            except Exception as e:
                print(f"❌ ERRO no modo executivo: {str(e)}")
                import traceback
                traceback.print_exc()
                
                # Fallback: usa análise básica se a executiva falhar
                basic_analysis = analyze_text(data.message)
                fallback_reply = json.dumps({
                    "summary": data.message,
                    "hashtags": ["Executivo"],
                    "followups": [],
                    "actions": [data.message],
                    "register_location": "DailyLog",
                    "error": "Análise executiva temporariamente indisponível"
                }, ensure_ascii=False)
                
                return ChatResponse(
                    reply=fallback_reply,
                    timestamp=datetime.utcnow().isoformat(),
                    intent="EXECUTIVE_FALLBACK",
                    source="system"
                )
        
        # =============================
        # MODO CHAT NORMAL (seguir fluxo existente)
        # =============================
        
        # Detectar intenção (apenas para modo normal)
        intent_data = detect_intent(data.message)
        intent = intent_data["intent"]
        
        print(f"   🎯 Intenção detectada: {intent}")
        
        # FOLLOWUPS - COM SQL DIRETO
        if intent == "FOLLOWUPS":
            try:
                print(f"🔍 [CHAT] Buscando follow-ups com SQL DIRETO...")
                
                # Primeiro: verifica quantos follow-ups existem no total
                result = db.execute(text("SELECT COUNT(*) FROM follow_ups"))
                total_count = result.scalar()
                print(f"   📊 Total de follow-ups no banco: {total_count}")
                
                # Busca com SQL DIRETO (nova função)
                followups = get_followups_sql_direct(db, str(user_id))
                search_method = "SQL direto"
                
                print(f"   ✅ Follow-ups encontrados: {len(followups)} (método: {search_method})")
                
                # Log dos primeiros resultados
                for i, fup in enumerate(followups[:3], 1):
                    desc = fup.get("description", "Sem descrição")
                    owner = fup.get("owner_id", "N/A")
                    print(f"   📝 Sample {i}: '{desc[:40]}...' | Owner: {owner}")
                
                # Formata resposta
                reply = format_followup_response(followups)
                
                return ChatResponse(
                    reply=reply,
                    timestamp=datetime.utcnow().isoformat(),
                    intent=intent,
                    source="database"
                )
                
            except Exception as e:
                print(f"❌ ERRO CRÍTICO em follow-ups: {str(e)}")
                import traceback
                traceback.print_exc()
                
                # Resposta de erro detalhada
                error_msg = f"""⚠️ **Erro ao buscar follow-ups**

Detalhes técnicos:
• O sistema detectou sua solicitação
• Mas encontrou um erro no banco de dados
• Erro: {str(e)[:100]}

💡 **Soluções:**
1. Tente novamente em alguns segundos
2. Verifique se há follow-ups cadastrados
3. Use o endpoint /api/v1/chat/debug/followups para diagnóstico"""
                
                return ChatResponse(
                    reply=error_msg,
                    timestamp=datetime.utcnow().isoformat(),
                    intent=intent,
                    source="system_error"
                )
        
        # CONSULTA GENÉRICA (mantido igual)
        else:
            # 🔥 MODIFICAÇÃO: Se não for follow-ups, também pode usar análise executiva básica
            # se a mensagem parecer "executiva" (tem verbos de ação, prazos, valores)
            
            msg_lower = data.message.lower()
            has_executive_keywords = any(word in msg_lower for word in 
                                       ["revisar", "analisar", "preparar", "entregar", 
                                        "até", "prazo", "valor", "r$", "urgente"])
            
            if has_executive_keywords:
                print("   🔍 Mensagem parece executiva, usando análise básica...")
                basic_analysis = analyze_text(data.message)
                
                # Formata resposta amigável mantendo estrutura
                reply = f"""🤖 **MAWDSLEYS Assistant - Análise Detectada**

📋 **Resumo:** {basic_analysis.get('summary', data.message[:100])}

🏷️  **Tags:** {', '.join(basic_analysis.get('tags', [])) or 'Nenhuma'}

💡 **Para análise executiva completa, use o modo "Bullet Journal (CEO)" no seletor superior.**"""
            else:
                # Resposta padrão genérica
                reply = """🤖 **MAWDSLEYS Assistant**

Para gerenciar seus follow-ups, digite:
• **"follow-ups"** - Listar todos os follow-ups
• **"mostrar tarefas"** - Ver suas tarefas
• **"lista de pendências"** - Ver pendências

💡 **Dica:** Você também pode:
- Perguntar sobre follow-ups específicos
- Pedir para filtrar por status
- Solicitar um resumo"""
            
            return ChatResponse(
                reply=reply,
                timestamp=datetime.utcnow().isoformat(),
                intent="GENERIC",
                source="system"
            )
    
    except Exception as e:
        print(f"❌ ERRO GERAL no chat: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return ChatResponse(
            reply="⚠️ Ocorreu um erro interno no sistema. Por favor, tente novamente ou contate o suporte.",
            timestamp=datetime.utcnow().isoformat(),
            intent="ERROR",
            source="system"
        )

# 🔥 NOVO ENDPOINT PARA TESTE DA ANÁLISE EXECUTIVA
@router.get("/test-executive-analysis")
async def test_executive_analysis():
    """Endpoint para testar a análise executiva sem autenticação"""
    try:
        test_messages = [
            "Revisar contrato urgente até sexta-feira, valor R$ 100.000",
            "Desenvolver nova feature do sistema até 30/03, equipe de Tecnologia",
            "Reunião de alinhamento com equipe comercial amanhã às 10h",
        ]
        
        results = []
        for msg in test_messages:
            analysis = analyze_executive_text(msg)
            results.append({
                "input": msg,
                "output": {
                    "hashtags": analysis.get("hashtags"),
                    "priority": analysis.get("priority"),
                    "deadline": analysis.get("deadline"),
                    "budget_impact": analysis.get("budget_impact"),
                    "actions_count": len(analysis.get("actions", [])),
                    "followups_count": len(analysis.get("followups", []))
                }
            })
        
        return {
            "success": True,
            "service": "Executive Analysis",
            "test_results": results,
            "note": "Para usar no frontend, envie POST com mode='bullet_journal_ceo'"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "note": "Verifique se a função analyze_executive_text está importada corretamente"
        }