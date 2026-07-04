"""Сборка reply-меню бота."""

from telegram import ReplyKeyboardMarkup

from src.core.logger import logger

BTN_MAIN_MENU = "🏠 Главное меню"
BTN_BACK = "⬅️ Назад"

BTN_PLAY = "🎮 Играть"
BTN_SHOP = "🛍 Магазин"
BTN_SETTINGS = "⚙️ Настройки"
BTN_SUPPORT = "🆘 Поддержка"

BTN_ADMIN_USERS = "Пользователи"
BTN_ADMIN_STATS = "Статистика"
BTN_ADMIN_EXPORT = "Экспорт CSV"
BTN_ADMIN_NOTIFY = "Новостная рассылка"
BTN_ADMIN_RIGHTS = "Права админов"

BTN_SHOP_PROFILES = "👤 Профили"
BTN_SHOP_THEMES = "🎨 Оформление"
BTN_SHOP_PREMIUM = "💎 Премиум"
BTN_SHOP_PROMO = "🎁 Промокод"
BTN_SHOP_AVATARS = "🖼 Аватарки"
BTN_SHOP_TITLES = "🏷 Титулы"
BTN_SHOP_DARK = "🌙 Тёмные стили"
BTN_SHOP_EFFECTS = "✨ Эффекты"
BTN_SHOP_BUY_PREMIUM = "💎 Купить премиум"
BTN_SHOP_PREMIUM_INFO = "📋 Что входит?"

BTN_SETTINGS_PROFILE = "👤 Профиль"
BTN_SETTINGS_NOTIFICATIONS = "🔔 Уведомления"
BTN_SETTINGS_LANGUAGE = "🌐 Язык"
BTN_SETTINGS_SAFETY = "🛡 Безопасность"
BTN_PROFILE_NAME = "✏️ Имя"
BTN_PROFILE_BIO = "📝 Описание"
BTN_NOTIF_LOBBY = "✅ Лобби: Вкл"
BTN_NOTIF_INVITES = "✅ Приглашения: Вкл"
BTN_LANGUAGE_RU = "🇷🇺 Русский"
BTN_NAME_LATER = "⏭ Позже"
BTN_SAFETY_BLACKLIST = "🚫 Чёрный список"
BTN_SAFETY_PRIVACY = "👁 Приватность профиля"
BTN_SAFETY_REPORTS = "⚠️ Жалобы"

BTN_SUPPORT_FAQ = "❓ FAQ"
BTN_SUPPORT_BUG = "🐞 Сообщить об ошибке"
BTN_SUPPORT_ADMIN = "👤 Связаться с админом"
BTN_SUPPORT_RULES = "📜 Правила"
BTN_FAQ_PLAY = "🎮 Как играть?"
BTN_FAQ_LOBBY = "🏠 Что такое лобби?"
BTN_FAQ_SHOP = "🛍 Как работает магазин?"


def _build_reply_keyboard(button_rows: list[list[str]]) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        button_rows,
        resize_keyboard=True,
        input_field_placeholder="Выбери действие",
    )


def _with_nav(rows: list[list[str]], include_back: bool = True) -> list[list[str]]:
    nav = []
    if include_back:
        nav.append(BTN_BACK)
    nav.append(BTN_MAIN_MENU)
    return rows + [nav]


def build_main_menu() -> ReplyKeyboardMarkup:
    return getMainMenuKeyboard()


def build_admin_panel() -> ReplyKeyboardMarkup:
    logger.info("build_admin_panel")
    return _build_reply_keyboard(
        [
            [BTN_ADMIN_USERS],
            [BTN_ADMIN_STATS, BTN_ADMIN_EXPORT],
            [BTN_ADMIN_NOTIFY],
            [BTN_ADMIN_RIGHTS],
            [BTN_MAIN_MENU],
        ]
    )


def getMainMenuKeyboard() -> ReplyKeyboardMarkup:
    return _build_reply_keyboard(
        [
            [BTN_PLAY],
            [BTN_SHOP],
            [BTN_SETTINGS, BTN_SUPPORT],
        ]
    )


def getShopKeyboard() -> ReplyKeyboardMarkup:
    return _build_reply_keyboard(_with_nav([[BTN_SHOP_PROFILES], [BTN_SHOP_THEMES], [BTN_SHOP_PREMIUM], [BTN_SHOP_PROMO]]))


def getShopProfilesKeyboard() -> ReplyKeyboardMarkup:
    return _build_reply_keyboard(_with_nav([[BTN_SHOP_AVATARS], [BTN_SHOP_TITLES]]))


def getShopThemesKeyboard() -> ReplyKeyboardMarkup:
    return _build_reply_keyboard(_with_nav([[BTN_SHOP_DARK], [BTN_SHOP_EFFECTS]]))


def getShopPremiumKeyboard() -> ReplyKeyboardMarkup:
    return _build_reply_keyboard(_with_nav([[BTN_SHOP_BUY_PREMIUM], [BTN_SHOP_PREMIUM_INFO]]))


def getSettingsKeyboard() -> ReplyKeyboardMarkup:
    return _build_reply_keyboard(
        _with_nav(
            [
                [BTN_SETTINGS_PROFILE],
                [BTN_SETTINGS_NOTIFICATIONS],
                [BTN_SETTINGS_LANGUAGE],
                [BTN_SETTINGS_SAFETY],
            ]
        )
    )


def getSettingsProfileKeyboard() -> ReplyKeyboardMarkup:
    return _build_reply_keyboard(_with_nav([[BTN_PROFILE_NAME], [BTN_PROFILE_BIO]]))


def getSettingsNotificationsKeyboard(userSettings=None) -> ReplyKeyboardMarkup:
    news_enabled = True
    if userSettings is not None:
        news_enabled = bool(getattr(userSettings, "news_notifications_enabled", True))

    news_label = "✅ Новости: Вкл" if news_enabled else "❌ Новости: Выкл"
    return _build_reply_keyboard(
        _with_nav(
            [
                [BTN_NOTIF_LOBBY],
                [BTN_NOTIF_INVITES],
                [news_label],
            ]
        )
    )


def getSettingsLanguageKeyboard() -> ReplyKeyboardMarkup:
    return _build_reply_keyboard(_with_nav([[BTN_LANGUAGE_RU]]))


def getSettingsSafetyKeyboard() -> ReplyKeyboardMarkup:
    return _build_reply_keyboard(_with_nav([[BTN_SAFETY_BLACKLIST], [BTN_SAFETY_PRIVACY], [BTN_SAFETY_REPORTS]]))


def getNamePromptKeyboard() -> ReplyKeyboardMarkup:
    return _build_reply_keyboard([[BTN_NAME_LATER], [BTN_MAIN_MENU]])


def getSupportKeyboard() -> ReplyKeyboardMarkup:
    return _build_reply_keyboard(
        _with_nav(
            [
                [BTN_SUPPORT_FAQ],
                [BTN_SUPPORT_BUG],
                [BTN_SUPPORT_ADMIN],
                [BTN_SUPPORT_RULES],
            ]
        )
    )


def getSupportFaqKeyboard() -> ReplyKeyboardMarkup:
    return _build_reply_keyboard(_with_nav([[BTN_FAQ_PLAY], [BTN_FAQ_LOBBY], [BTN_FAQ_SHOP]]))


def getBackToMenuKeyboard(back_target: str) -> ReplyKeyboardMarkup:
    return _build_reply_keyboard([[BTN_BACK], [BTN_MAIN_MENU]])
