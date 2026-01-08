import os
import asyncio
import logging
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from groq import Groq

# سيرفر وهمي لـ Render
app = Flask('')
@app.route('/')
def home(): return "Bot is Alive!"
def run_web_server(): app.run(host='0.0.0.0', port=8080)

# الإعدادات
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
client = Groq(api_key=GROQ_API_KEY)

# دالة ذكاء اصطناعي مطورة تأخذ "النوع" بعين الاعتبار
def get_ai_response(user_input, content_type="General"):
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": f"You are 'ViralMind Pro'. Style: {content_type}. Provide 3 Hooks, a Viral Script, and Visual cues. Language: User's language."},
                {"role": "user", "content": user_input}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# رسالة البداية مع الأزرار
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎥 TikTok Script", callback_data='TikTok'),
         InlineKeyboardButton("🎬 Instagram Reels", callback_data='Reels')],
        [InlineKeyboardButton("📺 YouTube Idea", callback_data='YouTube')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🚀 Welcome to ViralMind Pro!\nChoose your content type:", reply_markup=reply_markup)

# التعامل مع ضغطات الأزرار
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['type'] = query.data
    await query.edit_message_text(text=f"✅ Selected: {query.data}\nNow, tell me your video topic!")

# معالجة الرسائل
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    content_type = context.user_data.get('type', 'General')
    
    await update.message.reply_text(f"🧠 Crafting a viral {content_type} script for you...")
    
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, get_ai_response, user_text, content_type)
    await update.message.reply_text(response)

if __name__ == '__main__':
    Thread(target=run_web_server).start()
    
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    application.run_polling(drop_pending_updates=True)
