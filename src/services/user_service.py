"""
Сервис пользователей.

Модуль предназначен для бизнес-логики регистрации, профиля, ролей, проверок
состояния пользователя и других операций, которые не должны жить напрямую в
handlers.
"""

# Ошибка
from src.keyboards.main_menu import MAIN_MENU_BUTTONS

# Получить список кнопок
def get_menu_items() -> list[str]:
    output = []
    for buttons in MAIN_MENU_BUTTONS:
        output.extend(buttons)

    return output

# Текст нажатия кнопки
def get_button_text(button) -> str:
    return f"Кнопка {button} нажата"

print(get_menu_items())