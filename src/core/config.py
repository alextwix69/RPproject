"""
Центральная конфигурация проекта.

Этот модуль загружает настройки из .env и делает их доступными внутри
приложения: токен бота, API-ключи, параметры базы данных, Redis и режим
окружения. Здесь находится инфраструктурная точка конфигурации проекта.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path("../../.env")
load_dotenv(dotenv_path=env_path)
API_KEY = os.environ.get("API_KEY")

if not API_KEY:
    raise RuntimeError("API_KEY не получен")


