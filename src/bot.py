"""
Главная точка сборки Telegram-бота.

В этом модуле обычно создаются экземпляры Bot и Dispatcher, подключаются
handlers, callbacks, middlewares, конфигурация и инфраструктурные сервисы.
После сборки приложение запускает polling или webhook-режим, в зависимости
от выбранной схемы развёртывания.
"""

from src.core.config import get_api_key
from src.core.database import create_db_tables

from telegram.ext import ApplicationBuilder


from src.handlers.start import register_start_handler
from src.handlers.admin import register_admin_handler 

# Создание приложения бота
def build_application():
    create_db_tables()

    API_KEY = get_api_key()
    application = ApplicationBuilder().token(API_KEY).build()

    if application == None:
        raise RuntimeError("Ошибка билда приложения")
    
    register_start_handler(application)
    register_admin_handler(application)

    return application

# режим развертки - polling (poll/epoll)
def main() -> None:
    application = build_application() # Сам бот
    
    application.run_polling(
        poll_interval=0.0,
        bootstrap_retries=-1,
        drop_pending_updates=False
    ) # запускает боля в режиме ожидания, тут нужно поставить настройки (см библиотеку)

if __name__ == "__main__":
    main()
