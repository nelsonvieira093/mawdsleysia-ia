# E:\MAWDSLEYS-AGENTE\backend\services\ai_service.py
import re

class AIService:
    pass


ACTION_VERBS = [
    "cobrar", "verificar", "confirmar", "resolver",
    "mandar", "checar", "definir", "analisar"
]


def analyze_text(text: str):
    text_l = text.lower()

    result = {
        "summary": text.strip(),
        "ritual_code": None,
        "tags": [],
        "followups": []
    }

    if "elsa" in text_l:
        result["ritual_code"] = "ONE_ON_ONE_ELSA"

    if any(v in text_l for v in ACTION_VERBS):
        result["tags"].append("#FollowUp")
        result["followups"].append({
            "description": text,
            "owner": "Elsa"
        })

    if "willentine" in text_l:
        result["tags"].append("#WILLENTINE")

    if "regulat" in text_l:
        result["tags"].append("#Regulatorio")

    return result


# ✅ FUNÇÃO ADICIONADA — NÃO ALTERA NADA EXISTENTE
def load_system_prompt() -> str:
    """
    Prompt padrão do sistema para o agente MAWDSLEYS.
    Mantido simples para não quebrar fluxos existentes.
    """
    return (
        "Você é o assistente corporativo MAWDSLEYS. "
        "Seja profissional, objetivo e orientado a ações, "
        "follow-ups e organização executiva."
    )


