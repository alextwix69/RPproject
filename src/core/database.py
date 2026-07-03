"""
Слой подключения к базе данных.

Модуль предназначен для настройки engine, фабрики сессий и lifecycle
подключения. Через него repositories получают доступ к базе, не создавая
соединения вручную в бизнес-логике или handlers.
"""

from contextlib import contextmanager

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from src.core.config import get_database_url
from src.core.logger import logger
from src.models.base import Base
from src.models import lobby as _lobby_models  # noqa: F401
from src.models import user as _user_models  # noqa: F401

db_url = get_database_url()
engine = create_engine(db_url)

# работа с локальной сессией
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

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
    _ensure_runtime_columns()


def _ensure_runtime_columns() -> None:
    """Добавляет новые nullable-колонки в старую SQLite БД без Alembic."""

    if not db_url.startswith("sqlite"):
        return

    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("users")}
    statements = []

    if "current_lobby_id" not in columns:
        statements.append("ALTER TABLE users ADD COLUMN current_lobby_id INTEGER")
    if "pending_action" not in columns:
        statements.append("ALTER TABLE users ADD COLUMN pending_action VARCHAR(64)")
    if "create_state" not in columns:
        statements.append("ALTER TABLE users ADD COLUMN create_state JSON")

    if not statements:
        return

    with engine.begin() as connection:
        for statement in statements:
            logger.info("runtime schema update: %s", statement)
            connection.execute(text(statement))
