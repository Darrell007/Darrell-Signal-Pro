import requests
TOKEN = "7281967575:AAHCXsMmKwiGNNEBvRxCj30LBzfi2TrMnL0"
URL = f"https://darrell-scalp-bot.onrender.com/{TOKEN}"
res = requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={URL}")
print(res.json())
