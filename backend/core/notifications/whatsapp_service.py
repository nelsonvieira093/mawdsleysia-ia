# E:\MAWDSLEYS-AGENTE\backend\core\notifications\whatsapp_service.py

import os
import requests

class WhatsAppService:
    def __init__(self):
        self.api_key = os.getenv("ZENVIA_API_KEY")
        self.channel = os.getenv("ZENVIA_CHANNEL_ID")
        self.base_url = "https://api.zenvia.com/v2/channels/whatsapp/messages"

        if not self.api_key or not self.channel:
            raise RuntimeError("Zenvia não configurado corretamente")

    def send_alert(self, phone: str, message: str):
        payload = {
            "from": self.channel,
            "to": phone,
            "contents": [
                {
                    "type": "text",
                    "text": message
                }
            ]
        }

        headers = {
            "X-API-TOKEN": self.api_key,
            "Content-Type": "application/json"
        }

        response = requests.post(
            self.base_url,
            json=payload,
            headers=headers,
            timeout=10
        )

        if response.status_code not in (200, 201, 202):
            raise RuntimeError(
                f"Erro Zenvia WhatsApp: {response.status_code} - {response.text}"
            )

        print(f"[WhatsAppService] 📲 Mensagem enviada para {phone}")
