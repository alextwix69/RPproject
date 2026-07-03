"""Сборка inline-меню бота."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from src.core.logger import logger
import src.keyboards.inline_buttons as buttons


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
    return getMainMenuKeyboard()


def build_admin_panel() -> InlineKeyboardMarkup:
    logger.info("build_admin_panel")

    return _build_inline_keyboard(
        [
            [("Пользователи", "admin:users")],
            [("Статистика", "admin:stats"), ("Экспорт CSV", "admin:export_users")],
        ]
    )


def getMainMenuKeyboard() -> InlineKeyboardMarkup:
    return _build_inline_keyboard(buttons.MAIN_MENU_BUTTONS)


def getPlayTopicsKeyboard() -> InlineKeyboardMarkup:
    return _build_inline_keyboard(buttons.PLAY_TOPICS_BUTTONS)


def getTopicActionsKeyboard(topic: str) -> InlineKeyboardMarkup:
    return _build_inline_keyboard(
        [
            [("🔎 Найти лобби", f"play:find:{topic}")],
            [("➕ Создать лобби", f"play:create:{topic}")],
            [("📋 Список комнат", f"play:rooms:{topic}")],
            [("⬅️ Назад", "play:back:topics"), ("🏠 Меню", buttons.MENU_MAIN_CALLBACK)],
        ]
    )


def getShopKeyboard() -> InlineKeyboardMarkup:
    return _build_inline_keyboard(buttons.SHOP_BUTTONS)


def getShopProfilesKeyboard() -> InlineKeyboardMarkup:
    return _build_inline_keyboard(buttons.SHOP_PROFILES_BUTTONS)


def getShopThemesKeyboard() -> InlineKeyboardMarkup:
    return _build_inline_keyboard(buttons.SHOP_THEMES_BUTTONS)


def getShopPremiumKeyboard() -> InlineKeyboardMarkup:
    return _build_inline_keyboard(buttons.SHOP_PREMIUM_BUTTONS)


def getSettingsKeyboard() -> InlineKeyboardMarkup:
    return _build_inline_keyboard(buttons.SETTINGS_BUTTONS)


def getSettingsProfileKeyboard() -> InlineKeyboardMarkup:
    return _build_inline_keyboard(buttons.SETTINGS_PROFILE_BUTTONS)


def getSettingsNotificationsKeyboard(userSettings=None) -> InlineKeyboardMarkup:
    return _build_inline_keyboard(buttons.SETTINGS_NOTIFICATIONS_BUTTONS)


def getSettingsLanguageKeyboard() -> InlineKeyboardMarkup:
    return _build_inline_keyboard(buttons.SETTINGS_LANGUAGE_BUTTONS)


def getSettingsSafetyKeyboard() -> InlineKeyboardMarkup:
    return _build_inline_keyboard(buttons.SETTINGS_SAFETY_BUTTONS)


def getSupportKeyboard() -> InlineKeyboardMarkup:
    return _build_inline_keyboard(buttons.SUPPORT_BUTTONS)


def getSupportFaqKeyboard() -> InlineKeyboardMarkup:
    return _build_inline_keyboard(buttons.SUPPORT_FAQ_BUTTONS)


def getBackToMenuKeyboard(backCallback: str) -> InlineKeyboardMarkup:
    return _build_inline_keyboard(
        [
            [("⬅️ Назад", backCallback)],
            [("🏠 Главное меню", buttons.MENU_MAIN_CALLBACK)],
        ]
    )
