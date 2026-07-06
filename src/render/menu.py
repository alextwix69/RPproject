"""Рендер экранов reply-навигации RoleHub."""

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update

from src.keyboards.kb_build import (
    getBackToMenuKeyboard,
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


MAIN_MENU_TEXT = "Добро пожаловать в RoleHub!\n\nГлавное меню:"


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


async def showNamePrompt(update: Update) -> None:
    await _render(
        update,
        (
            "👤 Как тебя называть в RoleHub?\n\n"
            "Напиши имя следующим сообщением. Оно будет привязано к твоему Telegram ID "
            "и должно быть уникальным."
        ),
        getNamePromptKeyboard(),
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
        "🛍 Магазин RoleHub\n\nВыбери раздел:",
        getShopKeyboard(),
    )


async def showShopProfiles(update: Update) -> None:
    await _render(
        update,
        "👤 Профили\n\nЗдесь можно будет покупать и менять оформление профиля.",
        getShopProfilesKeyboard(),
    )


async def showShopThemes(update: Update) -> None:
    await _render(
        update,
        "🎨 Оформление\n\nЗдесь будут визуальные стили для профиля и комнат.",
        getShopThemesKeyboard(),
    )


async def showShopPremium(update: Update) -> None:
    await _render(
        update,
        (
            "💎 Премиум\n\n"
            "Премиум-возможности RoleHub:\n"
            "• больше возможностей профиля\n"
            "• дополнительные стили\n"
            "• расширенные настройки комнат"
        ),
        getShopPremiumKeyboard(),
    )


async def showSettings(update: Update) -> None:
    await _render(
        update,
        "⚙️ Настройки\n\nВыбери, что хочешь настроить:",
        getSettingsKeyboard(),
    )


async def showSettingsProfile(update: Update, display_name: str | None = None) -> None:
    text = "👤 Настройки профиля\n\n"
    if display_name:
        text += f"Имя: {display_name}\n\n"
    text += "Здесь можно изменить отображение профиля в RoleHub."

    await _render(
        update,
        text,
        getSettingsProfileKeyboard(),
    )


async def showSettingsNotifications(update: Update, user_settings=None) -> None:
    await _render(
        update,
        "🔔 Уведомления\n\nНастрой, какие уведомления получать:",
        getSettingsNotificationsKeyboard(user_settings),
    )


async def showSettingsLanguage(update: Update) -> None:
    await _render(
        update,
        "🌐 Язык\n\nВыбери язык интерфейса:",
        getSettingsLanguageKeyboard(),
    )


async def showSettingsSafety(update: Update) -> None:
    await _render(
        update,
        "🛡 Безопасность\n\nНастройки приватности и безопасности:",
        getSettingsSafetyKeyboard(),
    )


async def showSupport(update: Update) -> None:
    await _render(
        update,
        "🆘 Поддержка RoleHub\n\nЧем помочь?",
        getSupportKeyboard(),
    )


async def showSupportFaq(update: Update) -> None:
    await _render(
        update,
        "❓ FAQ\n\nВыбери вопрос:",
        getSupportFaqKeyboard(),
    )


async def showComingSoon(
    update: Update,
    title: str,
    description: str,
    back_target: str,
) -> None:
    text = f"🚧 Раздел в разработке\n\n{title}"
    if description:
        text = f"{text}\n\n{description}"

    await _render(update, text, getBackToMenuKeyboard(back_target))


async def showPremiumInfo(update: Update) -> None:
    await _render(
        update,
        (
            "📋 Что входит в премиум\n\n"
            "Планируемые возможности:\n"
            "• дополнительные стили профиля\n"
            "• уникальные титулы\n"
            "• больше настроек комнат\n"
            "• приоритетные возможности в будущих lobby-механиках"
        ),
        getBackToMenuKeyboard("shop:premium"),
    )


async def showFaqAnswer(update: Update, question: str) -> None:
    answers = {
        "play": (
            "🎮 Как играть?\n\n"
            "Нажми “Играть”, выбери тему, затем выбери действие: найти лобби, "
            "создать лобби или посмотреть список комнат."
        ),
        "lobby": (
            "🏠 Что такое лобби?\n\n"
            "Лобби — это комната ожидания, где пользователи собираются для общения "
            "по выбранной теме."
        ),
        "shop": (
            "🛍 Как работает магазин?\n\n"
            "В магазине будут доступны стили профиля, титулы, оформление и "
            "премиум-возможности."
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
            "📜 Правила RoleHub\n\n"
            "1. Уважай других пользователей.\n"
            "2. Не спамь.\n"
            "3. Не мешай общению в комнатах.\n"
            "4. Соблюдай тему выбранного лобби.\n"
            "5. Жалобы рассматриваются администрацией."
        ),
        getBackToMenuKeyboard("support:back"),
    )
