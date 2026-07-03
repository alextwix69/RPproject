from enum import Enum


class MainMenuIntent(str, Enum):
    """Понятные имена действий, которые может выбрать пользователь в главном меню."""

    MAIN = "MAIN"
    PLAY = "PLAY"
    SHOP = "SHOP"
    SETTINGS = "SETTINGS"
    SUPPORT = "SUPPORT"
    UNKNOWN = "UNKNOWN"


_MAIN_MENU_CALLBACKS = {
    "menu:main": MainMenuIntent.MAIN,
    "menu:play": MainMenuIntent.PLAY,
    "menu:shop": MainMenuIntent.SHOP,
    "menu:settings": MainMenuIntent.SETTINGS,
    "menu:support": MainMenuIntent.SUPPORT,
}


MAIN_MENU_RESPONSE_TEXTS = {
    MainMenuIntent.MAIN: "Добро пожаловать в RoleHub!\n\nГлавное меню:",
    MainMenuIntent.PLAY: "🎮 Играть\n\nВыбери тему для игры:",
    MainMenuIntent.SHOP: "🛍 Магазин RoleHub\n\nВыбери раздел:",
    MainMenuIntent.SETTINGS: "⚙️ Настройки\n\nВыбери, что хочешь настроить:",
    MainMenuIntent.SUPPORT: "🆘 Поддержка RoleHub\n\nЧем помочь?",
    MainMenuIntent.UNKNOWN: "Действие недоступно",
}


def resolve_main_menu_callback(callback_data: str) -> MainMenuIntent:
    """Преобразует callback-data главного меню в intent."""

    return _MAIN_MENU_CALLBACKS.get(callback_data, MainMenuIntent.UNKNOWN)


def get_main_menu_response_text(intent: MainMenuIntent) -> str:
    """Возвращает текст ответа для выбранного intent главного меню."""

    return MAIN_MENU_RESPONSE_TEXTS.get(
        intent,
        MAIN_MENU_RESPONSE_TEXTS[MainMenuIntent.UNKNOWN],
    )
