"""
ORM-модель пользователя Telegram.

Модель описывает таблицу users в базе данных. В ней хранятся Telegram-данные
пользователя, роль, статус регистрации и временные метки появления/обновления.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class User(Base):
    """Пользователь Telegram внутри приложения."""

    __tablename__ = "users"

    # Внутренний ID записи в базе данных.
    id: Mapped[int] = mapped_column(primary_key=True)

    # Telegram ID пользователя.
    # unique=True запрещает дубли, index=True ускоряет поиск по telegram_id.
    telegram_id: Mapped[int] = mapped_column(unique=True, index=True)

    # Данные, которые приходят из Telegram effective_user.
    # Они могут отсутствовать, поэтому ставим nullable=True.
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    language_code: Mapped[str | None] = mapped_column(String(16), nullable=True)

    # Служебные поля приложения.
    # role нужен для прав доступа, is_registered показывает прохождение регистрации.
    is_bot: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[str] = mapped_column(String(50), default="user")
    # Показывает, прошел ли пользователь регистрацию в боте.
    is_registered: Mapped[bool] = mapped_column(Boolean, default=False)
    current_lobby_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
    pending_action: Mapped[str | None] = mapped_column(String(64), nullable=True)
    create_state: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Время первого и последнего появления пользователя в боте.
    first_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # created_at ставится при создании записи.
    # updated_at обновляется при изменении записи благодаря onupdate.
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
