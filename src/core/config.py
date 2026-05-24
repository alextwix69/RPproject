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

