from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "ВСТАВЬ_СЮДА_ТОКЕН"
ADMIN_ID = 123456789  # сюда твой Telegram ID
INVITE_LINK = "https://t.me/your_private_channel"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✅ Хочу вступить в приватный канал", callback_data="request")]
    ]
    await update.message.reply_text(
        "Здравствуйте!\n\n"
        "Вы можете подать заявку на вступление в приватный канал.\n"
        "Нажмите кнопку ниже, чтобы отправить запрос.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user

    admin_keyboard = [
        [
            InlineKeyboardButton("✅ Разрешить", callback_data=f"approve:{user.id}"),
            InlineKeyboardButton("❌ Отклонить", callback_data=f"reject:{user.id}")
        ]
    ]

    text = (
        "📩 Новая заявка на вступление\n\n"
        f"👤 Пользователь: @{user.username or 'без_ника'}\n"
        f"🆔 ID: {user.id}"
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=text,
        reply_markup=InlineKeyboardMarkup(admin_keyboard)
    )

    await query.edit_message_text(
        "✅ Ваша заявка отправлена администратору.\n"
        "Пожалуйста, ожидайте решения."
    )

async def handle_admin_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action, user_id = query.data.split(":")
    user_id = int(user_id)

    if action == "approve":
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "🎉 Ваша заявка одобрена!\n\n"
                f"Вот ссылка для вступления:\n{INVITE_LINK}"
            )
        )
        await query.edit_message_text("✅ Заявка одобрена, ссылка отправлена.")
    else:
        await context.bot.send_message(
            chat_id=user_id,
            text="❌ К сожалению, ваша заявка была отклонена."
        )
        await query.edit_message_text("❌ Заявка отклонена.")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_request, pattern="^request$"))
    app.add_handler(CallbackQueryHandler(handle_admin_decision, pattern="^(approve|reject):"))

    print("Bot is running...")
    app.run_polling()

if __name__== "__main__":
    main()
