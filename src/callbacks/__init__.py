"""
Файл делает директорию callbacks Python-пакетом.

Здесь можно собирать и экспортировать callback-роутеры, которые обрабатывают
нажатия inline-кнопок Telegram и подключаются в основной сборке бота.
"""

from src.callbacks.main_menu import (
    MAIN_MENU_RESPONSE_TEXTS,
    MainMenuIntent,
    get_main_menu_response_text,
    resolve_main_menu_callback,
)


__all__ = [
    "MAIN_MENU_RESPONSE_TEXTS",
    "MainMenuIntent",
    "get_main_menu_response_text",
    "resolve_main_menu_callback",
]