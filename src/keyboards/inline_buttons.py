"""
Inline-кнопки и стабильные callback-data для навигации RoleHub.
"""

MENU_MAIN_CALLBACK = "menu:main"
MENU_PLAY_CALLBACK = "menu:play"
MENU_SHOP_CALLBACK = "menu:shop"
MENU_SETTINGS_CALLBACK = "menu:settings"
MENU_SUPPORT_CALLBACK = "menu:support"

from src.constants.topics import TOPICS

PLAY_ACTIONS = {
    "find": "Найти лобби",
    "create": "Создать лобби",
    "quick": "Быстрый вход",
    "code": "Войти по коду",
    "rooms": "Список комнат",
}

MAIN_MENU_BUTTONS = [
    [("🎮 Играть", MENU_PLAY_CALLBACK)],
    [("🛍 Магазин", MENU_SHOP_CALLBACK)],
    [
        ("⚙️ Настройки", MENU_SETTINGS_CALLBACK),
        ("🆘 Поддержка", MENU_SUPPORT_CALLBACK),
    ],
]

PLAY_TOPICS_BUTTONS = [
    [("⭐ Brawl Stars", "play:topic:brawl_stars")],
    [("🦄 My Little Pony", "play:topic:mlp")],
    [("⬅️ Назад", MENU_MAIN_CALLBACK)],
]

SHOP_BUTTONS = [
    [("👤 Профили", "shop:profiles")],
    [("🎨 Оформление", "shop:themes")],
    [("💎 Премиум", "shop:premium")],
    [("🎁 Промокод", "shop:promo")],
    [("⬅️ Назад", MENU_MAIN_CALLBACK)],
]

SHOP_PROFILES_BUTTONS = [
    [("🖼 Аватарки", "shop:profiles:avatars")],
    [("🏷 Титулы", "shop:profiles:titles")],
    [("⬅️ Назад", "shop:back"), ("🏠 Меню", MENU_MAIN_CALLBACK)],
]

SHOP_THEMES_BUTTONS = [
    [("🌙 Тёмные стили", "shop:themes:dark")],
    [("✨ Эффекты", "shop:themes:effects")],
    [("⬅️ Назад", "shop:back"), ("🏠 Меню", MENU_MAIN_CALLBACK)],
]

SHOP_PREMIUM_BUTTONS = [
    [("💎 Купить премиум", "shop:premium:buy")],
    [("📋 Что входит?", "shop:premium:info")],
    [("⬅️ Назад", "shop:back"), ("🏠 Меню", MENU_MAIN_CALLBACK)],
]

SETTINGS_BUTTONS = [
    [("👤 Профиль", "settings:profile")],
    [("🔔 Уведомления", "settings:notifications")],
    [("🌐 Язык", "settings:language")],
    [("🛡 Безопасность", "settings:safety")],
    [("⬅️ Назад", MENU_MAIN_CALLBACK)],
]

SETTINGS_PROFILE_BUTTONS = [
    [("✏️ Имя", "settings:profile:name")],
    [("📝 Описание", "settings:profile:bio")],
    [("⬅️ Назад", "settings:back"), ("🏠 Меню", MENU_MAIN_CALLBACK)],
]

SETTINGS_NOTIFICATIONS_BUTTONS = [
    [("✅ Лобби: Вкл", "settings:notif:lobby")],
    [("✅ Приглашения: Вкл", "settings:notif:invites")],
    [("✅ Новости: Вкл", "settings:notif:news")],
    [("⬅️ Назад", "settings:back"), ("🏠 Меню", MENU_MAIN_CALLBACK)],
]

SETTINGS_LANGUAGE_BUTTONS = [
    [("🇷🇺 Русский", "settings:lang:ru")],
    [("⬅️ Назад", "settings:back"), ("🏠 Меню", MENU_MAIN_CALLBACK)],
]

NAME_PROMPT_BUTTONS = [
    [("⏭ Позже", "settings:name_later")],
    [("🏠 Главное меню", MENU_MAIN_CALLBACK)],
]

SETTINGS_SAFETY_BUTTONS = [
    [("🚫 Чёрный список", "settings:safety:blacklist")],
    [("👁 Приватность профиля", "settings:safety:privacy")],
    [("⚠️ Жалобы", "settings:safety:reports")],
    [("⬅️ Назад", "settings:back"), ("🏠 Меню", MENU_MAIN_CALLBACK)],
]

SUPPORT_BUTTONS = [
    [("❓ FAQ", "support:faq")],
    [("🐞 Сообщить об ошибке", "support:bug")],
    [("👤 Связаться с админом", "support:admin")],
    [("📜 Правила", "support:rules")],
    [("⬅️ Назад", MENU_MAIN_CALLBACK)],
]

SUPPORT_FAQ_BUTTONS = [
    [("🎮 Как играть?", "support:faq:play")],
    [("🏠 Что такое лобби?", "support:faq:lobby")],
    [("🛍 Как работает магазин?", "support:faq:shop")],
    [("⬅️ Назад", "support:back"), ("🏠 Меню", MENU_MAIN_CALLBACK)],
]
