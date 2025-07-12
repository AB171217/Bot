import telebot
import requests
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from flask import Flask, request

API_TOKEN = '8048451154:AAGqceEivEO6hlKWCCd4zMLgEfzcb3NrHvU'
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# ✅ קישורים מוכנים
CHECKIN_URL = "https://script.google.com/macros/s/AKfycby2ZE8X-betb6lrAuD-NkNIcbnbVMwJki3evRoqjCqCoGaYjuSST-hu9Ihm6juBxSd3/exec?action=MAT%20Check%20in"
CHECKOUT_URL = "https://script.google.com/macros/s/AKfycby2ZE8X-betb6lrAuD-NkNIcbnbVMwJki3evRoqjCqCoGaYjuSST-hu9Ihm6juBxSd3/exec?action=MAT%20Check%20out"
WHO_IS_INSIDE_URL = "https://script.google.com/macros/s/AKfycbwQ2QwoI8k6cpR8zuJlZdho9fyBo-XMjkkfmmFKfy70s5FS-Q31U9cjPicc3jVgqwI-/exec?action=who"

FLOOR_LINKS = {
    "🏗 קומה OP.F": "https://script.google.com/macros/s/AKfycbze-hLTCCDCIfg8uBFAWJK9tz9KUB7aGHc-5Nt4XB7pmVqQiMv-TaDOi219Of8b1-Ca/exec?floor=OP.F",
    "⚙️ קומה GEN.F": "https://script.google.com/macros/s/AKfycbze-hLTCCDCIfg8uBFAWJK9tz9KUB7aGHc-5Nt4XB7pmVqQiMv-TaDOi219Of8b1-Ca/exec?floor=GEN.F",
    "🚇 קומה TU.F": "https://script.google.com/macros/s/AKfycbze-hLTCCDCIfg8uBFAWJK9tz9KUB7aGHc-5Nt4XB7pmVqQiMv-TaDOi219Of8b1-Ca/exec?floor=TU.F",
    "🧱 קומה MIV.F": "https://script.google.com/macros/s/AKfycbze-hLTCCDCIfg8uBFAWJK9tz9KUB7aGHc-5Nt4XB7pmVqQiMv-TaDOi219Of8b1-Ca/exec?floor=MIV.F",
}

# ✅ תפריט ראשי
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.row(
    KeyboardButton("✅ כניסה למנהרה"),
    KeyboardButton("🚪 יציאה מהמנהרה")
)
main_menu.row(
    KeyboardButton("📋 מי נמצא במנהרה?")
)
main_menu.row(
    KeyboardButton("🏗 קומה OP.F"),
    KeyboardButton("⚙️ קומה GEN.F")
)
main_menu.row(
    KeyboardButton("🚇 קומה TU.F"),
    KeyboardButton("🧱 קומה MIV.F")
)

# ✅ קבלת פקודות מהמשתמש
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "בחר פעולה:", reply_markup=main_menu)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text

    if text == "✅ כניסה למנהרה":
        bot.send_message(message.chat.id, f"🔄 פותח קישור לכניסה:\n{CHECKIN_URL}")
    elif text == "🚪 יציאה מהמנהרה":
        bot.send_message(message.chat.id, f"🔄 פותח קישור ליציאה:\n{CHECKOUT_URL}")
    elif text == "📋 מי נמצא במנהרה?":
        try:
            response = requests.get(WHO_IS_INSIDE_URL)
            response.raise_for_status()
            cleaned = clean_response(response.text)
            bot.send_message(message.chat.id, cleaned or "אין רישום של עובדים שנמצאים במנהרה")
        except Exception as e:
            bot.send_message(message.chat.id, f"שגיאה: {str(e)}")
    elif text in FLOOR_LINKS:
        bot.send_message(message.chat.id, f"🔄 קישור עבור {text}:\n{FLOOR_LINKS[text]}")
    else:
        bot.send_message(message.chat.id, "לא זיהיתי את הפעולה. אנא בחר מהתפריט:", reply_markup=main_menu)

# ✅ ניקוי תגובת Google Script
def clean_response(raw_text):
    lines = raw_text.strip().split('\n')
    cleaned = []
    for line in lines:
        if not line.strip():
            continue
        parts = line.split('|')
        if len(parts) != 3:
            continue
        email = parts[0].strip()
        date_str = parts[1].strip()
        duration = parts[2].strip()

        # שמירה רק על תאריך ושעה בלי אזור זמן
        if "GMT" in date_str:
            date_str = date_str.split("GMT")[0].strip()

        cleaned.append(f"{email} | {date_str} | {duration}")
    return "\n".join(cleaned)

# ✅ Flask Webhook
@app.route('/', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        return 'OK'

# ✅ נקודת התחלה
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