# 🔥 NOVA FUNÇÃO PARA MODO BULLET JOURNAL (CEO)
def analyze_executive_text(text: str) -> dict:
    """
    Analisa texto no modo Bullet Journal (CEO)
    Retorna dados estruturados para o ExecutiveBlock no frontend
    
    Args:
        text: Texto do usuário para análise executiva
        
    Returns:
        dict: Dados estruturados com hashtags, prioridades, prazos, etc.
    """
    text_lower = text.lower()
    
    # Inicializa resultado com estrutura completa
    result = {
        "hashtags": [],
        "summary": text.strip(),
        "structured_summary": "",
        "followups": [],
        "rituals": [],
        "directors": [],
        "actions": [],
        "register_location": "DailyLog",
        "deadline": None,
        "priority": None,
        "urgency": None,
        "impact": None,
        "complexity": None,
        "budget_impact": None,
        "team_members": [],
        "resources_needed": [],
        "risks": [],
        "decisions": [],
        "raw_text": text
    }
    
    # =============================
    # 1. EXTRAIR HASHTAGS E DIRETORIAS
    # =============================
    
    # Diretorias por palavras-chave
    director_keywords = {
        "Jurídico": ["contrato", "jurídico", "legal", "cláusula", "processo", "advogado"],
        "Financeiro": ["financeiro", "orçamento", "custo", "investimento", "receita", "despesa", "valor", "r$"],
        "Tecnologia": ["tecnologia", "ti", "sistema", "software", "aplicativo", "api", "desenvolvimento", "dev"],
        "Comercial": ["comercial", "vendas", "cliente", "contrato", "proposta", "negócio", "faturamento"],
        "RH": ["rh", "recursos humanos", "equipe", "colaborador", "funcionário", "contratação"],
        "Marketing": ["marketing", "campanha", "divulgação", "branding", "publicidade", "mídia"],
        "Operações": ["operações", "processo", "logística", "produção", "fornecedor", "entrega"],
        "Produto": ["produto", "feature", "funcionalidade", "lançamento", "design", "ux"]
    }
    
    for director, keywords in director_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            result["hashtags"].append(director)
            result["directors"].append(director)
    
    # Hashtag padrão se não encontrar
    if not result["hashtags"]:
        result["hashtags"].append("Executivo")
    
    # =============================
    # 2. DETECTAR PRIORIDADE E URGÊNCIA
    # =============================
    
    if any(word in text_lower for word in ["urgente", "asap", "hoje", "imediat", "crítico", "emergência"]):
        result["priority"] = "ALTA"
        result["urgency"] = 9
    elif any(word in text_lower for word in ["importante", "priorit", "relevante", "essencial"]):
        result["priority"] = "MÉDIA"
        result["urgency"] = 6
    else:
        result["priority"] = "BAIXA"
        result["urgency"] = 3
    
    # =============================
    # 3. EXTRAIR VALORES FINANCEIROS
    # =============================
    
    money_patterns = [
        r'R\$\s*(\d+[.,]?\d*)',
        r'US\$\s*(\d+[.,]?\d*)',
        r'(\d+[.,]?\d*)\s*(mil|milhão|bilhão|k|m|b)',
        r'valor\s*(?:de\s*)?(\d+[.,]?\d*)',
        r'custo\s*(?:de\s*)?(\d+[.,]?\d*)',
        r'investimento\s*(?:de\s*)?(\d+[.,]?\d*)',
        r'orçamento\s*(?:de\s*)?(\d+[.,]?\d*)'
    ]
    
    for pattern in money_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            if isinstance(matches[0], tuple):
                # Formata bonito: "R$ 100.000"
                value = matches[0][0].replace(',', '.').replace(' ', '')
                if 'mil' in matches[0][1].lower():
                    result["budget_impact"] = f"R$ {value} mil"
                elif 'milhão' in matches[0][1].lower():
                    result["budget_impact"] = f"R$ {value} milhões"
                else:
                    result["budget_impact"] = f"R$ {value}"
            else:
                result["budget_impact"] = matches[0]
            break
    
    # =============================
    # 4. EXTRAIR DATAS/PRAZOS
    # =============================
    
    date_patterns = [
        r'\b(\d{1,2}/\d{1,2}/\d{4})\b',  # DD/MM/YYYY
        r'\b(\d{1,2}\s+de\s+\w+\s+\d{4})\b',  # "15 de Março 2024"
        r'\b(amanhã|hoje)\b',
        r'\b(segunda|terça|quarta|quinta|sexta|sábado|domingo)(?:-feira)?\b',
        r'\b(\d{1,2}/\d{1,2})\b',  # DD/MM
        r'\baté\s+(\d{1,2}/\d{1,2}(?:/\d{4})?)',  # "até 15/03"
        r'\bpara\s+(\d{1,2}/\d{1,2}(?:/\d{4})?)',  # "para 15/03"
        r'\bprazo[:\s]+(.+?)(?=[,.\n]|$)',
        r'\bdeadline[:\s]+(.+?)(?=[,.\n]|$)',
        r'\bentregar?\s+(?:para|até)\s+(.+?)(?=[,.\n]|$)'
    ]
    
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            result["deadline"] = matches[0]
            break
    
    # =============================
    # 5. IDENTIFICAR AÇÕES E FOLLOW-UPS
    # =============================
    
    lines = text.split('\n')
    actions = []
    followups = []
    
    # Verbos de ação em português
    action_verbs = [
        "revisar", "analisar", "preparar", "entregar", "enviar", 
        "criar", "desenvolver", "implementar", "agendar", "concluir",
        "finalizar", "resolver", "verificar", "confirmar", "cobrar",
        "definir", "discutir", "apresentar", "compartilhar", "coordena",
        "gerenciar", "monitorar", "avaliar", "validar", "aprovar"
    ]
    
    for line in lines:
        line_stripped = line.strip()
        line_lower = line_stripped.lower()
        
        if not line_stripped:
            continue
            
        # Detecta ações (linhas que começam com verbo de ação)
        for verb in action_verbs:
            if line_lower.startswith(verb) or f" {verb} " in line_lower:
                actions.append(line_stripped)
                break
        
        # Detecta follow-ups (lista numerada ou com marcadores)
        if (re.match(r'^\d+[\.\)]\s+', line_stripped) or
            re.match(r'^[-•*➔›»]\s+', line_stripped) or
            'follow' in line_lower or 
            'seguir' in line_lower or
            'pendente' in line_lower):
            
            # Limpa marcadores
            clean_line = re.sub(r'^[\d\.\)\-\•\*\➔\›\»]\s+', '', line_stripped)
            if clean_line and len(clean_line) > 5:
                followups.append(clean_line)
    
    # Remove duplicatas
    actions = list(dict.fromkeys(actions))
    followups = list(dict.fromkeys(followups))
    
    result["actions"] = actions[:8]  # Limita a 8 ações
    result["followups"] = followups[:10]  # Limita a 10 follow-ups
    
    # =============================
    # 6. IDENTIFICAR RITOS
    # =============================
    
    ritual_keywords = [
        "daily", "weekly", "sprint", "review", "retrospective",
        "planning", "standup", "reunião", "meeting", "workshop",
        "alinhamento", "checkpoint", "sync", "briefing", "debriefing"
    ]
    
    for ritual in ritual_keywords:
        if ritual in text_lower:
            formatted = ritual.capitalize()
            if formatted not in result["rituals"]:
                result["rituals"].append(formatted)
    
    # =============================
    # 7. CALCULAR IMPACTO E COMPLEXIDADE
    # =============================
    
    word_count = len(text.split())
    has_numbers = bool(re.search(r'\d+', text))
    has_multiple_topics = len(result["hashtags"]) > 2
    has_multiple_actions = len(actions) > 3
    
    if word_count > 150 or has_numbers or has_multiple_topics or has_multiple_actions:
        result["impact"] = 8
        result["complexity"] = 7
    elif word_count > 50:
        result["impact"] = 6
        result["complexity"] = 5
    else:
        result["impact"] = 4
        result["complexity"] = 3
    
    # =============================
    # 8. CRIAR RESUMO ESTRUTURADO
    # =============================
    
    if word_count > 30:
        # Pega as primeiras palavras para o resumo
        words = text.split()[:20]
        result["structured_summary"] = " ".join(words) + "..."
    else:
        result["structured_summary"] = text
    
    # =============================
    # 9. IDENTIFICAR RISCOS (se mencionados)
    # =============================
    
    risk_keywords = ["risco", "problema", "dificuldade", "obstáculo", "desafio", "preocupação"]
    for keyword in risk_keywords:
        if keyword in text_lower:
            # Procura frase contendo a palavra risco
            risk_pattern = rf'[^.]*?{keyword}[^.]*\.'
            risk_matches = re.findall(risk_pattern, text, re.IGNORECASE)
            if risk_matches:
                result["risks"].extend([match.strip() for match in risk_matches[:3]])
    
    # =============================
    # 10. IDENTIFICAR DECISÕES
    # =============================
    
    decision_keywords = ["decisão", "decidir", "aprovar", "autorizar", "determinar"]
    for keyword in decision_keywords:
        if keyword in text_lower:
            decision_pattern = rf'[^.]*?{keyword}[^.]*\.'
            decision_matches = re.findall(decision_pattern, text, re.IGNORECASE)
            if decision_matches:
                result["decisions"].extend([match.strip() for match in decision_matches[:3]])
    
    # =============================
    # 11. LIMPAR DUPLICATAS
    # =============================
    
    result["hashtags"] = list(dict.fromkeys(result["hashtags"]))
    result["directors"] = list(dict.fromkeys(result["directors"]))
    result["actions"] = list(dict.fromkeys(result["actions"]))
    result["followups"] = list(dict.fromkeys(result["followups"]))
    
    # =============================
    # 12. LOG PARA DEBUG
    # =============================
    
    print(f"🔍 [AI_SERVICE] Análise executiva concluída:")
    print(f"   - Hashtags: {result['hashtags']}")
    print(f"   - Prioridade: {result['priority']}")
    print(f"   - Deadline: {result['deadline']}")
    print(f"   - Orçamento: {result['budget_impact']}")
    print(f"   - Ações: {len(result['actions'])}")
    print(f"   - Follow-ups: {len(result['followups'])}")
    
    return result


# 🔥 FUNÇÃO DE TESTE (opcional)
def test_executive_analysis():
    """Função para testar a análise executiva localmente"""
    test_cases = [
        "Revisar contrato urgente até sexta-feira, valor R$ 100.000",
        "Desenvolver nova feature do sistema até 30/03, equipe de Tecnologia",
        "Reunião de alinhamento com equipe comercial amanhã às 10h",
        "Analisar proposta de investimento de R$ 500.000 para novo projeto",
        "1. Revisar relatório financeiro\n2. Agendar reunião com diretoria\n3. Finalizar proposta",
    ]
    
    print("🧪 TESTANDO ANÁLISE EXECUTIVA:")
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*50}")
        print(f"TESTE {i}: {test}")
        print(f"{'='*50}")
        result = analyze_executive_text(test)
        print(f"Hashtags: {result['hashtags']}")
        print(f"Prioridade: {result['priority']}")
        print(f"Deadline: {result['deadline']}")
        print(f"Orçamento: {result['budget_impact']}")
        print(f"Ações: {result['actions'][:2]}")
    
    return True