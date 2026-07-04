from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from src.core.database import get_session
from src.keyboards.inline_buttons import PLAY_ACTIONS, TOPICS
from src.render.menu import (
    get_action_name,
    get_topic_name,
    showComingSoon,
    showFaqAnswer,
    showMainMenu,
    showNamePrompt,
    showPlayTopics,
    showPremiumInfo,
    showRules,
    showSettings,
    showSettingsLanguage,
    showSettingsNotifications,
    showSettingsProfile,
    showSettingsSafety,
    showShop,
    showShopPremium,
    showShopProfiles,
    showShopThemes,
    showSupport,
    showSupportFaq,
    showTopicActions,
)
from src.constants.callbacks import PENDING_SET_DISPLAY_NAME
from src.handlers.play_lobby import (
    handle_create_callback,
    handle_find_callback,
    handle_lobby_callback,
    handle_play_callback as handle_lobby_play_callback,
    handle_quick_callback,
)
from src.services.user_service import ensure_from_effective_user, toggle_news_notifications
from src.services.user_state_service import clear_pending_action, set_pending_action


async def _ensure_callback_user(update: Update) -> None:
    with get_session() as session:
        try:
            ensure_from_effective_user(session, update.effective_user)
            session.commit()
        except Exception:
            session.rollback()
            raise


