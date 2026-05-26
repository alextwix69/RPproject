"""
Слой подключения к базе данных.

Модуль предназначен для настройки engine, фабрики сессий и lifecycle
подключения. Через него repositories получают доступ к базе, не создавая
соединения вручную в бизнес-логике или handlers.
"""

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.config import get_database_url
from src.core.logger import logger
from src.models.base import Base

db_url = get_database_url()
engine = create_engine(db_url)

# работа с локальной сессией
SessionLocal = sessionmaker(bind=engine)

# Функция передачи сессии
@contextmanager
def get_session():
    logger.info("get_session вызвана")
    with SessionLocal() as session:
        yield session

# проверка и создание таблиц при запуске 
def create_db_tables() -> None :
    logger.info("create_db_tables вызвана")
    Base.metadata.create_all(engine)
