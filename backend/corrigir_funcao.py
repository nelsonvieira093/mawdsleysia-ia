import re

with open('api/routes/chat.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Substitui toda a fun√ß√£o format_followup_response por uma vers√£o simplificada
nova_funcao = '''def format_followup_response(followups: List[FollowUp]) -> str:
    """Formata followups para resposta amig√°vel - VERS√ÉO CORRIGIDA"""
    if not followups:
        return "Ì≥≠ Voc√™ n√£o possui follow-ups pendentes no momento."

    response = "Ì≥ã **Seus follow-ups pendentes:**\\n\\n"

    for i, fup in enumerate(followups, 1):
        # Informa√ß√µes b√°sicas
        description = fup.description or "Sem descri√ß√£o"
        title = description[:50] + "..." if len(description) > 50 else description
        status = fup.status or "PENDENTE"

        # Data de vencimento
        due_info = ""
        if fup.due_date:
            due_date = fup.due_date.strftime('%d/%m/%Y')
            due_info = f" | Ì≥Ö Vence: {due_date}"

        # Respons√°vel (verifica se o atributo existe)
        owner = ""
        if hasattr(fup, 'owner_name') and fup.owner_name:
            owner = f" | Ì±§ {fup.owner_name}"
        elif hasattr(fup, 'owner') and fup.owner:
            owner = f" | Ì±§ {fup.owner}"

        response += f"{i}. **{title}**\\n"
        response += f"   Ì≥å Status: {status}{due_info}{owner}\\n"

        # Adiciona linha em branco entre itens
        if i < len(followups):
            response += "\\n"

    # Estat√≠sticas
    total = len(followups)

    response += f"\\n---\\n"
    response += f"Ì≥ä **Resumo:** {total} follow-up(s)"

    return response'''

# Encontra e substitui a fun√ß√£o antiga
pattern = r'def format_followup_response\(followups: List\[FollowUp\]\) -> str:.*?return response'
content = re.sub(pattern, nova_funcao, content, flags=re.DOTALL)

with open('api/routes/chat.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('‚úÖ Fun√ß√£o format_followup_response corrigida')
