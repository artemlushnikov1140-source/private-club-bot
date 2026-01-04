import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ===== ENV =====
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
INVITE_LINK = os.getenv("INVITE_LINK")

# ===== FAKE WEB SERVER =====
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_http_server():
    port = int(os.getenv("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()

# ===== TELEGRAM BOT =====
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

async def request_access(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    admin_keyboard = [
        [
            InlineKeyboardButton("✅ Разрешить", callback_data=f"approve:{user.id}"),
            InlineKeyboardButton("❌ Отклонить", callback_data=f"reject:{user.id}")
        ]
    ]

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "📩 Новая заявка в приватный канал\n\n"
            f"👤 @{user.username or 'без_ника'}\n"
            f"🆔 ID: {user.id}"
        ),
        reply_markup=InlineKeyboardMarkup(admin_keyboard)
    )

    await query.edit_message_text(
        "✅ Ваша заявка отправлена администратору.\n"
        "Пожалуйста, ожидайте решения."
    )

async def admin_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        await query.edit_message_text("✅ Заявка одобрена. Ссылка отправлена.")
    else:
        await context.bot.send_message(
            chat_id=user_id,
            text="❌ К сожалению, Ваша заявка была отклонена."
        )
        await query.edit_message_text("❌ Заявка отклонена.")

def main():
    # запускаем HTTP-сервер в отдельном потоке
    threading.Thread(target=run_http_server, daemon=True).start()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(request_access, pattern="^request$"))
    app.add_handler(CallbackQueryHandler(admin_decision, pattern="^(approve|reject):"))

    print("Private club bot is running")
    app.run_polling()

if __name__ == "__main__":
    main()
