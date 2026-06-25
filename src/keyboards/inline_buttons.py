"""
Общие inline-кнопки и callback-data.

Каждая кнопка хранится как пара: видимый текст и стабильный callback_data.
"""

MAIN_PLAY_CALLBACK = "main:play"
MAIN_SHOP_CALLBACK = "main:shop"
MAIN_SETTINGS_CALLBACK = "main:settings"
MAIN_SUPPORT_CALLBACK = "main:support"

THEME_BRAWL_STARS_CALLBACK = "theme:brawl_stars"
THEME_MY_LITTLE_PONY_CALLBACK = "theme:my_little_pony"
THEME_ROBLOX_CALLBACK = "theme:roblox"
THEME_BACK_CALLBACK = "theme:back"

ADMIN_1_CALLBACK = "admin:admin1"
ADMIN_2_CALLBACK = "admin:admin2"
ADMIN_3_CALLBACK = "admin:admin3"

MAIN_MENU_BUTTONS = [
    [("Играть 🎮", MAIN_PLAY_CALLBACK)],
    [("Магазин 🛍️", MAIN_SHOP_CALLBACK)],
    [
        ("Настройки ⚙️", MAIN_SETTINGS_CALLBACK),
        ("Поддержка 🆘", MAIN_SUPPORT_CALLBACK),
    ],
]

ADMIN_PANEL_BUTTONS = [
    [("admin1", ADMIN_1_CALLBACK)],
    [("admin2", ADMIN_2_CALLBACK), ("admin3", ADMIN_3_CALLBACK)],
]

CHOOSE_THEME_BUTTONS = [
    [("brawl stars", THEME_BRAWL_STARS_CALLBACK)],
    [("my little pony", THEME_MY_LITTLE_PONY_CALLBACK)],
    [("roblox", THEME_ROBLOX_CALLBACK)],
    [("Назад", THEME_BACK_CALLBACK)],
]

THEME_TITLES = {
    THEME_BRAWL_STARS_CALLBACK: "brawl stars",
    THEME_MY_LITTLE_PONY_CALLBACK: "my little pony",
    THEME_ROBLOX_CALLBACK: "roblox",
}
