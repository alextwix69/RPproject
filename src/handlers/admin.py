from src.core.logger import logger
from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes
)

from src.keyboards.kb_build import build_admin_panel
from src.core.config import get_admin_ids

ADMIN_MESSAGE = (
    "Это admin-панель\n"
)

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("admin()")

    if update.effective_user is None or update.effective_user.id not in get_admin_ids():
        return

    await update.message.reply_text(
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
    await query.edit_message_text("Админ-действие пока не настроено.")


def register_admin_handler(application) -> None:
    application.add_handler(CommandHandler("admin", admin))
    application.add_handler(CallbackQueryHandler(admin_callback, pattern=r"^admin:"))
