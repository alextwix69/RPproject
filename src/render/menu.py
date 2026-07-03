"""Рендер экранов inline-навигации RoleHub."""

from telegram import Update
from telegram.error import BadRequest

from src.keyboards.inline_buttons import PLAY_ACTIONS, TOPICS
from src.keyboards.kb_build import (
    getBackToMenuKeyboard,
    getMainMenuKeyboard,
    getPlayTopicsKeyboard,
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
    getTopicActionsKeyboard,
)


MAIN_MENU_TEXT = "Добро пожаловать в RoleHub!\n\nГлавное меню:"


async def _render(update: Update, text: str, reply_markup=None) -> None:
    query = update.callback_query

    if query is not None:
        await query.answer()
        try:
            await query.edit_message_text(text, reply_markup=reply_markup)
        except BadRequest as exc:
            message = str(exc).lower()
            if "message is not modified" in message:
                return
        return

    if update.message is not None:
        await update.message.reply_text(text, reply_markup=reply_markup)


def get_topic_name(topic: str) -> str | None:
    return TOPICS.get(topic)


def get_action_name(action: str) -> str | None:
    return PLAY_ACTIONS.get(action)


async def showMainMenu(update: Update) -> None:
    await _render(update, MAIN_MENU_TEXT, getMainMenuKeyboard())


async def showPlayTopics(update: Update) -> None:
    await _render(
        update,
        "🎮 Играть\n\nВыбери тему для игры:",
        getPlayTopicsKeyboard(),
    )


async def showTopicActions(update: Update, topic: str) -> None:
    topic_name = get_topic_name(topic)
    if topic_name is None:
        await showPlayTopics(update)
        return

    await _render(
        update,
        f"🎮 Тема: {topic_name}\n\nЧто хочешь сделать?",
        getTopicActionsKeyboard(topic),
    )


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


async def showSettingsProfile(update: Update) -> None:
    await _render(
        update,
        "👤 Настройки профиля\n\nЗдесь можно будет изменить отображение профиля в RoleHub.",
        getSettingsProfileKeyboard(),
    )


async def showSettingsNotifications(update: Update) -> None:
    await _render(
        update,
        "🔔 Уведомления\n\nНастрой, какие уведомления получать:",
        getSettingsNotificationsKeyboard(),
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
    backCallback: str,
) -> None:
    text = f"🚧 Раздел в разработке\n\n{title}"
    if description:
        text = f"{text}\n\n{description}"

    await _render(update, text, getBackToMenuKeyboard(backCallback))


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
