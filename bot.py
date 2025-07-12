import os
import telebot
import requests
from flask import Flask, request

# טוקן מה-@BotFather
TOKEN = "8048451154:AAGqceEivEO6hlKWCCd4zMLgEfzcb3NrHvU"
bot = telebot.TeleBot(TOKEN)

# URL שמחזיר את רשימת העובדים במנהרה
WHO_IS_INSIDE_URL = "https://script.google.com/macros/s/AKfycbwQ2QwoI8k6cpR8zuJlZdho9fyBo-XMjkkfmmFKfy70s5FS-Q31U9cjPicc3jVgqwI-/exec?action=who"

# קישורים לכל קומה
FLOOR_LINKS = {
    "OP.F": "https://script.google.com/macros/s/AKfycbze-hLTCCDCIfg8uBFAWJK9tz9KUB7aGHc-5Nt4XB7pmVqQiMv-TaDOi219Of8b1-Ca/exec?floor=OP.F",
    "GEN.F": "https://script.google.com/macros/s/AKfycbze-hLTCCDCIfg8uBFAWJK9tz9KUB7aGHc-5Nt4XB7pmVqQiMv-TaDOi219Of8b1-Ca/exec?floor=GEN.F",
    "TU.F": "https://script.google.com/macros/s/AKfycbze-hLTCCDCIfg8uBFAWJK9tz9KUB7aGHc-5Nt4XB7pmVqQiMv-TaDOi219Of8b1-Ca/exec?floor=TU.F",
    "MIV.F": "https://script.google.com/macros/s/AKfycbze-hLTCCDCIfg8uBFAWJK9tz9KUB7aGHc-5Nt4XB7pmVqQiMv-TaDOi219Of8b1-Ca/exec?floor=MIV.F"
}

# קישור לגיליון
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1SEdIG0scZEEtKOfvHuKrO7A3Uq2-1B7eKUtI7v3cKZs/edit?usp=sharing"

# תפריט אינליין
def send_main_menu(chat_id):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("☑️ כניסה למנהרה", url="https://script.google.com/macros/s/AKfycby2ZE8X-betb6lrAuD-NkNIcbnbVMwJki3evRoqjCqCoGaYjuSST-hu9Ihm6juBxSd3/exec?action=MAT%20Check%20in"),
        telebot.types.InlineKeyboardButton("✅ יציאה מהמנהרה", url="https://script.google.com/macros/s/AKfycby2ZE8X-betb6lrAuD-NkNIcbnbVMwJki3evRoqjCqCoGaYjuSST-hu9Ihm6juBxSd3/exec?action=MAT%20Check%20out"),
    )
    markup.add(telebot.types.InlineKeyboardButton("👀 מי נמצא במנהרה?", callback_data="who_is_inside"))
    for floor_name, url in FLOOR_LINKS.items():
        markup.add(telebot.types.InlineKeyboardButton(f"📍 קומה {floor_name}", url=url))
    bot.send_message(chat_id, "בחר פעולה:", reply_markup=markup)

# תפריט נעוץ למטה
def send_reply_keyboard(chat_id):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.row("📊 טבלת מעקב")
    bot.send_message(chat_id, "בחר פעולה נוספת או שלח פקודה", reply_markup=markup)

# התחלה
@bot.message_handler(commands=['start'])
def handle_start(message):
    send_main_menu(message.chat.id)
    send_reply_keyboard(message.chat.id)

# לחיצה על כפתור "מי נמצא במנהרה?"
@bot.callback_query_handler(func=lambda call: call.data == "who_is_inside")
def handle_who_is_inside(call):
    try:
        res = requests.get(WHO_IS_INSIDE_URL)
        data = res.text.strip()

        if not data or "אין רישום" in data:
            bot.send_message(call.message.chat.id, "אין רישום של עובדים שנמצאים במנהרה.")
        else:
            lines = data.splitlines()
            output = ""
            for line in lines:
                parts = line.split("|")
                if len(parts) >= 3:
                    name = parts[0].strip()
                    time = parts[1].split(" GMT")[0].strip()
                    duration = parts[2].strip()
                    output += f"{name} - {time} ({duration})\n"

            bot.send_message(call.message.chat.id, output or "לא נמצאו עובדים.")
    except Exception as e:
        bot.send_message(call.message.chat.id, f"שגיאה: {e}")

    send_main_menu(call.message.chat.id)
    send_reply_keyboard(call.message.chat.id)

# לחיצה על כפתור "📊 טבלת מעקב"
@bot.message_handler(func=lambda msg: msg.text == "📊 טבלת מעקב")
def handle_sheet_button(message):
    bot.send_message(message.chat.id, GOOGLE_SHEET_URL)

# Flask setup
app = Flask(__name__)

@app.route(f"/{TOKEN}", methods=['POST'])
def telegram_webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "OK", 200

@app.route("/", methods=['GET'])
def index():
    return "Bot is running!", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
