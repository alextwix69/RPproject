"""Рендер экранов reply-навигации RoleHub."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update

from src.keyboards.kb_build import (
    getBackToMenuKeyboard,
    getFoundFriendKeyboard,
    getFriendSearchPromptKeyboard,
    getFriendsKeyboard,
    getMainMenuKeyboard,
    getNamePromptKeyboard,
    getSettingsKeyboard,
    getSettingsLanguageKeyboard,
    getSettingsNotificationsKeyboard,
    getSettingsProfileKeyboard,
    getSettingsSafetyKeyboard,
    getShopKeyboard,
    getShopPremiumKeyboard,
    getShopProfilesKeyboard,
    getShopThemesKeyboard,
    getSupportFaqKeyboard,
    getSupportKeyboard,
)
from src.keyboards.lobby_keyboard import get_play_main_reply_keyboard
from src.core.database import get_session
from src.render.lobby_render import render_play_main
from src.repositories import lobby_member_repo, lobby_repo
from src.services.chat_cleanup_service import remember_telegram_message
from src.services.user_service import ensure_from_effective_user


MAIN_MENU_TEXT = (
    "✨👑 Добро пожаловать в RoleHub, герой!\n\n"
    "Здесь открываются двери в любимые вселенные 🌌\n"
    "Выбирай свой путь:"
)
SUPPORT_ADMIN_USERNAME = "sanyasigma2006"
SUPPORT_ADMIN_URL = f"https://t.me/{SUPPORT_ADMIN_USERNAME}"


async def _render(update: Update, text: str, reply_markup=None) -> None:
    message = update.effective_message
    if message is not None:
        if isinstance(reply_markup, (ReplyKeyboardMarkup, ReplyKeyboardRemove)):
            sent_message = await message.reply_text(text, reply_markup=reply_markup)
            remember_telegram_message(sent_message, is_active_screen=True)
            return

        sent_message = await message.reply_text(text, reply_markup=reply_markup)
        remember_telegram_message(sent_message, is_active_screen=True)


async def showMainMenu(update: Update) -> None:
    await _render(update, MAIN_MENU_TEXT, getMainMenuKeyboard(_has_current_open_lobby(update)))


async def showFriends(update: Update) -> None:
    await _render(
        update,
        (
            "🤝✨ Зал друзей и героев\n\n"
            "Найди своего будущего союзника по имени в RoleHub или Telegram username 🌟"
        ),
        getFriendsKeyboard(),
    )


async def showFriendSearchPrompt(update: Update) -> None:
    await _render(
        update,
        (
            "🔎✨ Магический поиск героя\n\n"
            "Напиши имя в RoleHub или Telegram username — и карта миров попробует его найти 🌌"
        ),
        getFriendSearchPromptKeyboard(),
    )


async def _render_profile_card(
    update: Update,
    text: str,
    reply_markup,
    avatar_file_id: str | None = None,
) -> None:
    message = update.effective_message
    if message is None:
        return

    if avatar_file_id:
        sent_message = await message.reply_photo(
            photo=avatar_file_id,
            caption=text,
            reply_markup=reply_markup,
        )
        remember_telegram_message(sent_message, is_active_screen=True)
        return

    await _render(update, text, reply_markup)


async def showFoundFriend(
    update: Update,
    profile_text: str,
    avatar_file_id: str | None = None,
) -> None:
    await _render_profile_card(
        update,
        f"🌟 Герой найден!\n\n{profile_text}",
        getFoundFriendKeyboard(),
        avatar_file_id,
    )


async def showProfile(
    update: Update,
    profile_text: str,
    avatar_file_id: str | None = None,
) -> None:
    await _render_profile_card(
        update,
        profile_text,
        getBackToMenuKeyboard("profile"),
        avatar_file_id,
    )


async def showNamePrompt(update: Update) -> None:
    await _render(
        update,
        (
            "👑✨ Как будут звать тебя в мирах RoleHub?\n\n"
            "Напиши имя героя следующим сообщением. Оно будет связано с твоим Telegram ID "
            "и станет уникальным во всём королевстве 🌌"
        ),
        getNamePromptKeyboard(),
    )


async def showAvatarPrompt(update: Update) -> None:
    await _render(
        update,
        "🖼✨ Портрет героя\n\nОтправь фото следующим сообщением — оно украсит твой профиль 👑",
        getBackToMenuKeyboard("settings:profile"),
    )


async def showPlayTopics(update: Update) -> None:
    await _render(
        update,
        render_play_main(),
        get_play_main_reply_keyboard(_has_current_open_lobby(update)),
    )


def _has_current_open_lobby(update: Update) -> bool:
    if update.effective_user is None:
        return False

    with get_session() as session:
        user = ensure_from_effective_user(session, update.effective_user)
        if user is None or user.current_lobby_id is None:
            session.commit()
            return False

        lobby = lobby_repo.get_by_id(session, user.current_lobby_id)
        if lobby is None or lobby.status == "closed":
            session.commit()
            return False

        member = lobby_member_repo.get_joined_member(session, lobby.id, user.id)
        session.commit()
        return member is not None


async def showShop(update: Update) -> None:
    await _render(
        update,
        "💎✨ Лавка сокровищ RoleHub\n\nКакую магию ты хочешь открыть сегодня?",
        getShopKeyboard(),
    )


async def showShopProfiles(update: Update) -> None:
    await _render(
        update,
        "🪞✨ Образы профиля\n\nЗдесь появятся редкие аватарки и титулы для настоящих героев 👑",
        getShopProfilesKeyboard(),
    )


async def showShopThemes(update: Update) -> None:
    await _render(
        update,
        "🎨🌌 Магия оформления\n\nЗдесь появятся стили и эффекты для профиля и твоих миров ✨",
        getShopThemesKeyboard(),
    )


async def showShopPremium(update: Update) -> None:
    await _render(
        update,
        (
            "💎👑 RoleHub Premium\n\n"
            "Сокровища для самых ярких героев:\n"
            "✨ больше возможностей профиля\n"
            "🎨 дополнительные стили\n"
            "🌌 расширенные настройки миров"
        ),
        getShopPremiumKeyboard(),
    )


async def showSettings(update: Update) -> None:
    await _render(
        update,
        "⚙️✨ Настройки героя\n\nЧто настроим перед новым приключением?",
        getSettingsKeyboard(),
    )


async def showSettingsProfile(
    update: Update,
    profile_text: str,
    avatar_file_id: str | None = None,
) -> None:
    await _render_profile_card(
        update,
        f"{profile_text}\n\n✨ Выбери, что изменить в образе героя:",
        getSettingsProfileKeyboard(),
        avatar_file_id,
    )


async def showSettingsNotifications(update: Update, user_settings=None) -> None:
    await _render(
        update,
        "🔔✨ Волшебные весточки\n\nКакие новости из миров должны прилетать к тебе?",
        getSettingsNotificationsKeyboard(user_settings),
    )


async def showSettingsLanguage(update: Update) -> None:
    await _render(
        update,
        "🌐✨ Язык мира\n\nНа каком языке будет говорить твоё королевство?",
        getSettingsLanguageKeyboard(),
    )


async def showSettingsSafety(update: Update) -> None:
    await _render(
        update,
        "🛡✨ Щит безопасности\n\nНастрой защиту своего профиля и приключений:",
        getSettingsSafetyKeyboard(),
    )


async def showSupport(update: Update) -> None:
    await _render(
        update,
        "🪄✨ Магическая поддержка RoleHub\n\nЕсли нужна помощь, главный волшебник уже рядом:",
        getSupportKeyboard(),
    )


async def showSupportAdmin(update: Update) -> None:
    await _render(
        update,
        "👑✨ Связаться с администратором\n\nНапиши главному хранителю RoleHub — он поможет разобраться:",
        InlineKeyboardMarkup(
            [[InlineKeyboardButton(f"🪄 Написать @{SUPPORT_ADMIN_USERNAME}", url=SUPPORT_ADMIN_URL)]]
        ),
    )


async def showSupportFaq(update: Update) -> None:
    await _render(
        update,
        "📚✨ Книга ответов\n\nКакую тайну RoleHub раскрыть?",
        getSupportFaqKeyboard(),
    )


async def showComingSoon(
    update: Update,
    title: str,
    description: str,
    back_target: str,
) -> None:
    text = f"🏗✨ Здесь скоро появится новая магия!\n\n{title}"
    if description:
        text = f"{text}\n\n{description}"
    text = f"{text}\n\nЗагляни сюда позже — мастера RoleHub уже работают 👑"

    await _render(update, text, getBackToMenuKeyboard(back_target))


async def showPremiumInfo(update: Update) -> None:
    await _render(
        update,
        (
            "📜💎 Сокровища RoleHub Premium\n\n"
            "В волшебной сокровищнице планируются:\n"
            "🎨 дополнительные стили профиля\n"
            "👑 уникальные титулы\n"
            "🌌 больше настроек миров\n"
            "⚡ особые возможности в будущих приключениях"
        ),
        getBackToMenuKeyboard("shop:premium"),
    )


async def showFaqAnswer(update: Update, question: str) -> None:
    answers = {
        "play": (
            "🌌✨ Как войти в приключение?\n\n"
            "Нажми «Войти в мир», выбери любимую вселенную, а затем создай свой мир "
            "или присоединись к приключению других героев 👑"
        ),
        "lobby": (
            "🏰✨ Что такое лобби?\n\n"
            "Лобби — это маленький мир, где герои одной вселенной собираются для общения "
            "и совместных историй 🌟"
        ),
        "shop": (
            "💎✨ Как работает лавка?\n\n"
            "В лавке сокровищ появятся стили профиля, титулы, оформление и "
            "Premium-возможности для твоего героя 👑"
        ),
    }

    text = answers.get(question)
    if text is None:
        await showSupportFaq(update)
        return

    await _render(update, text, getBackToMenuKeyboard("support:faq"))


async def showRules(update: Update) -> None:
    await _render(
        update,
        (
            "📜👑 Законы королевства RoleHub\n\n"
            "1. ✨ Уважай других героев.\n"
            "2. 🔕 Не спамь магическими посланиями.\n"
            "3. 🤝 Не мешай приключениям других участников.\n"
            "4. 🌌 Соблюдай тему выбранного мира.\n"
            "5. 🛡 Жалобы рассматривает администрация."
        ),
        getBackToMenuKeyboard("support:back"),
    )
