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
    get_by_display_name,
    get_by_telegram_id,
    update_from_effective_user
)


class DisplayNameError(ValueError):
    """Ошибка сохранения имени профиля."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


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


def normalize_display_name(raw_name: str | None) -> str:
    """Приводит имя профиля к стабильному виду."""

    return " ".join((raw_name or "").strip().split())


def set_display_name(session, user: User, raw_name: str | None) -> User:
    """Сохраняет уникальное имя профиля пользователя."""

    display_name = normalize_display_name(raw_name)
    if not display_name:
        raise DisplayNameError("empty", "Напиши имя текстом.")
    if len(display_name) < 2:
        raise DisplayNameError("too_short", "Имя должно быть не короче 2 символов.")
    if len(display_name) > 32:
        raise DisplayNameError("too_long", "Имя должно быть не длиннее 32 символов.")
    if display_name.startswith("@"):
        raise DisplayNameError("starts_with_at", "Имя не должно начинаться с @.")

    existing_user = get_by_display_name(session, display_name)
    if existing_user is not None and existing_user.id != user.id:
        raise DisplayNameError("taken", "Такое имя уже занято. Попробуй другое.")

    user.display_name = display_name
    user.is_registered = True
    return user


def toggle_news_notifications(user: User) -> bool:
    user.news_notifications_enabled = not user.news_notifications_enabled
    return user.news_notifications_enabled



    
