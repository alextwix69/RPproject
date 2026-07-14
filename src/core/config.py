"""
Центральная конфигурация проекта.

Этот модуль загружает настройки из .env и делает их доступными внутри
приложения: токен бота, API-ключи, параметры базы данных, Redis и режим
окружения. Здесь находится инфраструктурная точка конфигурации проекта.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

# Функция получения API-ключа, используется в bot.py
def get_api_key() -> str:
    api_key = os.environ.get("API_KEY")
    if not api_key:
        raise RuntimeError("API_KEY не получен")
    return api_key

# Получение DATABASE_URL из .env
def get_database_url() -> str:
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise RuntimeError("db_url не получен")
    return db_url

def _parse_id_list(raw_value: str) -> list[int]:
    return [
        int(x.strip())
        for x in raw_value.split(",")
        if x.strip()
    ]


def get_owner_ids() -> list[int]:
    owner_ids = os.getenv("OWNER_IDS")
    if owner_ids:
        return _parse_id_list(owner_ids)

    legacy_admin_ids = os.getenv("ADMIN_IDS", "")
    return _parse_id_list(legacy_admin_ids)
