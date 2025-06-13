import telebot
from flask import Flask, request
import requests
import os
import pandas as pd

# === Your Telegram Bot Token ===
BOT_TOKEN = "7281967575:AAHCXsMmKwiGNNEBvRxCj30LBzfi2TrMnL0"
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# === Function to fetch price data from Binance ===
def get_binance_data(symbol, interval="5m", limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    try:
        response = requests.get(url)
        data = response.json()
        df = pd.DataFrame(data, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "number_of_trades",
            "taker_buy_base", "taker_buy_quote", "ignore"
        ])
        df["close"] = df["close"].astype(float)
        return df
    except Exception as e:
        print("Error fetching data:", e)
        return None

# === Signal Decision Logic ===
def generate_signal(df):
    if df is None or len(df) < 50:
        return "❌ Not enough data to generate signal."

    df["EMA20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["close"].ewm(span=50, adjust=False).mean()
    df["RSI"] = compute_rsi(df["close"], 14)
    df["MACD"] = df["close"].ewm(span=12, adjust=False).mean() - df["close"].ewm(span=26, adjust=False).mean()

    latest = df.iloc[-1]

    if latest["EMA20"] > latest["EMA50"] and latest["RSI"] > 50 and latest["MACD"] > 0:
        return "📈 *BUY Signal!* (EMA20 > EMA50, RSI > 50, MACD > 0)"
    elif latest["EMA20"] < latest["EMA50"] and latest["RSI"] < 50 and latest["MACD"] < 0:
        return "📉 *SELL Signal!* (EMA20 < EMA50, RSI < 50, MACD < 0)"
    else:
        return "⚖️ *No Clear Signal* (Indicators not aligned)"

# === RSI Calculation ===
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# === Webhook Listener ===
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/")
def index():
    return "🚀 DarrellScalpBot is running!"

# === /start Command ===
@bot.message_handler(commands=["start"])
def welcome(message):
    bot.reply_to(message, "👋 Welcome to DarrellScalpBot! Use /btc, /eth, or /xau to get instant scalping signals.")

# === /testsignal Command ===
@bot.message_handler(commands=["testsignal"])
def send_test_signal(message):
    test_message = (
        "📊 *Test Signal Alert!*\n"
        "Asset: BTC/USD\n"
        "Signal: *BUY*\n"
        "Entry: 67,200\n"
        "Target: 67,550\n"
        "Stop Loss: 66,950\n"
        "_[This is a test signal]_"
    )
    bot.send_message(message.chat.id, test_message, parse_mode='Markdown')

# === Signal Commands (/btc, /eth, /xau) ===
@bot.message_handler(commands=["btc"])
def btc_signal(message):
    df = get_binance_data("BTCUSDT")
    signal = generate_signal(df)
    bot.send_message(message.chat.id, f"🪙 BTC/USD Signal:\n{signal}", parse_mode='Markdown')

@bot.message_handler(commands=["eth"])
def eth_signal(message):
    df = get_binance_data("ETHUSDT")
    signal = generate_signal(df)
    bot.send_message(message.chat.id, f"🪙 ETH/USD Signal:\n{signal}", parse_mode='Markdown')

@bot.message_handler(commands=["xau"])
def xau_signal(message):
    # Binance doesn't have XAU, so you need an alternate data source.
    # For now, return placeholder.
    bot.send_message(message.chat.id, "⛏️ Gold (XAU/USD) not supported yet via Binance. Coming soon!")

# === Set Webhook on Render ===
if __name__ == "__main__":
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{BOT_TOKEN}"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))




 
