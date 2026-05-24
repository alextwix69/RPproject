"""
ORM-модель пользователя Telegram.

Здесь обычно хранятся telegram_id, имя, роль, регистрационные данные,
timestamps и другая информация, которая нужна для сценариев профиля,
регистрации и прав доступа.
"""

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String
from datetime import date

class Base(DeclarativeBase):
    pass

class User(Base):
    __name__ = "users"

    id : Mapped[int] = mapped_column(
        primary_key=True, 
        unique=True, 
        index=True
    )
    
    username : Mapped[str] = mapped_column(String(255))
    created_at : Mapped[date] = mapped_column(date)


