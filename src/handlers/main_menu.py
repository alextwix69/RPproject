import re

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

from src.constants.pending_actions import (
    PENDING_FIND_FRIEND,
    PENDING_SET_DISPLAY_NAME,
    PENDING_SET_PROFILE_PHOTO,
)
from src.core.database import get_session
from src.handlers.play_lobby import show_current_lobby, show_play_menu
from src.keyboards.kb_build import (
    BTN_BACK,
    BTN_ADD_FOUND_FRIEND,
    BTN_FIND_FRIEND,
    BTN_FRIENDS,
    BTN_LANGUAGE_RU,
    BTN_MAIN_MENU,
    BTN_NAME_LATER,
    BTN_NOTIF_INVITES,
    BTN_NOTIF_LOBBY,
    BTN_PLAY,
    BTN_PROFILE_AVATAR,
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
    BTN_SEARCH_FRIEND_AGAIN,
    BTN_VIEW_FOUND_PROFILE,
    LEGACY_BUTTON_ALIASES,
    normalize_button_text,
)
from src.render.menu import (
    showAvatarPrompt,
    showComingSoon,
    showFriendSearchPrompt,
    showFriends,
    showMainMenu,
    showNamePrompt,
    showPremiumInfo,
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
    showSupportAdmin,
    showProfile,
)
from src.repositories.user_repo import get_by_id
from src.services.profile_service import FriendActionError, add_friend, render_profile_text
from src.services.user_service import ensure_from_effective_user, toggle_news_notifications
from src.services.user_state_service import (
    clear_create_state,
    clear_pending_action,
    get_create_state,
    is_general_menu_scene,
    set_create_state,
    set_pending_action,
)

BTN_NEWS_ON = "✅ Вести королевства: Вкл"
BTN_NEWS_OFF = "❌ Вести королевства: Выкл"

MENU_BUTTONS = {
    BTN_PLAY,
    BTN_FRIENDS,
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
    BTN_PROFILE_AVATAR,
    BTN_PROFILE_BIO,
    BTN_FIND_FRIEND,
    BTN_VIEW_FOUND_PROFILE,
    BTN_ADD_FOUND_FRIEND,
    BTN_SEARCH_FRIEND_AGAIN,
    BTN_NOTIF_LOBBY,
    BTN_NOTIF_INVITES,
    BTN_NEWS_ON,
    BTN_NEWS_OFF,
    BTN_LANGUAGE_RU,
    BTN_NAME_LATER,
    BTN_SAFETY_BLACKLIST,
    BTN_SAFETY_PRIVACY,
    BTN_SAFETY_REPORTS,
    BTN_SUPPORT_ADMIN,
    *LEGACY_BUTTON_ALIASES,
    "✅ Новости: Вкл",
    "❌ Новости: Выкл",
}


async def main_menu_reply_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.text is None:
        return

    text = normalize_button_text(update.message.text.strip())
    text = {
        "✅ Новости: Вкл": BTN_NEWS_ON,
        "❌ Новости: Выкл": BTN_NEWS_OFF,
    }.get(text, text)
    _ensure_reply_user(update)

    if text == BTN_MAIN_MENU:
        _clear_name_pending(update)
        await showMainMenu(update)
        return

    if text == BTN_BACK:
        await _handle_back(update)
        return

    if text == BTN_PLAY:
        await show_play_menu(update)
        return

    if text == BTN_FRIENDS:
        _set_menu_scene(update, "friends")
        await showFriends(update)
        return

    if text == BTN_RETURN_TO_ACTIVE_LOBBY:
        await show_current_lobby(update)
        return

    if text == BTN_SHOP:
        _set_menu_scene(update, "shop")
        await showShop(update)
        return

    if text == BTN_SETTINGS:
        _set_menu_scene(update, "settings")
        await showSettings(update)
        return

    if text == BTN_SUPPORT:
        _set_menu_scene(update, "support")
        await showSupport(update)
        return

    await _handle_shop_text(update, text)
    await _handle_settings_text(update, text)
    await _handle_friends_text(update, text)
    await _handle_support_text(update, text)


