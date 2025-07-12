import telebot
from telebot import types
from flask import Flask, request
import requests

API_TOKEN = '8048451154:AAGqceEivEO6hlKWCCd4zMLgEfzcb3NrHvU'
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# קישורים מוכנים
CHECKIN_URL = 'https://script.google.com/macros/s/AKfycby2ZE8X-betb6lrAuD-NkNIcbnbVMwJki3evRoqjCqCoGaYjuSST-hu9Ihm6juBxSd3/exec?action=MAT%20Check%20in'
CHECKOUT_URL = 'https://script.google.com/macros/s/AKfycby2ZE8X-betb6lrAuD-NkNIcbnbVMwJki3evRoqjCqCoGaYjuSST-hu9Ihm6juBxSd3/exec?action=MAT%20Check%20out'
WHO_IS_INSIDE_URL = 'https://script.google.com/macros/s/AKfycbwQ2QwoI8k6cpR8zuJlZdho9fyBo-XMjkkfmmFKfy70s5FS-Q31U9cjPicc3jVgqwI-/exec?action=who'

FLOORS = {
    "OP.F": "https://script.google.com/macros/s/AKfycbze-hLTCCDCIfg8uBFAWJK9tz9KUB7aGHc-5Nt4XB7pmVqQiMv-TaDOi219Of8b1-Ca/exec?floor=OP.F",
    "GEN.F": "https://script.google.com/macros/s/AKfycbze-hLTCCDCIfg8uBFAWJK9tz9KUB7aGHc-5Nt4XB7pmVqQiMv-TaDOi219Of8b1-Ca/exec?floor=GEN.F",
    "TU.F": "https://script.google.com/macros/s/AKfycbze-hLTCCDCIfg8uBFAWJK9tz9KUB7aGHc-5Nt4XB7pmVqQiMv-TaDOi219Of8b1-Ca/exec?floor=TU.F",
    "MIV.F": "https://script.google.com/macros/s/AKfycbze-hLTCCDCIfg8uBFAWJK9tz9KUB7aGHc-5Nt4XB7pmVqQiMv-TaDOi219Of8b1-Ca/exec?floor=MIV.F"
}

# תפריט ראשי
def send_main_menu(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("✅ כניסה למנהרה", url=CHECKIN_URL),
        types.InlineKeyboardButton("🚪 יציאה מהמנהרה", url=CHECKOUT_URL)
    )
    markup.add(types.InlineKeyboardButton("👀 מי נמצא במנהרה?", callback_data='who_is_inside'))

    for name, url in FLOORS.items():
        markup.add(types.InlineKeyboardButton(f"📍 קומה {name}", url=url))

    bot.send_message(chat_id, "בחר פעולה:", reply_markup=markup)

# התחלה
@bot.message_handler(commands=['start'])
def send_welcome(message):
    send_main_menu(message.chat.id)

# לחצני callback
@bot.callback_query_handler(func=lambda call: call.data == 'who_is_inside')
def handle_who_is_inside(call):
    try:
        response = requests.get(WHO_IS_INSIDE_URL)
        if response.status_code == 200:
            text = response.text.strip()
            if not text or "אין רישום" in text:
                bot.send_message(call.message.chat.id, "אין רישום של עובדים שנמצאים במנהרה")
                return

            lines = [line.strip() for line in text.splitlines() if line.strip()]
            cleaned_lines = []
            for line in lines:
                if "|" in line:
                    parts = line.split("|")
                    email = parts[0].strip()
                    datetime = parts[1].strip().split("GMT")[0].strip()
                    duration = parts[2].strip() if len(parts) > 2 else ""
                    cleaned_lines.append(f"{email} | {datetime} | {duration}")

            final_text = "\n".join(cleaned_lines)
            bot.send_message(call.message.chat.id, final_text or "אין רישום של עובדים במנהרה.")
        else:
            bot.send_message(call.message.chat.id, "שגיאה בעת בקשת הנתונים.")
    except Exception as e:
        bot.send_message(call.message.chat.id, f"שגיאה פנימית: {str(e)}")

# Flask endpoint (לנתיב עם הטוקן)
@app.route(f"/{API_TOKEN}", methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    return 'Invalid request', 400

# בדיקה ראשונית
@app.route('/', methods=['GET'])
def index():
    return 'Bot is running!'

# הפעלת Flask
if __name__ == '__main__':
    app.run(debug=False, port=10000)
