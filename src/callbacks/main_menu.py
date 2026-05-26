from enum import Enum


class MainMenuIntent(str, Enum):
    """Понятные имена действий, которые может выбрать пользователь в главном меню."""

    REGISTER = "REGISTER"
    PROFILE = "PROFILE"
    LOBBY = "LOBBY"
    HELP = "HELP"
    UNKNOWN = "UNKNOWN"


# Единый контракт callback-data главного меню.
# Клавиатура должна отправлять эти строки, а handler будет получать готовый intent.
_MAIN_MENU_CALLBACKS = {
    "main:register": MainMenuIntent.REGISTER,
    "main:profile": MainMenuIntent.PROFILE,
    "main:lobby": MainMenuIntent.LOBBY,
    "main:help": MainMenuIntent.HELP,
}


# Тексты держим рядом с router'ом, пока проект маленький.
# Так handler сможет просто выбрать intent и взять готовый ответ.
MAIN_MENU_RESPONSE_TEXTS = {
    MainMenuIntent.REGISTER: (
        "Регистрация скоро стартует. "
        "Это будет первый шаг входа в RoleHub-лобби."
    ),
    MainMenuIntent.PROFILE: (
        "Профиль пока не заполнен. "
        "После регистрации здесь появятся данные участника."
    ),
    MainMenuIntent.LOBBY: (
        "Лобби готовится. "
        "Скоро здесь будет список доступных RP-комнат."
    ),
    MainMenuIntent.HELP: (
        "RoleHub помогает найти RP-лобби и подготовить профиль участника. "
        "Сейчас доступны базовые разделы: регистрация, профиль, лобби и помощь."
    ),
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