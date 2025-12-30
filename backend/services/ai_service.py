class AIService: pass


ACTION_VERBS = [
    "cobrar","verificar","confirmar","resolver",
    "mandar","checar","definir","analisar"
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
