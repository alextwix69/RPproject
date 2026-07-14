"""
Обработчик команды /start и первичного входа пользователя.

Здесь обычно формируется приветствие, проверяется состояние пользователя,
показывается главное меню и запускаются первые шаги регистрации или знакомства
с ботом.
"""

from src.core.logger import logger
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CommandHandler,
    ContextTypes
)

from src.render.menu import showMainMenu
from src.render.menu import showNamePrompt
from src.services.user_service import ensure_from_effective_user
from src.core.database import get_session
from src.constants.pending_actions import PENDING_SET_DISPLAY_NAME
from src.services.chat_cleanup_service import clear_chat, reply_text
from src.services.admin_service import is_admin_effective_user, is_owner_effective_user
from src.services.user_state_service import set_pending_action

DEVELOPMENT_MESSAGE = (
    "🏰✨ Порталы RoleHub пока готовятся к открытию!\n\n"
    "Мы собираем любимые вселенные, роли и приключения, чтобы твой первый вход "
    "получился по-настоящему majestic 👑🌌\n\n"
    "Следи за магическими весточками и открытием доступа в нашем канале:"
)


def _development_channel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🌟 Заглянуть в канал", url="https://t.me/RoleHubChannel")]]
    )


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

    if not _can_access_development_build(update):
        await reply_text(
            update.message,
            DEVELOPMENT_MESSAGE,
            reply_markup=_development_channel_keyboard(),
        )
        return

    if should_prompt_name:
        await showNamePrompt(update)
        return

    await showMainMenu(update)


def _can_access_development_build(update: Update) -> bool:
    return (
        is_owner_effective_user(update.effective_user)
        or is_admin_effective_user(update.effective_user)
    )


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return

    await showMainMenu(update)
    await clear_chat(update)


# связь вызова /start и функции start()
def register_start_handler(application) -> None:
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("clear", clear_command))
