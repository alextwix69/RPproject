from enum import Enum


class MainMenuIntent(str, Enum):
    """Понятные имена действий, которые может выбрать пользователь в главном меню."""

    PLAY = "PLAY"
    SHOP = "SHOP"
    SETTINGS = "SETTINGS"
    SUPPORT = "SUPPORT"
    UNKNOWN = "UNKNOWN"


# Единый контракт callback-data главного меню.
# Клавиатура должна отправлять эти строки, а handler будет получать готовый intent.
_MAIN_MENU_CALLBACKS = {
    "main:play": MainMenuIntent.PLAY,
    "main:shop": MainMenuIntent.SHOP,
    "main:settings": MainMenuIntent.SETTINGS,
    "main:support": MainMenuIntent.SUPPORT,
}


# Тексты держим рядом с router'ом, пока проект маленький.
# Так handler сможет просто выбрать intent и взять готовый ответ.
MAIN_MENU_RESPONSE_TEXTS = {
    MainMenuIntent.PLAY: "Выбери тему для игры:",
    MainMenuIntent.SHOP: "Тут будет магазин.",
    MainMenuIntent.SETTINGS: "Тут будут настройки.",
    MainMenuIntent.SUPPORT: "Тут будет поддержка.",
    MainMenuIntent.UNKNOWN: (
        "Неизвестная кнопка. Вернись в главное меню и выбери раздел ещё раз."
    ),
}


def resolve_main_menu_callback(callback_data: str) -> MainMenuIntent:
    """Преобразует callback-data из Telegram-кнопки в intent главного меню."""

    # Неизвестные callback-data не должны ломать handler.
    # Поэтому для любой чужой или старой кнопки возвращаем UNKNOWN.
    return _MAIN_MENU_CALLBACKS.get(callback_data, MainMenuIntent.UNKNOWN)


def get_main_menu_response_text(intent: MainMenuIntent) -> str:
    """Возвращает текст ответа для выбранного intent главного меню."""

    # Если handler случайно передаст неизвестный intent,
    # пользователь всё равно получит понятный fallback.
    return MAIN_MENU_RESPONSE_TEXTS.get(
        intent,
        MAIN_MENU_RESPONSE_TEXTS[MainMenuIntent.UNKNOWN],
    )
