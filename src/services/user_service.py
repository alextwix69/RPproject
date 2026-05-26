"""
Сервис пользователей.

Модуль предназначен для бизнес-логики регистрации, профиля, ролей, проверок
состояния пользователя и других операций, которые не должны жить напрямую в
handlers.
"""

from src.core.logger import logger
from src.models.user import User

from src.repositories.user_repo import (
    create_from_effective_user,
    get_by_telegram_id,
    update_from_effective_user
)

def ensure_from_effective_user(session, effective_user) -> User | None:
    """Создает пользователя, если его нет, или обновляет, если он уже есть."""
    logger.info("ensure_from_effective_user : start")

    # Иногда update может прийти без Telegram-пользователя.
    if effective_user is None:
        return None

    logger.info("ensure_from_effective_user : eu is NOT NONE")
    
    # Ищем пользователя по Telegram ID.
    user = get_by_telegram_id(session, effective_user.id)
    logger.info("ensure_from_effective_user : get_by_telegram_id : end")

    # Если пользователя еще нет в базе — создаем.
    if user is None:
        return create_from_effective_user(session, effective_user)
    logger.info("ensure_from_effective_user : user is NOT NONE")
    
    # Если пользователь уже есть — обновляем Telegram-данные.
    return update_from_effective_user(user, effective_user)



    
