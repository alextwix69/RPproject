"""
Главная точка сборки Telegram-бота.

В этом модуле обычно создаются экземпляры Bot и Dispatcher, подключаются
handlers, callbacks, middlewares, конфигурация и инфраструктурные сервисы.
После сборки приложение запускает polling или webhook-режим, в зависимости
от выбранной схемы развёртывания.
"""

from core.config import get_api_key

API_KEY = get_api_key()


