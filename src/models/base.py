"""
Базовый слой ORM-моделей.

Модуль предназначен для общего базового класса, metadata и повторно
используемых полей, которые нужны моделям пользователей, платежей, товаров и
других сущностей.
"""

from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass


