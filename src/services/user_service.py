"""
Сервис пользователей.

Модуль предназначен для бизнес-логики регистрации, профиля, ролей, проверок
состояния пользователя и других операций, которые не должны жить напрямую в
handlers.
"""

from src.keyboards.main_menu import MAIN_MENU_BUTTONS
from src.core.logger import logger

# Получить список кнопок
def get_menu_items() -> list[str]:
    logger.info("get_menu_items")

    output = []
    for buttons in MAIN_MENU_BUTTONS:
        output.extend(buttons)

    return output

# Текст нажатия кнопки
def get_button_text(button) -> str:
    logger.info(f"get_button_text({button})")
    
    return f"Кнопка {button} нажата"

