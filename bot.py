import os
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import openai

# جلب المفاتيح من متغيرات البيئة
openai.api_key = os.getenv("OPENAI_API_KEY")
telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=telegram_token)

# URL البوت على Railway (ستحصل عليه بعد نشر المشروع)
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # مثال: https://project-name.up.railway.app/

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحبًا! أرسل لي نص أو 'صورة <الوصف>' لإنشاء صورة.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    if user_message.lower().startswith("صورة "):
        prompt = user_message[6:]
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512"
        )
        image_url = response['data'][0]['url']
        await update.message.reply_photo(photo=image_url)
    else:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_message}]
        )
        reply = response['choices'][0]['message']['content']
        await update.message.reply_text(reply)

# إعداد التطبيق
app = ApplicationBuilder().token(telegram_token).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# تفعيل Webhook
app.run_webhook(
    listen="0.0.0.0",
    port=int(os.environ.get("PORT", 3000)),
    webhook_url=WEBHOOK_URL
)
