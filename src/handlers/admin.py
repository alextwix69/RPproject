from src.core.logger import logger
from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes
)

from src.keyboards.kb_build import build_admin_panel

ADMIN_MESSAGE = (
    "Это admin-панель\n"
)

ADMIN_IDS = [
    1016417047
]

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("admin()")

    
    if update.effective_user.id not in ADMIN_IDS:
        return
    

    await update.message.reply_text(
        ADMIN_MESSAGE,
        reply_markup=build_admin_panel()
    )

def register_admin_handler(application) -> None:
    application.add_handler(CommandHandler("admin", admin))