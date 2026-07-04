"""Роли для RP-режима по темам."""

ROLE_PAGE_SIZE = 10


def _slug(name: str) -> str:
    return (
        name.lower()
        .replace("&", "and")
        .replace(".", "")
        .replace("-", "_")
        .replace(" ", "_")
        .replace("'", "")
    )


BRAWL_STARS_ROLE_NAMES = [
    ("8-Bit", "8-Бит"),
    ("Alli", "Алли"),
    ("Amber", "Амбер"),
    ("Angelo", "Анджело"),
    ("Ash", "Эш"),
    ("Barley", "Барли"),
    ("Bea", "Беа"),
    ("Belle", "Белль"),
    ("Berry", "Берри"),
    ("Bibi", "Биби"),
    ("Bo", "Бо"),
    ("Bolt", "Болт"),
    ("Bonnie", "Бонни"),
    ("Brock", "Брок"),
    ("Bull", "Булл"),
    ("Buster", "Бастер"),
    ("Buzz", "Базз"),
    ("Buzz Lightyear", "Базз Лайтйир"),
    ("Byron", "Байрон"),
    ("Carl", "Карл"),
    ("Charlie", "Чарли"),
    ("Chester", "Честер"),
    ("Chuck", "Чак"),
    ("Clancy", "Клэнси"),
    ("Colette", "Колетт"),
    ("Colt", "Кольт"),
    ("Cordelius", "Корделиус"),
    ("Crow", "Кроу"),
    ("Damian", "Дамиан"),
    ("Darryl", "Дэррил"),
    ("Doug", "Даг"),
    ("Draco", "Драко"),
    ("Dynamike", "Динамайк"),
    ("Edgar", "Эдгар"),
    ("El Primo", "Эль Примо"),
    ("Emz", "Эмз"),
    ("Eve", "Ив"),
    ("Fang", "Фэнг"),
    ("Finx", "Финкс"),
    ("Frank", "Фрэнк"),
    ("Gale", "Гейл"),
    ("Gene", "Джин"),
    ("Gigi", "Джиджи"),
    ("Glowy", "Глоуи"),
    ("Gray", "Грей"),
    ("Griff", "Грифф"),
    ("Grom", "Гром"),
    ("Gus", "Гас"),
    ("Hank", "Хэнк"),
    ("Jacky", "Джеки"),
    ("Jae-Yong", "Дже-Йонг"),
    ("Janet", "Джанет"),
    ("Jessie", "Джесси"),
    ("Juju", "Джуджу"),
    ("Kaze", "Казе"),
    ("Kenji", "Кенджи"),
    ("Kit", "Кит"),
    ("Larry & Lawrie", "Ларри и Лори"),
    ("Leon", "Леон"),
    ("Lily", "Лили"),
    ("Lola", "Лола"),
    ("Lou", "Лу"),
    ("Lumi", "Луми"),
    ("Maisie", "Мэйси"),
    ("Mandy", "Мэнди"),
    ("Max", "Макс"),
    ("Meeple", "Мипл"),
    ("Meg", "Мэг"),
    ("Melodie", "Мелоди"),
    ("Mico", "Мико"),
    ("Mina", "Мина"),
    ("Moe", "Мо"),
    ("Mortis", "Мортис"),
    ("Mr. P", "Мистер Пи"),
    ("Najia", "Наджия"),
    ("Nani", "Нани"),
    ("Nita", "Нита"),
    ("Nori", "Нори"),
    ("Ollie", "Олли"),
    ("Otis", "Отис"),
    ("Pam", "Пэм"),
    ("Pearl", "Перл"),
    ("Penny", "Пенни"),
    ("Pierce", "Пирс"),
    ("Piper", "Пайпер"),
    ("Poco", "Поко"),
    ("R-T", "Ар-Ти"),
    ("Rico", "Рико"),
    ("Rosa", "Роза"),
    ("Ruffs", "Раффс"),
    ("Sam", "Сэм"),
    ("Sandy", "Сэнди"),
    ("Shade", "Шейд"),
    ("Shelly", "Шелли"),
    ("Sirius", "Сириус"),
    ("Spike", "Спайк"),
    ("Sprout", "Спраут"),
    ("Squeak", "Сквик"),
    ("Starr Nova", "Старр Нова"),
    ("Stu", "Сту"),
    ("Surge", "Сёрдж"),
    ("Tara", "Тара"),
    ("Tick", "Тик"),
    ("Trunk", "Транк"),
    ("Wendy", "Венди"),
    ("Willow", "Виллоу"),
    ("Ziggy", "Зигги"),
]

