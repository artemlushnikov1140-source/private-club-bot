import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
PRIVATE_INVITE_LINK = os.getenv("INVITE_LINK")

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Хочу вступить в приватный канал", callback_data="request")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Здравствуйте!\n\n"
        "Вы хотите подать заявку на вступление в приватный канал?",
        reply_markup=reply_markup
    )

async def request_access(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user

    keyboard = [
        [
            InlineKeyboardButton("✅ Разрешить", callback_data=f"approve:{user.id}"),
            InlineKeyboardButton("❌ Отклонить", callback_data=f"reject:{user.id}")
        ]
    ]

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "📥 Новая заявка в приватный канал\n\n"
            f"👤 {user.full_name}\n"
            f"🔗 @{user.username if user.username else 'без username'}\n"
            f"🆔 ID: {user.id}"
        ),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await query.message.reply_text(
        "✅ Ваша заявка отправлена администратору.\n"
        "Пожалуйста, ожидайте решения."
    )

async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = int(query.data.split(":")[1])

    await context.bot.send_message(
        chat_id=user_id,
        text=(
            "🎉 Ваша заявка одобрена!\n\n"
            f"Вот ссылка для входа:\n{PRIVATE_INVITE_LINK}"
        )
    )

    await query.edit_message_text("✅ Заявка одобрена")

async def reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = int(query.data.split(":")[1])

    await context.bot.send_message(
        chat_id=user_id,
        text="❌ К сожалению, ваша заявка была отклонена."
    )

    await query.edit_message_text("❌ Заявка отклонена")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(request_access, pattern="^request$"))
    app.add_handler(CallbackQueryHandler(approve, pattern="^approve:"))
    app.add_handler(CallbackQueryHandler(reject, pattern="^reject:"))

    app.run_polling()

if __name__ == "__main__":
    main()
