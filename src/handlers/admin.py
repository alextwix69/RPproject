from src.core.logger import logger
from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes
)

from src.keyboards.kb_build import build_admin_panel
from src.core.config import get_admin_ids
from src.handlers.admin_handlers.users import register_admin_users_handlers
from src.services.chat_cleanup_service import remember_telegram_message, reply_text
from src.services.news_notification_service import send_news_notification

ADMIN_MESSAGE = (
    "Админ-панель\n\n"
    "Команды:\n"
    "/users - последние пользователи\n"
    "/user <telegram_id> - карточка пользователя\n"
    "/stats - статистика\n"
    "/export_users - экспорт CSV\n"
    "/notify <текст> - новостная рассылка"
)

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("admin()")

    if update.effective_user is None or update.effective_user.id not in get_admin_ids():
        return

    await reply_text(
        update.message,
        ADMIN_MESSAGE,
        reply_markup=build_admin_panel()
    )


async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    if query is None:
        return

    if update.effective_user is None or update.effective_user.id not in get_admin_ids():
        await query.answer("Нет доступа", show_alert=True)
        return

    await query.answer()
    if query.data == "admin:notify":
        sent_message = await query.edit_message_text(
            "Новостная рассылка\n\n"
            "Отправь команду:\n"
            "/notify текст новости",
            reply_markup=build_admin_panel(),
        )
        if sent_message is not True:
            remember_telegram_message(sent_message, is_active_screen=True)
        return

    sent_message = await query.edit_message_text("Админ-действие пока не настроено.")
    if sent_message is not True:
        remember_telegram_message(sent_message, is_active_screen=True)


async def notify_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user is None or update.effective_user.id not in get_admin_ids():
        return

    if update.message is None:
        return

    text = " ".join(context.args).strip()
    if not text:
        await reply_text(
            update.message,
            "Использование: /notify текст новости"
        )
        return

    await send_news_notification(update.get_bot(), text)


def register_admin_handler(application) -> None:
    application.add_handler(CommandHandler("admin", admin))
    application.add_handler(CommandHandler("notify", notify_command))
    register_admin_users_handlers(application)
    application.add_handler(CallbackQueryHandler(admin_callback, pattern=r"^admin:"))
