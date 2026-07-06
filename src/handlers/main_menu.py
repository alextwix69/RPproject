import re

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

from src.constants.pending_actions import PENDING_SET_DISPLAY_NAME
from src.core.database import get_session
from src.handlers.play_lobby import show_current_lobby, show_play_menu
from src.keyboards.kb_build import (
    BTN_BACK,
    BTN_FAQ_LOBBY,
    BTN_FAQ_PLAY,
    BTN_FAQ_SHOP,
    BTN_LANGUAGE_RU,
    BTN_MAIN_MENU,
    BTN_NAME_LATER,
    BTN_NOTIF_INVITES,
    BTN_NOTIF_LOBBY,
    BTN_PLAY,
    BTN_PROFILE_BIO,
    BTN_PROFILE_NAME,
    BTN_RETURN_TO_ACTIVE_LOBBY,
    BTN_SAFETY_BLACKLIST,
    BTN_SAFETY_PRIVACY,
    BTN_SAFETY_REPORTS,
    BTN_SETTINGS,
    BTN_SETTINGS_LANGUAGE,
    BTN_SETTINGS_NOTIFICATIONS,
    BTN_SETTINGS_PROFILE,
    BTN_SETTINGS_SAFETY,
    BTN_SHOP,
    BTN_SHOP_AVATARS,
    BTN_SHOP_BUY_PREMIUM,
    BTN_SHOP_DARK,
    BTN_SHOP_EFFECTS,
    BTN_SHOP_PREMIUM,
    BTN_SHOP_PREMIUM_INFO,
    BTN_SHOP_PROFILES,
    BTN_SHOP_PROMO,
    BTN_SHOP_THEMES,
    BTN_SHOP_TITLES,
    BTN_SUPPORT,
    BTN_SUPPORT_ADMIN,
    BTN_SUPPORT_BUG,
    BTN_SUPPORT_FAQ,
    BTN_SUPPORT_RULES,
)
from src.render.menu import (
    showComingSoon,
    showFaqAnswer,
    showMainMenu,
    showNamePrompt,
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
)
from src.services.user_service import ensure_from_effective_user, toggle_news_notifications
from src.services.user_state_service import clear_pending_action, set_pending_action

BTN_NEWS_ON = "✅ Новости: Вкл"
BTN_NEWS_OFF = "❌ Новости: Выкл"

MENU_BUTTONS = {
    BTN_PLAY,
    BTN_RETURN_TO_ACTIVE_LOBBY,
    BTN_SHOP,
    BTN_SETTINGS,
    BTN_SUPPORT,
    BTN_SHOP_PROFILES,
    BTN_SHOP_THEMES,
    BTN_SHOP_PREMIUM,
    BTN_SHOP_PROMO,
    BTN_SHOP_AVATARS,
    BTN_SHOP_TITLES,
    BTN_SHOP_DARK,
    BTN_SHOP_EFFECTS,
    BTN_SHOP_BUY_PREMIUM,
    BTN_SHOP_PREMIUM_INFO,
    BTN_SETTINGS_PROFILE,
    BTN_SETTINGS_NOTIFICATIONS,
    BTN_SETTINGS_LANGUAGE,
    BTN_SETTINGS_SAFETY,
    BTN_PROFILE_NAME,
    BTN_PROFILE_BIO,
    BTN_NOTIF_LOBBY,
    BTN_NOTIF_INVITES,
    BTN_NEWS_ON,
    BTN_NEWS_OFF,
    BTN_LANGUAGE_RU,
    BTN_NAME_LATER,
    BTN_SAFETY_BLACKLIST,
    BTN_SAFETY_PRIVACY,
    BTN_SAFETY_REPORTS,
    BTN_SUPPORT_FAQ,
    BTN_SUPPORT_BUG,
    BTN_SUPPORT_ADMIN,
    BTN_SUPPORT_RULES,
    BTN_FAQ_PLAY,
    BTN_FAQ_LOBBY,
    BTN_FAQ_SHOP,
}


async def main_menu_reply_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.text is None:
        return

    text = update.message.text.strip()
    _ensure_reply_user(update)

    if text == BTN_MAIN_MENU:
        _clear_name_pending(update)
        await showMainMenu(update)
        return

    if text == BTN_BACK:
        await showMainMenu(update)
        return

    if text == BTN_PLAY:
        await show_play_menu(update)
        return

    if text == BTN_RETURN_TO_ACTIVE_LOBBY:
        await show_current_lobby(update)
        return

    if text == BTN_SHOP:
        await showShop(update)
        return

    if text == BTN_SETTINGS:
        await showSettings(update)
        return

    if text == BTN_SUPPORT:
        await showSupport(update)
        return

    await _handle_shop_text(update, text)
    await _handle_settings_text(update, text)
    await _handle_support_text(update, text)


