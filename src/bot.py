"""
Главная точка сборки Telegram-бота.

В этом модуле обычно создаются экземпляры Bot и Dispatcher, подключаются
handlers, callbacks, middlewares, конфигурация и инфраструктурные сервисы.
После сборки приложение запускает polling или webhook-режим, в зависимости
от выбранной схемы развёртывания.
"""

from src.core.config import get_api_key

from telegram.ext import ApplicationBuilder

from src.handlers.start import register_start_handler

# Создание приложения бота
def build_application():
    API_KEY = get_api_key()
    application = ApplicationBuilder().token(API_KEY).build()

    if application == None:
        raise RuntimeError("Ошибка билда приложения")
    
    register_start_handler(application)

    return application

# режим развертки - polling (poll/epoll)
def main() -> None:
    application = build_application() # Сам бот
    
    application.run_polling() # запускает боля в режиме ожидания, тут нужно поставить настройки (см библиотеку)


main()