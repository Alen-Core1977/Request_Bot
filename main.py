import os
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7306973574  # ← замени на свой Telegram ID

NAME, PHONE, REQUEST = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome!\nTo submit a request, type /apply"
    )

async def apply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👤 What is your name?")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("📞 Please enter your phone number:")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    if not phone.replace("+", "").isdigit():
        await update.message.reply_text("❌ Invalid phone. Please enter again:")
        return PHONE

    context.user_data["phone"] = phone
    await update.message.reply_text("📝 Describe your request:")
    return REQUEST

async def get_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["request"] = update.message.text

    name = context.user_data["name"]
    phone = context.user_data["phone"]
    req = context.user_data["request"]

    await update.message.reply_text("✅ Thank you! Your application has been submitted.")

    await context.bot.send_message(
        ADMIN_ID,
        f"📩 New request:\n\n"
        f"👤 Name: {name}\n"
        f"📞 Phone: {phone}\n"
        f"📝 Request: {req}"
    )

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Application canceled.")
    return ConversationHandler.END

app = Application.builder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("apply", apply)],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
        REQUEST: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_request)],
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)

app.add_handler(CommandHandler("start", start))
app.add_handler(conv_handler)

PORT = int(os.environ.get("PORT", 8443))
WEBHOOK_URL = f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/"

app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    webhook_url=WEBHOOK_URL,
)
