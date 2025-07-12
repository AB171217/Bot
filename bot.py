import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import requests
from flask import Flask, request

# === הגדרות ===
TOKEN = "8048451154:AAGqceEivEO6hlKWCCd4zMLgEfzcb3NrHvU"
bot = telebot.TeleBot(TOKEN)

# קישורים מוכנים מראש
CHECKIN_URL = "https://script.google.com/macros/s/AKfycby2ZE8X-betb6lrAuD-NkNIcbnbVMwJki3evRoqjCqCoGaYjuSST-hu9Ihm6juBxSd3/exec?action=MAT%20Check%20in"
CHECKOUT_URL = "https://script.google.com/macros/s/AKfycby2ZE8X-betb6lrAuD-NkNIcbnbVMwJki3evRoqjCqCoGaYjuSST-hu9Ihm6juBxSd3/exec?action=MAT%20Check%20out"
WHO_IS_INSIDE_URL = "https://script.google.com/macros/s/AKfycby2ZE8X-betb6lrAuD-NkNIcbnbVMwJki3evRoqjCqCoGaYjuSST-hu9Ihm6juBxSd3/exec?action=who"

# === תפריט ראשי ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(
        KeyboardButton("✅ כניסה למנהרה"),
        KeyboardButton("🚪 יציאה מהמנהרה")
    )
    markup.row(
        KeyboardButton("📋 מי נמצא במנהרה?")
    )
    bot.send_message(message.chat.id, "ברוך הבא! בחר פעולה:", reply_markup=markup)

# === כפתור כניסה ===
@bot.message_handler(func=lambda message: message.text == "✅ כניסה למנהרה")
def handle_checkin(message):
    try:
        response = requests.get(CHECKIN_URL)
        bot.send_message(message.chat.id, response.text)
    except Exception as e:
        bot.send_message(message.chat.id, f"שגיאה פנימית:\n{str(e)}")

# === כפתור יציאה ===
@bot.message_handler(func=lambda message: message.text == "🚪 יציאה מהמנהרה")
def handle_checkout(message):
    try:
        response = requests.get(CHECKOUT_URL)
        bot.send_message(message.chat.id, response.text)
    except Exception as e:
        bot.send_message(message.chat.id, f"שגיאה פנימית:\n{str(e)}")

# === כפתור מי נמצא במנהרה ===
@bot.message_handler(func=lambda message: message.text == "📋 מי נמצא במנהרה?")
def handle_who_inside(message):
    try:
        response = requests.get(WHO_IS_INSIDE_URL)
        if response.status_code == 200:
            text = response.text.strip()
            if not text:
                bot.send_message(message.chat.id, "אין רישום של עובדים שנמצאים במנהרה")
            elif len(text) > 4000:
                for i in range(0, len(text), 4000):
                    bot.send_message(message.chat.id, text[i:i+4000])
            else:
                bot.send_message(message.chat.id, text)
        else:
            bot.send_message(message.chat.id, f"שגיאה בטעינת המידע: {response.status_code}")
    except Exception as e:
        bot.send_message(message.chat.id, f"שגיאה פנימית:\n{str(e)}")

# === Flask (עבור render) ===
app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return 'Bot is running'

if __name__ == '__main__':
    import threading
    threading.Thread(target=bot.infinity_polling, name="bot").start()
    app.run(host="0.0.0.0", port=10000)
            
