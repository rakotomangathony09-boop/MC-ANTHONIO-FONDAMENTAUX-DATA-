import requests
import os

def send_briefing():
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("CHAT_ID")
    if not token or not chat_id:
        return print("Erreur : Clés manquantes.")
    
    msg = "🏛️ **SYSTEM CHECK : OPERATIONAL**\n👤 Michel Anthonio\n✅ Terminal en ligne sur Render."
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"})

if __name__ == "__main__":
    send_briefing()
