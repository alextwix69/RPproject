"""Сборка reply-меню бота."""

from telegram import ReplyKeyboardMarkup

from src.core.logger import logger

BTN_MAIN_MENU = "🏰 Главное меню"
BTN_BACK = "↩️ Назад"

BTN_PLAY = "🌌 Войти в мир"
BTN_FRIENDS = "🤝 Друзья и герои"
BTN_SHOP = "💎 Лавка сокровищ"
BTN_SETTINGS = "⚙️ Настройки героя"
BTN_SUPPORT = "🪄 Магическая поддержка"
BTN_RETURN_TO_ACTIVE_LOBBY = "↩️ Вернуться в свой мир"

BTN_ADMIN_USERS = "👥 Пользователи"
BTN_ADMIN_STATS = "📊 Статистика"
BTN_ADMIN_EXPORT = "📜 Экспорт CSV"
BTN_ADMIN_NOTIFY = "📣 Новостная рассылка"
BTN_ADMIN_RIGHTS = "👑 Права админов"

BTN_SHOP_PROFILES = "🪞 Образы профиля"
BTN_SHOP_THEMES = "🎨 Магия оформления"
BTN_SHOP_PREMIUM = "💎 RoleHub Premium"
BTN_SHOP_PROMO = "🎁 Волшебный промокод"
BTN_SHOP_AVATARS = "🖼 Волшебные аватарки"
BTN_SHOP_TITLES = "👑 Титулы героев"
BTN_SHOP_DARK = "🌙 Ночные стили"
BTN_SHOP_EFFECTS = "✨ Магические эффекты"
BTN_SHOP_BUY_PREMIUM = "💎 Получить Premium"
BTN_SHOP_PREMIUM_INFO = "📜 Что дарит Premium?"

BTN_SETTINGS_PROFILE = "👤 Профиль героя"
BTN_SETTINGS_NOTIFICATIONS = "🔔 Волшебные весточки"
BTN_SETTINGS_LANGUAGE = "🌐 Язык мира"
BTN_SETTINGS_SAFETY = "🛡 Щит безопасности"
BTN_PROFILE_NAME = "✍️ Имя героя"
BTN_PROFILE_AVATAR = "🖼 Аватар героя"
BTN_PROFILE_BIO = "📖 История героя"
BTN_FIND_FRIEND = "🔎 Найти героя"
BTN_VIEW_FOUND_PROFILE = "👤 Открыть профиль"
BTN_ADD_FOUND_FRIEND = "🤝 Добавить в друзья"
BTN_SEARCH_FRIEND_AGAIN = "🌟 Искать ещё"
BTN_NOTIF_LOBBY = "✅ Миры: Вкл"
BTN_NOTIF_INVITES = "✅ Приглашения: Вкл"
BTN_LANGUAGE_RU = "🇷🇺 Русский"
BTN_NAME_LATER = "⏭ Выбрать позже"
BTN_SAFETY_BLACKLIST = "🚫 Чёрный свиток"
BTN_SAFETY_PRIVACY = "👁 Тайны профиля"
BTN_SAFETY_REPORTS = "⚠️ Отправить жалобу"

BTN_SUPPORT_FAQ = "📚 Книга ответов"
BTN_SUPPORT_BUG = "🐞 Сообщить о магическом сбое"
BTN_SUPPORT_ADMIN = "👑 Связаться с администратором"
BTN_SUPPORT_RULES = "📜 Законы королевства"
BTN_FAQ_PLAY = "🌌 Как войти в мир?"
BTN_FAQ_LOBBY = "🏰 Что такое лобби?"
BTN_FAQ_SHOP = "💎 Как работает лавка?"

