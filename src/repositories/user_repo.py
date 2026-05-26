"""
Репозиторий пользователей.

Здесь находятся операции поиска, создания и обновления пользователя Telegram.
Репозиторий работает с ORM-моделью User и получает session снаружи.
"""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.user import User
from src.core.logger import logger

def get_by_telegram_id(session: Session, telegram_id: int) -> User | None:
    """Ищет пользователя в базе по Telegram ID."""

    logger.info("get_by_telegram_id : вход")

    # Собираем SQL-запрос: SELECT users WHERE telegram_id = ...
    stmt = select(User).where(User.telegram_id == telegram_id)
    logger.info("get_by_telegram_id : select вызван")

    # session.scalar вернет одного пользователя или None, если пользователь не найден.
    return session.scalar(stmt)


def create_from_effective_user(session: Session, effective_user) -> User:
    """Создает нового пользователя из Telegram effective_user."""

    # Одно и то же время используем для first_seen_at и last_seen_at.
    now = datetime.utcnow()

    # Перекладываем данные из Telegram effective_user в нашу ORM-модель User.
    user = User(
        telegram_id=effective_user.id,
        username=effective_user.username,
        first_name=effective_user.first_name,
        last_name=effective_user.last_name,
        language_code=effective_user.language_code,
        is_bot=effective_user.is_bot,
        first_seen_at=now,
        last_seen_at=now,
    )

    # Добавляем пользователя в session.
    # Финальное сохранение обычно делается снаружи через session.commit().
    session.add(user)

    return user


def update_from_effective_user(user: User, effective_user) -> User:
    """Обновляет Telegram-поля уже существующего пользователя."""

    # Если пользователь поменял username или имя в Telegram,
    # сохраняем свежие данные в нашей базе.
    user.username = effective_user.username
    user.first_name = effective_user.first_name
    user.last_name = effective_user.last_name
    user.language_code = effective_user.language_code
    user.is_bot = effective_user.is_bot
    user.last_seen_at = datetime.utcnow()

    # Важно: is_registered здесь не меняем.
    # Регистрация в боте — отдельная логика, она не должна сбрасываться.
    return user
