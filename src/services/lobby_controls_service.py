"""Reply-клавиатура активной комнаты."""

from telegram import Bot

from src.core.logger import logger
from src.keyboards.lobby_keyboard import (
    get_active_lobby_reply_keyboard,
    get_remove_lobby_reply_keyboard,
)
from src.services.chat_cleanup_service import remember_telegram_message


async def show_active_lobby_controls(bot: Bot, chat_id: int) -> None:
    try:
        message = await bot.send_message(
            chat_id=chat_id,
            text="Кнопки комнаты доступны снизу.",
            reply_markup=get_active_lobby_reply_keyboard(),
        )
        remember_telegram_message(message)
    except Exception:
        logger.exception("Failed to show active lobby controls to chat %s", chat_id)


async def hide_active_lobby_controls(bot: Bot, chat_id: int) -> None:
    try:
        message = await bot.send_message(
            chat_id=chat_id,
            text="Клавиатура комнаты скрыта.",
            reply_markup=get_remove_lobby_reply_keyboard(),
        )
        remember_telegram_message(message)
    except Exception:
        logger.exception("Failed to hide active lobby controls for chat %s", chat_id)
