"""
Обработчик команды /start и первичного входа пользователя.

Здесь обычно формируется приветствие, проверяется состояние пользователя,
показывается главное меню и запускаются первые шаги регистрации или знакомства
с ботом.
"""

from src.core.logger import logger
from telegram import ReplyKeyboardRemove, Update
from telegram.ext import (
    CommandHandler,
    ContextTypes
)

from src.keyboards.kb_build import build_main_menu

from src.services.user_service import ensure_from_effective_user
from src.core.database import get_session

START_MESSAGE = (
    "Добро пожаловать в RoleHub!\n"
)

# что делает бот при start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("start()")

    # Обработка текущего пользователя
    
    with get_session() as session:
        try:
            ensure_from_effective_user(session, update.effective_user)
            session.commit()
        except Exception:
            session.rollback()
            raise
        

    if update.message is None:
        return

    await update.message.reply_text(
        START_MESSAGE,
        reply_markup=ReplyKeyboardRemove()
    )

    await update.message.reply_text(
        "Главное меню:",
        reply_markup=build_main_menu()
    )

# связь вызова /start и функции start()
def register_start_handler(application) -> None:
    application.add_handler(CommandHandler("start", start))
