# backend/controllers/agenda.py

from datetime import datetime, timedelta

# Templates simples por rito (expanda depois)
RITUAL_TEMPLATES = {
    "ONE_ON_ONE_ELSA": {
        "title": "Pauta One-on-One – Elsa",
        "sections": [
            "Follow-ups abertos",
            "Projetos / Temas regulatórios",
            "Riscos e dependências",
            "Decisões e próximos passos"
        ]
    },
    "STAFF_MEETING": {
        "title": "Pauta Staff Meeting",
        "sections": [
            "Indicadores críticos",
            "Travas interdepartamentais",
            "Follow-ups transversais",
            "Decisões executivas"
        ]
    }
}

def build_agenda(ritual_code: str):
    template = RITUAL_TEMPLATES.get(ritual_code)

    if not template:
        return {
            "ritual": ritual_code,
            "error": "Rito não encontrado"
        }

    # 🔹 MOCKS (trocar por DB depois)
    followups = [
        {
            "description": "Cobrar atualização do shelf life do WILLENTINE",
            "owner": "Elsa",
            "status": "ABERTO",
            "due_date": (datetime.now() + timedelta(days=7)).date().isoformat()
        }
    ]

    notes = [
        {
            "content": "Tema recorrente sobre estabilidade de 36 meses",
            "created_at": datetime.now().isoformat()
        }
    ]

    return {
        "ritual": ritual_code,
        "agenda": {
            "title": template["title"],
            "sections": {
                "Follow-ups abertos": followups,
                "Notas recentes": notes
            }
        }
    }