async def _handle_shop_text(update: Update, text: str) -> None:
    if text == BTN_SHOP_PROFILES:
        await showShopProfiles(update)
    elif text == BTN_SHOP_THEMES:
        await showShopThemes(update)
    elif text == BTN_SHOP_PREMIUM:
        await showShopPremium(update)
    elif text == BTN_SHOP_PROMO:
        await showComingSoon(update, "Промокод", "Ввод промокодов пока в разработке.", "shop")
    elif text == BTN_SHOP_AVATARS:
        await showComingSoon(update, "Аватарки", "Скоро здесь появятся предметы для профиля.", "shop")
    elif text == BTN_SHOP_TITLES:
        await showComingSoon(update, "Титулы", "Скоро здесь появятся предметы для профиля.", "shop")
    elif text == BTN_SHOP_DARK:
        await showComingSoon(update, "Тёмные стили", "Скоро здесь появятся визуальные стили.", "shop")
    elif text == BTN_SHOP_EFFECTS:
        await showComingSoon(update, "Эффекты", "Скоро здесь появятся визуальные стили.", "shop")
    elif text == BTN_SHOP_BUY_PREMIUM:
        await showComingSoon(update, "Покупка премиума пока в разработке.", "", "shop")
    elif text == BTN_SHOP_PREMIUM_INFO:
        await showPremiumInfo(update)


async def _handle_settings_text(update: Update, text: str) -> None:
    if text == BTN_SETTINGS_PROFILE:
        await showSettingsProfile(update, _get_current_display_name(update))
    elif text == BTN_SETTINGS_NOTIFICATIONS:
        await showSettingsNotifications(update, _get_current_user_settings(update))
    elif text == BTN_SETTINGS_LANGUAGE:
        await showSettingsLanguage(update)
    elif text == BTN_SETTINGS_SAFETY:
        await showSettingsSafety(update)
    elif text == BTN_PROFILE_NAME:
        _set_name_pending(update)
        await showNamePrompt(update)
    elif text == BTN_PROFILE_BIO:
        await showComingSoon(update, "Описание", "", "settings")
    elif text in {BTN_NOTIF_LOBBY, BTN_NOTIF_INVITES}:
        await showComingSoon(update, "Настройки уведомлений будут доступны позже.", "", "settings")
    elif text in {BTN_NEWS_ON, BTN_NEWS_OFF}:
        await _toggle_news_notifications(update)
    elif text == BTN_LANGUAGE_RU:
        await showComingSoon(update, "Выбор языка будет доступен позже.", "", "settings")
    elif text == BTN_NAME_LATER:
        _clear_name_pending(update)
        await showMainMenu(update)
    elif text in {BTN_SAFETY_BLACKLIST, BTN_SAFETY_PRIVACY, BTN_SAFETY_REPORTS}:
        titles = {
            BTN_SAFETY_BLACKLIST: "Чёрный список",
            BTN_SAFETY_PRIVACY: "Приватность профиля",
            BTN_SAFETY_REPORTS: "Жалобы",
        }
        await showComingSoon(update, titles[text], "", "settings")


async def _handle_support_text(update: Update, text: str) -> None:
    if text == BTN_SUPPORT_FAQ:
        await showSupportFaq(update)
    elif text == BTN_SUPPORT_BUG:
        await showComingSoon(update, "Сообщить об ошибке", "Функция отправки баг-репортов пока в разработке.", "support")
    elif text == BTN_SUPPORT_ADMIN:
        await showComingSoon(update, "Связаться с админом", "Связь с администратором пока в разработке.", "support")
    elif text == BTN_SUPPORT_RULES:
        await showRules(update)
    elif text == BTN_FAQ_PLAY:
        await showFaqAnswer(update, "play")
    elif text == BTN_FAQ_LOBBY:
        await showFaqAnswer(update, "lobby")
    elif text == BTN_FAQ_SHOP:
        await showFaqAnswer(update, "shop")


def _ensure_reply_user(update: Update) -> None:
    with get_session() as session:
        try:
            ensure_from_effective_user(session, update.effective_user)
            session.commit()
        except Exception:
            session.rollback()
            raise


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


def _menu_filter():
    pattern = "^(?:" + "|".join(re.escape(button) for button in sorted(MENU_BUTTONS, key=len, reverse=True)) + ")$"
    return filters.TEXT & ~filters.COMMAND & filters.Regex(pattern)


def register_main_menu_handler(application) -> None:
    application.add_handler(MessageHandler(_menu_filter(), main_menu_reply_router))
