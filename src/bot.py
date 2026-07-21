"""
Главная точка сборки Telegram-бота.

В этом модуле обычно создаются экземпляры Bot и Dispatcher, подключаются
handlers, reply-роутеры, middlewares, конфигурация и инфраструктурные сервисы.
После сборки приложение запускает polling или webhook-режим, в зависимости
от выбранной схемы развёртывания.
"""

from src.core.config import get_api_key
from src.core.database import create_db_tables

from telegram.ext import ApplicationBuilder, MessageHandler, filters


from src.handlers.start import register_start_handler
from src.handlers.admin import register_admin_handler 
from src.handlers.main_menu import register_main_menu_handler
from src.handlers.play_lobby import (
    register_lobby_message_handler,
    start_lobby_background_tasks,
    stop_lobby_background_tasks,
)
from src.services.chat_cleanup_service import track_incoming_message

# Создание приложения бота
def build_application():
    create_db_tables()

    API_KEY = get_api_key()
    application = (
        ApplicationBuilder()
        .token(API_KEY)
        .post_init(start_lobby_background_tasks)
        .post_stop(stop_lobby_background_tasks)
        .post_shutdown(stop_lobby_background_tasks)
        .build()
    )

    if application == None:
        raise RuntimeError("Ошибка билда приложения")
    
    application.add_handler(MessageHandler(filters.ALL, track_incoming_message), group=-1)
    register_start_handler(application)
    register_admin_handler(application)
    register_main_menu_handler(application)
    register_lobby_message_handler(application)

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
