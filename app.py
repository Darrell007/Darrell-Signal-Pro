from flask import Flask, request
import requests

TOKEN = "7281967575:AAHCXsMmKwiGNNEBvRxCj30LBzfi2TrMnL0"
app = Flask(__name__)

@app.route(f'/{TOKEN}', methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        message = data["message"].get("text", "")

        if message.lower() == "/start":
            send_message(chat_id, "✅ Welcome to Darrell Signal Bot. You'll receive crypto signals here.")
        else:
            send_message(chat_id, "👋 Got your message. Auto-signals will come soon!")

    return {"ok": True}

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

@app.route('/')
def home():
    return "Darrell Signal Bot is running."

if __name__ == "__main__":
    app.run()


 
