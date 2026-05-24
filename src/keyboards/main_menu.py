"""
Основное меню пользователя.

Модуль предназначен для клавиатуры главного экрана бота: перехода в каталог,
профиль, оплату, бронирование и другие базовые пользовательские разделы.
"""

from telegram import ReplyKeyboardMarkup
from src.core.logger import logger

MAIN_MENU_BUTTONS = [
    ["Кнопка 1", "Кнопка 2"],
    ["Кнопка 3", "Кнопка 4"]
]

# билд inline-кнопок
def build_main_menu() -> ReplyKeyboardMarkup:
    logger.info("build_main_menu")
    
    return ReplyKeyboardMarkup(
        MAIN_MENU_BUTTONS,
        resize_keyboard=True,
        input_field_placeholder="main menu"
    )




