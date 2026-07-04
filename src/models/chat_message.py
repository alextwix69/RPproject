"""Сообщения чатов, которые бот может очищать."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class ChatMessage(Base):
    """Telegram message_id, который бот может удалить или переиспользовать."""

    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(Integer, index=True)
    message_id: Mapped[int] = mapped_column(Integer)
    is_notify: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active_screen: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