async def _handle_shop_text(update: Update, text: str) -> None:
    if text == BTN_SHOP_PROFILES:
        _set_menu_scene(update, "shop")
        await showShopProfiles(update)
    elif text == BTN_SHOP_THEMES:
        _set_menu_scene(update, "shop")
        await showShopThemes(update)
    elif text == BTN_SHOP_PREMIUM:
        _set_menu_scene(update, "shop")
        await showShopPremium(update)
    elif text == BTN_SHOP_PROMO:
        await showComingSoon(update, "🎁 Волшебный промокод", "Скоро здесь можно будет открывать тайные подарки.", "shop")
    elif text == BTN_SHOP_AVATARS:
        await showComingSoon(update, "🖼 Волшебные аватарки", "Скоро здесь появятся редкие портреты героев.", "shop")
    elif text == BTN_SHOP_TITLES:
        await showComingSoon(update, "👑 Титулы героев", "Скоро здесь можно будет выбрать величественный титул.", "shop")
    elif text == BTN_SHOP_DARK:
        await showComingSoon(update, "🌙 Ночные стили", "Скоро здесь появится магия ночного оформления.", "shop")
    elif text == BTN_SHOP_EFFECTS:
        await showComingSoon(update, "✨ Магические эффекты", "Скоро профиль засияет новыми чарами.", "shop")
    elif text == BTN_SHOP_BUY_PREMIUM:
        await showComingSoon(update, "💎 Получить RoleHub Premium", "Сокровищница ещё готовится к открытию.", "shop")
    elif text == BTN_SHOP_PREMIUM_INFO:
        _set_menu_scene(update, "shop_premium")
        await showPremiumInfo(update)


async def _handle_settings_text(update: Update, text: str) -> None:
    if text == BTN_SETTINGS_PROFILE:
        _set_menu_scene(update, "settings_profile")
        profile_text, avatar_file_id = _get_current_profile_payload(update)
        await showSettingsProfile(update, profile_text, avatar_file_id)
    elif text == BTN_SETTINGS_NOTIFICATIONS:
        _set_menu_scene(update, "settings")
        await showSettingsNotifications(update, _get_current_user_settings(update))
    elif text == BTN_SETTINGS_LANGUAGE:
        _set_menu_scene(update, "settings")
        await showSettingsLanguage(update)
    elif text == BTN_SETTINGS_SAFETY:
        _set_menu_scene(update, "settings")
        await showSettingsSafety(update)
    elif text == BTN_PROFILE_NAME:
        _set_name_pending(update)
        await showNamePrompt(update)
    elif text == BTN_PROFILE_AVATAR:
        _set_profile_photo_pending(update)
        await showAvatarPrompt(update)
    elif text == BTN_PROFILE_BIO:
        await showComingSoon(update, "📖 История героя", "Скоро ты сможешь рассказать свою легенду.", "settings")
    elif text in {BTN_NOTIF_LOBBY, BTN_NOTIF_INVITES}:
        await showComingSoon(update, "🔔 Волшебные весточки", "Тонкая настройка посланий появится позже.", "settings")
    elif text in {BTN_NEWS_ON, BTN_NEWS_OFF}:
        await _toggle_news_notifications(update)
    elif text == BTN_LANGUAGE_RU:
        await showComingSoon(update, "🌐 Язык мира", "Новые языки королевства появятся позже.", "settings")
    elif text == BTN_NAME_LATER:
        _clear_name_pending(update)
        await showMainMenu(update)
    elif text in {BTN_SAFETY_BLACKLIST, BTN_SAFETY_PRIVACY, BTN_SAFETY_REPORTS}:
        titles = {
            BTN_SAFETY_BLACKLIST: "🚫 Чёрный свиток",
            BTN_SAFETY_PRIVACY: "👁 Тайны профиля",
            BTN_SAFETY_REPORTS: "⚠️ Жалобы королевской страже",
        }
        await showComingSoon(update, titles[text], "", "settings")


async def _handle_friends_text(update: Update, text: str) -> None:
    if text == BTN_FIND_FRIEND or text == BTN_SEARCH_FRIEND_AGAIN:
        _set_find_friend_pending(update)
        await showFriendSearchPrompt(update)
    elif text == BTN_VIEW_FOUND_PROFILE:
        await _show_found_user_profile(update)
    elif text == BTN_ADD_FOUND_FRIEND:
        await _add_found_friend(update)


