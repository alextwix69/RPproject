"""
Основное меню пользователя.

Модуль предназначен для клавиатуры главного экрана бота: перехода в каталог,
профиль, оплату, бронирование и другие базовые пользовательские разделы.
"""

from telegram import ReplyKeyboardMarkup
from src.core.logger import logger
import src.keyboards.inline_buttons as inline_buttons

# билд inline-кнопок
def build_main_menu() -> ReplyKeyboardMarkup:
    logger.info("build_main_menu")

    return ReplyKeyboardMarkup(
        inline_buttons.MAIN_MENU_BUTTONS,
        resize_keyboard=True,
        input_field_placeholder="main menu"
    )

def build_admin_panel() -> ReplyKeyboardMarkup:
    logger.info("build_admin_panel")

    return ReplyKeyboardMarkup(
        inline_buttons.ADMIN_PANEL_BUTTONS,
        resize_keyboard=True,
        input_field_placeholder="main menu"
    )