async def callback_router(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query
    if query is None:
        return

    data = query.data or ""
    section, action, value, extra = (data.split(":") + ["", "", "", ""])[:4]

    if section not in {
        "menu",
        "play",
        "create",
        "find",
        "quick",
        "lobby",
        "noop",
        "shop",
        "settings",
        "support",
    }:
        await query.answer("Действие недоступно")
        return

    await _ensure_callback_user(update)

    if section == "noop":
        await query.answer()
        return

    if section == "menu":
        await handleMainMenuCallback(update, action)
        return

    if section == "play":
        await handlePlayCallback(update, action, value, extra)
        return

    if section == "create":
        await handle_create_callback(update, action, value, extra)
        return

    if section == "find":
        await handle_find_callback(update, action, value, extra)
        return

    if section == "quick":
        await handle_quick_callback(update, action, value, extra)
        return

    if section == "lobby":
        await handle_lobby_callback(update, action, value, extra)
        return

    if section == "shop":
        await handleShopCallback(update, action, value)
        return

    if section == "settings":
        await handleSettingsCallback(update, action, value)
        return

    if section == "support":
        await handleSupportCallback(update, action, value)
        return


async def handleMainMenuCallback(update: Update, action: str) -> None:
    if action == "main":
        _clear_name_pending(update)
        await showMainMenu(update)
        return

    if action == "play":
        await showPlayTopics(update)
        return

    if action == "shop":
        await showShop(update)
        return

    if action == "settings":
        await showSettings(update)
        return

    if action == "support":
        await showSupport(update)
        return

    await _answer_unavailable(update)


async def handlePlayCallback(update: Update, action: str, value: str, extra: str) -> None:
    if await handle_lobby_play_callback(update, action, value, extra):
        return

    if action == "topic":
        if value not in TOPICS:
            await showPlayTopics(update)
            return
        await showTopicActions(update, value)
        return

    if action == "back" and value == "topics":
        await showPlayTopics(update)
        return

    if action == "back" and value == "actions":
        if extra not in TOPICS:
            await showPlayTopics(update)
            return
        await showTopicActions(update, extra)
        return

    if action in PLAY_ACTIONS:
        topic_name = get_topic_name(value)
        action_name = get_action_name(action)
        if topic_name is None or action_name is None:
            await showPlayTopics(update)
            return

        await showComingSoon(
            update,
            action_name,
            f"Тема: {topic_name}",
            f"play:back:actions:{value}",
        )
        return

    await _answer_unavailable(update)


async def handleShopCallback(update: Update, action: str, value: str) -> None:
    if action == "back":
        await showShop(update)
        return

    if action == "profiles" and not value:
        await showShopProfiles(update)
        return

    if action == "profiles" and value in {"avatars", "titles"}:
        title = "Аватарки" if value == "avatars" else "Титулы"
        await showComingSoon(
            update,
            title,
            "Скоро здесь появятся предметы для профиля.",
            "shop:profiles",
        )
        return

    if action == "themes" and not value:
        await showShopThemes(update)
        return

    if action == "themes" and value in {"dark", "effects"}:
        title = "Тёмные стили" if value == "dark" else "Эффекты"
        await showComingSoon(
            update,
            title,
            "Скоро здесь появятся визуальные стили.",
            "shop:themes",
        )
        return

    if action == "premium" and not value:
        await showShopPremium(update)
        return

    if action == "premium" and value == "buy":
        await showComingSoon(
            update,
            "Покупка премиума пока в разработке.",
            "",
            "shop:premium",
        )
        return

    if action == "premium" and value == "info":
        await showPremiumInfo(update)
        return

    if action == "promo":
        await showComingSoon(
            update,
            "Промокод",
            "Ввод промокодов пока в разработке.",
            "shop:back",
        )
        return

    await _answer_unavailable(update)


async def handleSettingsCallback(update: Update, action: str, value: str) -> None:
    if action == "back":
        await showSettings(update)
        return

    if action == "profile" and not value:
        await showSettingsProfile(update, _get_current_display_name(update))
        return

    if action == "profile" and value == "name":
        _set_name_pending(update)
        await showNamePrompt(update)
        return

    if action == "profile" and value == "bio":
        titles = {
            "bio": "Описание",
        }
        await showComingSoon(update, titles[value], "", "settings:profile")
        return

    if action == "notifications":
        await showSettingsNotifications(update, _get_current_user_settings(update))
        return

    if action == "notif" and value == "news":
        await _toggle_news_notifications(update)
        return

    if action == "notif" and value in {"lobby", "invites"}:
        await showComingSoon(
            update,
            "Настройки уведомлений будут доступны позже.",
            "",
            "settings:notifications",
        )
        return

    if action == "language":
        await showSettingsLanguage(update)
        return

    if action == "lang" and value == "ru":
        await showComingSoon(
            update,
            "Выбор языка будет доступен позже.",
            "",
            "settings:language",
        )
        return

    if action == "name_later":
        _clear_name_pending(update)
        await showMainMenu(update)
        return

    if action == "safety" and not value:
        await showSettingsSafety(update)
        return

    if action == "safety" and value in {"blacklist", "privacy", "reports"}:
        titles = {
            "blacklist": "Чёрный список",
            "privacy": "Приватность профиля",
            "reports": "Жалобы",
        }
        await showComingSoon(update, titles[value], "", "settings:safety")
        return

    await _answer_unavailable(update)


async def handleSupportCallback(update: Update, action: str, value: str) -> None:
    if action == "back":
        await showSupport(update)
        return

    if action == "faq" and not value:
        await showSupportFaq(update)
        return

    if action == "faq" and value in {"play", "lobby", "shop"}:
        await showFaqAnswer(update, value)
        return

    if action == "bug":
        await showComingSoon(
            update,
            "Сообщить об ошибке",
            "Функция отправки баг-репортов пока в разработке.",
            "support:back",
        )
        return

    if action == "admin":
        await showComingSoon(
            update,
            "Связаться с админом",
            "Связь с администратором пока в разработке.",
            "support:back",
        )
        return

    if action == "rules":
        await showRules(update)
        return

    await _answer_unavailable(update)


async def _answer_unavailable(update: Update) -> None:
    if update.callback_query is not None:
        await update.callback_query.answer("Действие недоступно")


def _set_name_pending(update: Update) -> None:
    with get_session() as session:
        try:
            user = ensure_from_effective_user(session, update.effective_user)
            if user is not None:
                set_pending_action(user, PENDING_SET_DISPLAY_NAME)
            session.commit()
        except Exception:
            session.rollback()
            raise


def _get_current_display_name(update: Update) -> str | None:
    with get_session() as session:
        user = ensure_from_effective_user(session, update.effective_user)
        session.commit()
        return user.display_name if user is not None else None


def _get_current_user_settings(update: Update):
    with get_session() as session:
        user = ensure_from_effective_user(session, update.effective_user)
        session.commit()
        return user


async def _toggle_news_notifications(update: Update) -> None:
    with get_session() as session:
        try:
            user = ensure_from_effective_user(session, update.effective_user)
            if user is not None:
                toggle_news_notifications(user)
            session.commit()
        except Exception:
            session.rollback()
            raise

    await showSettingsNotifications(update, user)


def _clear_name_pending(update: Update) -> None:
    with get_session() as session:
        try:
            user = ensure_from_effective_user(session, update.effective_user)
            if user is not None and user.pending_action == PENDING_SET_DISPLAY_NAME:
                clear_pending_action(user)
            session.commit()
        except Exception:
            session.rollback()
            raise


def register_main_menu_handler(application) -> None:
    application.add_handler(
        CallbackQueryHandler(
            callback_router,
            pattern=r"^(menu|play|create|find|quick|lobby|noop|shop|settings|support):",
        )
    )
    application.add_handler(CallbackQueryHandler(callback_router))
