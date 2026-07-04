"""
Обработчик команды /start и первичного входа пользователя.

Здесь обычно формируется приветствие, проверяется состояние пользователя,
показывается главное меню и запускаются первые шаги регистрации или знакомства
с ботом.
"""

from src.core.logger import logger
from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes
)

from src.render.menu import showMainMenu
from src.render.menu import showNamePrompt
from src.services.user_service import ensure_from_effective_user
from src.core.database import get_session
from src.constants.pending_actions import PENDING_SET_DISPLAY_NAME
from src.services.chat_cleanup_service import clear_chat
from src.services.user_state_service import set_pending_action

# что делает бот при start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("start()")

    await clear_chat(update)

    # Обработка текущего пользователя
    
    with get_session() as session:
        try:
            user = ensure_from_effective_user(session, update.effective_user)
            should_prompt_name = bool(user is not None and not user.display_name)
            if should_prompt_name:
                set_pending_action(user, PENDING_SET_DISPLAY_NAME)
            session.commit()
        except Exception:
            session.rollback()
            raise
        

    if update.message is None:
        return

    if should_prompt_name:
        await showNamePrompt(update)
        return

    await showMainMenu(update)


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return

    await clear_chat(update)


# связь вызова /start и функции start()
def register_start_handler(application) -> None:
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("clear", clear_command))
