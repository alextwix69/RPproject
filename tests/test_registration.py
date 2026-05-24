"""
Тесты сценария регистрации пользователя.

Модуль предназначен для проверки шагов сбора данных, подтверждений, сохранения
пользователя и поведения бота при корректном или ошибочном вводе.
"""

import pytest
from src.services.user_service import (
    get_menu_items,
    get_button_text
)

# Тест, проверяющий работу get_menu_items()
def test_menu_items_not_empty():
    menu_items = get_menu_items()
    assert menu_items != None and len(menu_items) > 0

# Тест, проверяющщий get_button_text()
def test_button_text_not_empty():
    buttons = get_menu_items()
    buttons_number = len(buttons)
    flag = True

    for i in range(buttons_number):

        if get_button_text(i) == None or len(get_button_text(i)) == 0:
            flag = False
            break

    assert flag == True