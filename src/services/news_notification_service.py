"""Новостные уведомления от администраторов."""

from telegram import Bot

from src.core.database import get_session
from src.core.logger import logger
from src.repositories.user_repo import list_news_notification_users
from src.services.chat_cleanup_service import remember_telegram_message


async def send_news_notification(bot: Bot, text: str) -> None:
    """Рассылает новость всем пользователям с включенной настройкой."""

    with get_session() as session:
        users = list_news_notification_users(session)

    for user in users:
        try:
            message = await bot.send_message(
                chat_id=user.telegram_id,
                text=f"📰 Новость RoleHub\n\n{text}",
            )
            remember_telegram_message(message)
        except Exception:
            logger.exception("Failed to send news notification to %s", user.telegram_id)