LEGACY_BUTTON_ALIASES = {
    "🏠 Главное меню": BTN_MAIN_MENU,
    "⬅️ Назад": BTN_BACK,
    "🎮 Играть": BTN_PLAY,
    "👥 Друзья": BTN_FRIENDS,
    "🛍 Магазин": BTN_SHOP,
    "⚙️ Настройки": BTN_SETTINGS,
    "🆘 Поддержка": BTN_SUPPORT,
    "↩️ Вернуться в активное лобби": BTN_RETURN_TO_ACTIVE_LOBBY,
    "Пользователи": BTN_ADMIN_USERS,
    "Статистика": BTN_ADMIN_STATS,
    "Экспорт CSV": BTN_ADMIN_EXPORT,
    "Новостная рассылка": BTN_ADMIN_NOTIFY,
    "Права админов": BTN_ADMIN_RIGHTS,
    "👤 Профили": BTN_SHOP_PROFILES,
    "🎨 Оформление": BTN_SHOP_THEMES,
    "💎 Премиум": BTN_SHOP_PREMIUM,
    "🎁 Промокод": BTN_SHOP_PROMO,
    "🖼 Аватарки": BTN_SHOP_AVATARS,
    "🏷 Титулы": BTN_SHOP_TITLES,
    "🌙 Тёмные стили": BTN_SHOP_DARK,
    "✨ Эффекты": BTN_SHOP_EFFECTS,
    "💎 Купить премиум": BTN_SHOP_BUY_PREMIUM,
    "📋 Что входит?": BTN_SHOP_PREMIUM_INFO,
    "👤 Профиль": BTN_SETTINGS_PROFILE,
    "🔔 Уведомления": BTN_SETTINGS_NOTIFICATIONS,
    "🌐 Язык": BTN_SETTINGS_LANGUAGE,
    "🛡 Безопасность": BTN_SETTINGS_SAFETY,
    "✏️ Имя": BTN_PROFILE_NAME,
    "🖼 Аватар": BTN_PROFILE_AVATAR,
    "📝 Описание": BTN_PROFILE_BIO,
    "🔎 Найти друга": BTN_FIND_FRIEND,
    "👤 Посмотреть профиль": BTN_VIEW_FOUND_PROFILE,
    "➕ Добавить друга": BTN_ADD_FOUND_FRIEND,
    "🔁 Искать ещё": BTN_SEARCH_FRIEND_AGAIN,
    "✅ Лобби: Вкл": BTN_NOTIF_LOBBY,
    "⏭ Позже": BTN_NAME_LATER,
    "🚫 Чёрный список": BTN_SAFETY_BLACKLIST,
    "👁 Приватность профиля": BTN_SAFETY_PRIVACY,
    "⚠️ Жалобы": BTN_SAFETY_REPORTS,
    "❓ FAQ": BTN_SUPPORT_FAQ,
    "🐞 Сообщить об ошибке": BTN_SUPPORT_BUG,
    "👤 Связаться с админом": BTN_SUPPORT_ADMIN,
    "👤 Связаться с администратором": BTN_SUPPORT_ADMIN,
    "📜 Правила": BTN_SUPPORT_RULES,
    "🎮 Как играть?": BTN_FAQ_PLAY,
    "🏠 Что такое лобби?": BTN_FAQ_LOBBY,
    "🛍 Как работает магазин?": BTN_FAQ_SHOP,
}


def normalize_button_text(text: str) -> str:
    return LEGACY_BUTTON_ALIASES.get(text, text)


def _build_reply_keyboard(button_rows: list[list[str]]) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        button_rows,
        resize_keyboard=True,
        input_field_placeholder="Выбери свой путь ✨",
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


def getMainMenuKeyboard(include_return_to_lobby: bool = False) -> ReplyKeyboardMarkup:
    rows = []
    if include_return_to_lobby:
        rows.append([BTN_RETURN_TO_ACTIVE_LOBBY])
    rows.extend(
        [
            [BTN_PLAY],
            [BTN_FRIENDS],
            [BTN_SHOP],
            [BTN_SETTINGS, BTN_SUPPORT],
        ]
    )
    return _build_reply_keyboard(
        rows
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
    return _build_reply_keyboard(_with_nav([[BTN_PROFILE_NAME], [BTN_PROFILE_AVATAR], [BTN_PROFILE_BIO]]))


def getFriendsKeyboard() -> ReplyKeyboardMarkup:
    return _build_reply_keyboard(_with_nav([[BTN_FIND_FRIEND]]))


def getFriendSearchPromptKeyboard() -> ReplyKeyboardMarkup:
    return _build_reply_keyboard(_with_nav([]))


def getFoundFriendKeyboard() -> ReplyKeyboardMarkup:
    return _build_reply_keyboard(
        _with_nav(
            [
                [BTN_VIEW_FOUND_PROFILE],
                [BTN_ADD_FOUND_FRIEND],
                [BTN_SEARCH_FRIEND_AGAIN],
            ]
        )
    )


def getSettingsNotificationsKeyboard(userSettings=None) -> ReplyKeyboardMarkup:
    news_enabled = True
    if userSettings is not None:
        news_enabled = bool(getattr(userSettings, "news_notifications_enabled", True))

    news_label = "✅ Вести королевства: Вкл" if news_enabled else "❌ Вести королевства: Выкл"
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
    return _build_reply_keyboard(_with_nav([[BTN_SUPPORT_ADMIN]]))


def getSupportFaqKeyboard() -> ReplyKeyboardMarkup:
    return _build_reply_keyboard(_with_nav([[BTN_FAQ_PLAY], [BTN_FAQ_LOBBY], [BTN_FAQ_SHOP]]))


def getBackToMenuKeyboard(back_target: str) -> ReplyKeyboardMarkup:
    return _build_reply_keyboard([[BTN_BACK], [BTN_MAIN_MENU]])
