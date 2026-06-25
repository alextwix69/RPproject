"""Сборка inline-меню бота."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from src.core.logger import logger
import src.keyboards.inline_buttons as inline_buttons


def _build_inline_keyboard(button_rows) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text=text, callback_data=callback_data)
                for text, callback_data in row
            ]
            for row in button_rows
        ]
    )


def build_main_menu() -> InlineKeyboardMarkup:
    logger.info("build_main_menu")

    return _build_inline_keyboard(inline_buttons.MAIN_MENU_BUTTONS)


def build_admin_panel() -> InlineKeyboardMarkup:
    logger.info("build_admin_panel")

    return _build_inline_keyboard(inline_buttons.ADMIN_PANEL_BUTTONS)


def build_choose_theme() -> InlineKeyboardMarkup:
    logger.info("build_choose_theme")

    return _build_inline_keyboard(inline_buttons.CHOOSE_THEME_BUTTONS)

