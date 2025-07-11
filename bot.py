import telebot
import requests

BOT_TOKEN = "8048451154:AAGqceEivEO6hlKWCCd4zMLgEfzcb3NrHvU"
bot = telebot.TeleBot(BOT_TOKEN)

# קישורים לפעולות
CHECKIN_URL = "https://script.google.com/macros/s/AKfycby2ZE8X-betb6lrAuD-NkNIcbnbVMwJki3evRoqjCqCoGaYjuSST-hu9Ihm6juBxSd3/exec?action=MAT%20Check%20in"
CHECKOUT_URL = "https://script.google.com/macros/s/AKfycby2ZE8X-betb6lrAuD-NkNIcbnbVMwJki3evRoqjCqCoGaYjuSST-hu9Ihm6juBxSd3/exec?action=MAT%20Check%20out"
WHO_IS_INSIDE_URL = "https://script.google.com/macros/s/AKfycby2ZE8X-betb6lrAuD-NkNIcbnbVMwJki3evRoqjCqCoGaYjuSST-hu9Ihm6juBxSd3/exec?action=who"

FLOOR_URLS = {
    "OP.F": "https://script.google.com/macros/s/AKfycbze-hLTCCDCIfg8uBFAWJK9tz9KUB7aGHc-5Nt4XB7pmVqQiMv-TaDOi219Of8b1-Ca/exec?floor=OP.F",
    "GEN.F": "https://script.google.com/macros/s/AKfycbze-hLTCCDCIfg8uBFAWJK9tz9KUB7aGHc-5Nt4XB7pmVqQiMv-TaDOi219Of8b1-Ca/exec?floor=GEN.F",
    "TU.F":  "https://script.google.com/macros/s/AKfycbze-hLTCCDCIfg8uBFAWJK9tz9KUB7aGHc-5Nt4XB7pmVqQiMv-TaDOi219Of8b1-Ca/exec?floor=TU.F",
    "MIV.F": "https://script.google.com/macros/s/AKfycbze-hLTCCDCIfg8uBFAWJK9tz9KUB7aGHc-5Nt4XB7pmVqQiMv-TaDOi219Of8b1-Ca/exec?floor=MIV.F",
}

@bot.message_handler(commands=['start'])
def send_menu(message):
    markup = telebot.types.InlineKeyboardMarkup()

    markup.row(
        telebot.types.InlineKeyboardButton("✅ כניסה למנהרה", url=CHECKIN_URL),
        telebot.types.InlineKeyboardButton("❌ יציאה מהמנהרה", url=CHECKOUT_URL)
    )

    markup.add(
        telebot.types.InlineKeyboardButton("📋 מי נמצא במנהרה?", callback_data="who_inside")
    )

    row = []
    for floor, url in FLOOR_URLS.items():
        row.append(telebot.types.InlineKeyboardButton(f"🔹 {floor}", url=url))
    markup.add(*row[:2])
    markup.add(*row[2:])

    bot.send_message(message.chat.id, "שלום! בחר פעולה:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "who_inside":
        try:
            response = requests.get(WHO_IS_INSIDE_URL)
            if response.status_code == 200:
                data = response.text.strip()
                if not data:
                    bot.send_message(call.message.chat.id, "🔍 אף אחד לא נמצא כרגע במנהרה.")
                else:
                    bot.send_message(call.message.chat.id, "📋 עובדים במנהרה כרגע:\n\n" + data)
            else:
                bot.send_message(call.message.chat.id, "שגיאה בשליפת הנתונים מהגיליון.")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"שגיאה: {str(e)}")

bot.infinity_polling()
