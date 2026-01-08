import os
import asyncio
import logging
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from groq import Groq

# 1. إعداد سيرفر وهمي لـ Render
app = Flask('')

@app.route('/')
def home():
    return "Bot is Alive!"

def run_web_server():
    app.run(host='0.0.0.0', port=8080)

# 2. إعدادات البوت الأساسية
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
client = Groq(api_key=GROQ_API_KEY)

def get_ai_response(user_input):
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are 'ViralMind Pro'. Create viral scripts. Response in user language."},
                {"role": "user", "content": user_input}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_text("🧠 Crafting your viral script...")
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, get_ai_response, user_text)
    await update.message.reply_text(response)

# 3. تشغيل البوت والسيرفر معاً
if __name__ == '__main__':
    # تشغيل السيرفر الوهمي في خيط منفصل
    t = Thread(target=run_web_server)
    t.start()
    
    # تشغيل البوت
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot & Web Server are starting...")
    application.run_polling(drop_pending_updates=True)