async def _handle_support_text(update: Update, text: str) -> None:
    if text == BTN_SUPPORT_ADMIN:
        _set_menu_scene(update, "support")
        await showSupportAdmin(update)


async def _handle_back(update: Update) -> None:
    scene = _get_menu_scene(update)
    if is_general_menu_scene(scene):
        await _clear_menu_state(update)
        return

    await showMainMenu(update)


def _set_menu_scene(update: Update, scene: str) -> None:
    with get_session() as session:
        try:
            user = ensure_from_effective_user(session, update.effective_user)
            if user is not None:
                set_create_state(session, user, {"menu_scene": scene})
            session.commit()
        except Exception:
            session.rollback()
            raise


def _get_menu_scene(update: Update) -> str | None:
    with get_session() as session:
        user = ensure_from_effective_user(session, update.effective_user)
        scene = get_create_state(user).get("menu_scene") if user is not None else None
        session.commit()
        return scene


async def _clear_menu_state(update: Update) -> None:
    with get_session() as session:
        try:
            user = ensure_from_effective_user(session, update.effective_user)
            if user is not None:
                clear_pending_action(user)
                clear_create_state(user)
            session.commit()
        except Exception:
            session.rollback()
            raise

    await showMainMenu(update)


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


def _set_profile_photo_pending(update: Update) -> None:
    with get_session() as session:
        try:
            user = ensure_from_effective_user(session, update.effective_user)
            if user is not None:
                set_pending_action(user, PENDING_SET_PROFILE_PHOTO)
            session.commit()
        except Exception:
            session.rollback()
            raise


def _set_find_friend_pending(update: Update) -> None:
    with get_session() as session:
        try:
            user = ensure_from_effective_user(session, update.effective_user)
            if user is not None:
                set_pending_action(user, PENDING_FIND_FRIEND)
                set_create_state(session, user, {"menu_scene": "friends"})
            session.commit()
        except Exception:
            session.rollback()
            raise


def _get_current_profile_payload(update: Update) -> tuple[str, str | None]:
    with get_session() as session:
        user = ensure_from_effective_user(session, update.effective_user)
        text = render_profile_text(user, is_self=True) if user is not None else "👤 Твой профиль"
        avatar_file_id = user.avatar_file_id if user is not None else None
        session.commit()
        return text, avatar_file_id


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


async def _show_found_user_profile(update: Update) -> None:
    with get_session() as session:
        user = ensure_from_effective_user(session, update.effective_user)
        state = get_create_state(user) if user is not None else {}
        found_user = get_by_id(session, int(state.get("found_friend_id", 0) or 0))
        if user is not None:
            set_create_state(session, user, {"menu_scene": "friend_profile"})
        profile_text = render_profile_text(found_user) if found_user is not None else None
        avatar_file_id = found_user.avatar_file_id if found_user is not None else None
        session.commit()

    if profile_text is None:
        await showFriends(update)
        return

    await showProfile(update, profile_text, avatar_file_id)


async def _add_found_friend(update: Update) -> None:
    with get_session() as session:
        try:
            user = ensure_from_effective_user(session, update.effective_user)
            state = get_create_state(user) if user is not None else {}
            found_user = get_by_id(session, int(state.get("found_friend_id", 0) or 0))
            if user is None or found_user is None:
                session.commit()
                await showFriends(update)
                return
            add_friend(session, user, found_user)
            set_create_state(session, user, {"menu_scene": "friend_found"})
            session.commit()
        except FriendActionError as exc:
            session.commit()
            await showProfile(update, exc.message)
            return
        except Exception:
            session.rollback()
            raise

    await showProfile(update, "🤝✨ Заявка в друзья отправлена! Возможно, скоро у тебя появится новый союзник 🌟")


def _clear_name_pending(update: Update) -> None:
    with get_session() as session:
        try:
            user = ensure_from_effective_user(session, update.effective_user)
            if user is not None and user.pending_action in {
                PENDING_SET_DISPLAY_NAME,
                PENDING_SET_PROFILE_PHOTO,
                PENDING_FIND_FRIEND,
            }:
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
