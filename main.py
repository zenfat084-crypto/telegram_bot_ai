import os
import telebot
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID"))   # ID مدير البوت

bot = telebot.TeleBot(TOKEN)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

users = set()

# تسجيل المستخدمين
@bot.message_handler(commands=["start"])
def start(msg):
    users.add(msg.chat.id)

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🤖 دردشة الذكاء الاصطناعي", callback_data="ai_chat"))
    kb.add(InlineKeyboardButton("📢 نشر إعلان", callback_data="send_ad"))

    bot.send_message(
        msg.chat.id,
        "مرحبًا! اختر إحدى الخيارات:",
        reply_markup=kb
    )


# اختيار الزر
@bot.callback_query_handler(func=lambda c: True)
def handle_buttons(call):
    if call.data == "ai_chat":
        msg = bot.send_message(call.message.chat.id, "ارسل رسالتك للذكاء الاصطناعي:")
        bot.register_next_step_handler(msg, ai_reply)

    elif call.data == "send_ad":
        if call.from_user.id != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ ليس لديك صلاحية.", show_alert=True)
            return

        msg = bot.send_message(call.message.chat.id, "اكتب نص الإعلان:")
        bot.register_next_step_handler(msg, send_ad_to_all)


# ذكاء اصطناعي Groq LLaMA 3
def ai_reply(msg):
    prompt = msg.text

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    res = requests.post(GROQ_URL, json=data, headers=headers).json()

    reply = res["choices"][0]["message"]["content"]

    bot.send_message(msg.chat.id, reply)


# نشر الإعلانات
def send_ad_to_all(msg):
    ad = msg.text
    count = 0

    for user in list(users):
        try:
            bot.send_message(user, ad)
            count += 1
        except:
            pass

    bot.send_message(msg.chat.id, f"تم إرسال الإعلان إلى {count} مستخدم.")


bot.infinity_polling()