MLP_ROLE_NAMES = [
    ("Adagio Dazzle", "Адажио Даззл"),
    ("Apple Bloom", "Эппл Блум"),
    ("Applejack", "Эпплджек"),
    ("Aria Blaze", "Ария Блейз"),
    ("Autumn Blaze", "Отэм Блейз"),
    ("Big McIntosh", "Биг Макинтош"),
    ("Bon Bon", "Бон Бон"),
    ("Braeburn", "Брейбёрн"),
    ("Bright Mac", "Брайт Мак"),
    ("Cadance", "Кейденс"),
    ("Capper", "Кэппер"),
    ("Cheese Sandwich", "Чиз Сэндвич"),
    ("Cheerilee", "Черили"),
    ("Chrysalis", "Кризалис"),
    ("Coco Pommel", "Коко Поммел"),
    ("Cozy Glow", "Коузи Глоу"),
    ("Derpy Hooves", "Дёрпи Хувз"),
    ("Diamond Tiara", "Даймонд Тиара"),
    ("Discord", "Дискорд"),
    ("DJ Pon-3", "Ди-Джей Пон-3"),
    ("Ember", "Эмбер"),
    ("Fancy Pants", "Фэнси Пэнтс"),
    ("Featherweight", "Фезервейт"),
    ("Filthy Rich", "Филти Рич"),
    ("Flam", "Флэм"),
    ("Flash Sentry", "Флэш Сентри"),
    ("Flim", "Флим"),
    ("Flurry Heart", "Фларри Харт"),
    ("Fluttershy", "Флаттершай"),
    ("Gallus", "Галлус"),
    ("Gilda", "Гилда"),
    ("Granny Smith", "Грэнни Смит"),
    ("Grogar", "Грогар"),
    ("Gusty", "Гасти"),
    ("Hoity Toity", "Хойти Тойти"),
    ("King Sombra", "Кинг Сомбра"),
    ("Limestone Pie", "Лаймстоун Пай"),
    ("Lord Tirek", "Лорд Тирек"),
    ("Lyra Heartstrings", "Лира Хартстрингс"),
    ("Maud Pie", "Мод Пай"),
    ("Mayor Mare", "Мэйор Мэр"),
    ("Minuette", "Минюэт"),
    ("Mistmane", "Мистмейн"),
    ("Moondancer", "Мунденсер"),
    ("Nightmare Moon", "Найтмэр Мун"),
    ("Ocellus", "Оцеллус"),
    ("Octavia Melody", "Октавия Мелоди"),
    ("Pear Butter", "Пэр Баттер"),
    ("Pharynx", "Фаринкс"),
    ("Pinkie Pie", "Пинки Пай"),
    ("Princess Celestia", "Принцесс Селестия"),
    ("Princess Luna", "Принцесс Луна"),
    ("Queen Novo", "Квин Ново"),
    ("Rainbow Dash", "Рэйнбоу Дэш"),
    ("Rara", "Рара"),
    ("Rarity", "Рэрити"),
    ("Sandbar", "Сэндбар"),
    ("Sapphire Shores", "Сапфайр Шорс"),
    ("Scootaloo", "Скуталу"),
    ("Shining Armor", "Шайнинг Армор"),
    ("Silver Spoon", "Сильвер Спун"),
    ("Silverstream", "Сильверстрим"),
    ("Smolder", "Смолдер"),
    ("Snails", "Снейлс"),
    ("Snips", "Снипс"),
    ("Soarin", "Соарин"),
    ("Somnambula", "Сомнамбула"),
    ("Sonata Dusk", "Соната Даск"),
    ("Spike", "Спайк"),
    ("Spitfire", "Спитфайр"),
    ("Starlight Glimmer", "Старлайт Глиммер"),
    ("Starswirl the Bearded", "Старсвирл зе Бирдед"),
    ("Sugar Belle", "Шугар Белль"),
    ("Sunburst", "Санбёрст"),
    ("Sunset Shimmer", "Сансет Шиммер"),
    ("Sweetie Belle", "Свити Белль"),
    ("Tempest Shadow", "Темпест Шэдоу"),
    ("Thorax", "Торакс"),
    ("Trixie Lulamoon", "Трикси Луламун"),
    ("Twilight Sparkle", "Твайлайт Спаркл"),
    ("Vapor Trail", "Вейпор Трейл"),
    ("Yona", "Йона"),
    ("Zecora", "Зекора"),
    ("Zephyr Breeze", "Зефир Бриз"),
]


ROLE_ORIGINAL_NAMES_BY_TOPIC = {
    "brawl_stars": {_slug(original): original for original, _label in BRAWL_STARS_ROLE_NAMES},
    "mlp": {_slug(original): original for original, _label in MLP_ROLE_NAMES},
}

ROLES_BY_TOPIC = {
    "brawl_stars": dict(
        sorted(
            ((_slug(original), label) for original, label in BRAWL_STARS_ROLE_NAMES),
            key=lambda item: item[1].casefold(),
        )
    ),
    "mlp": dict(
        sorted(
            ((_slug(original), label) for original, label in MLP_ROLE_NAMES),
            key=lambda item: item[1].casefold(),
        )
    ),
}

def get_role_original_name(topic: str | None, role: str | None) -> str:
    if not topic or not role:
        return ""
    return ROLE_ORIGINAL_NAMES_BY_TOPIC.get(topic, {}).get(role, "")


def search_roles(topic: str | None, query: str, taken_roles: set[str] | None = None) -> list[tuple[str, str]]:
    if not topic:
        return []

    normalized_query = query.casefold().strip()
    if not normalized_query:
        return []

    taken_roles = taken_roles or set()
    results = []
    for role, label in ROLES_BY_TOPIC.get(topic, {}).items():
        if role in taken_roles:
            continue
        original = get_role_original_name(topic, role)
        haystack = f"{label} {original} {role.replace('_', ' ')}".casefold()
        if normalized_query in haystack:
            results.append((role, label))
    return results
