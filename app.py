from flask import Flask, request
import requests

app = Flask(__name__)
TOKEN = '7281967575:AAHCXsMmKwiGNNEBvRxCj30LBzfi2TrMnL0'
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"

# Home route just for testing Render
@app.route('/')
def home():
    return '✅ Darrell Signal Bot is live!'

# Telegram webhook route
@app.route(f'/{TOKEN}', methods=['POST'])
def receive_update():
    data = request.get_json()

    # Check if message exists and has text
    if 'message' in data:
        chat_id = data['message']['chat']['id']
        message_text = data['message'].get('text', '')

        if message_text == '/start':
            welcome_msg = (
                "👋 Welcome to *Darrell Signal Bot*!\n\n"
                "📈 You'll start receiving automated scalping signals for:\n"
                "– Bitcoin (BTC/USD)\n"
                "– Ethereum (ETH/USD)\n"
                "– Gold (XAU/USD)\n\n"
                "🕒 Signals come Mon–Sat at:\n• 9:00–11:30 AM GMT\n• 1:30–4:30 PM GMT"
            )
            send_message(chat_id, welcome_msg)

    return 'OK'

def send_message(chat_id, text):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)

if __name__ == '__main__':
    app.run(debug=True)
@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()

    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")

        # Manual trigger for signal
        if text.startswith("/signal"):
            parts = text.split()
            if len(parts) == 3:
                asset, action = parts[1], parts[2]
                message = f"📡 Manual Signal\nAsset: {asset}\nAction: {action.upper()}"
                log_signal(asset, action, source="manual")
                send_message(chat_id, message)
            else:
                send_message(chat_id, "Usage: /signal BTC/USD BUY")
    
    return "OK"



 
