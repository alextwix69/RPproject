"""Роли для RP-режима по темам."""

ROLES_BY_TOPIC = {
    "brawl_stars": {
        "hero": "Герой",
        "fighter": "Боец",
        "strategist": "Стратег",
    },
    "mlp": {
        "pony": "Пони",
        "mage": "Маг",
        "friend": "Друг",
    },
    "roblox": {
        "player": "Игрок",
        "creator": "Создатель",
        "explorer": "Исследователь",
    },
}

ROLE_BUTTONS_BY_TOPIC = {
    "brawl_stars": [
        ("🛡 Герой", "create:role:hero"),
        ("💥 Боец", "create:role:fighter"),
        ("🧠 Стратег", "create:role:strategist"),
    ],
    "mlp": [
        ("🦄 Пони", "create:role:pony"),
        ("✨ Маг", "create:role:mage"),
        ("🌈 Друг", "create:role:friend"),
    ],
    "roblox": [
        ("🧱 Игрок", "create:role:player"),
        ("👑 Создатель", "create:role:creator"),
        ("🗺 Исследователь", "create:role:explorer"),
    ],
}
