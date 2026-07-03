"""Уведомления участникам лобби."""

from telegram import Bot, InlineKeyboardMarkup

from src.core.database import get_session
from src.core.logger import logger
from src.keyboards.lobby_keyboard import get_active_lobby_keyboard, get_closed_lobby_keyboard
from src.render.lobby_render import render_active_lobby_started
from src.repositories import lobby_member_repo, lobby_repo
from src.repositories.user_repo import get_by_id
from src.utils.display_name import format_display_name

REASON_TEXTS = {
    "owner_left": "владелец вышел",
    "empty": "все участники вышли",
    "expired": "истек срок действия",
    "manual": "лобби закрыто владельцем",
    "error": "техническая ошибка",
}


async def notify_lobby_started(bot: Bot, lobby_id: int) -> None:
    with get_session() as session:
        lobby = lobby_repo.get_by_id(session, lobby_id)
        if lobby is None:
            return
        recipients = lobby_member_repo.list_joined_users(session, lobby_id)
        text = render_active_lobby_started(lobby)
        keyboard = get_active_lobby_keyboard(lobby.code)

    for _member, user in recipients:
        await _safe_send(bot, user.telegram_id, text, keyboard)


async def notify_user_joined(bot: Bot, lobby_id: int, user_id: int) -> None:
    with get_session() as session:
        lobby = lobby_repo.get_by_id(session, lobby_id)
        joined_user = get_by_id(session, user_id)
        recipients = lobby_member_repo.list_joined_users(session, lobby_id)
        if lobby is None:
            return
        text = (
            f"✅ {format_display_name(joined_user)} вошёл в лобби.\n"
            f"Игроков: {lobby.players_count}/{lobby.max_players}"
        )

    for _member, user in recipients:
        if user.id == user_id:
            continue
        await _safe_send(bot, user.telegram_id, text)


async def notify_user_left(bot: Bot, lobby_id: int, user_id: int) -> None:
    with get_session() as session:
        lobby = lobby_repo.get_by_id(session, lobby_id)
        left_user = get_by_id(session, user_id)
        recipients = lobby_member_repo.list_joined_users(session, lobby_id)
        if lobby is None:
            return
        text = (
            f"🚪 {format_display_name(left_user)} вышел из лобби.\n"
            f"Игроков: {lobby.players_count}/{lobby.max_players}"
        )

    for _member, user in recipients:
        await _safe_send(bot, user.telegram_id, text)


async def notify_lobby_closed(bot: Bot, lobby_id: int, reason: str) -> None:
    with get_session() as session:
        recipients = lobby_member_repo.list_joined_users(session, lobby_id)

    text = f"🏁 Лобби закрыто.\n\nПричина: {REASON_TEXTS.get(reason, reason)}"
    keyboard = get_closed_lobby_keyboard()
    for _member, user in recipients:
        await _safe_send(bot, user.telegram_id, text, keyboard)


async def notify_owner_changed(bot: Bot, lobby_id: int, new_owner_id: int | None = None) -> None:
    with get_session() as session:
        recipients = lobby_member_repo.list_joined_users(session, lobby_id)
    for _member, user in recipients:
        await _safe_send(bot, user.telegram_id, "👑 Владелец лобби изменился.")


async def _safe_send(
    bot: Bot,
    chat_id: int,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    try:
        await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
    except Exception:
        logger.exception("Failed to send lobby notification to chat %s", chat_id)
