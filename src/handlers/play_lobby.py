"""Handlers для lobby-механики RoleHub."""

import asyncio
import random
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

from src.constants.callbacks import (
    PENDING_CREATE_ROLE_SEARCH,
    PENDING_ENTER_LOBBY_CODE,
    PENDING_JOIN_ROLE_SEARCH_PREFIX,
)
from src.constants.roles import ROLES_BY_TOPIC, search_roles
from src.constants.topics import TOPICS
from src.core.database import get_session
from src.core.logger import logger
from src.keyboards.lobby_keyboard import (
    get_active_lobby_keyboard,
    get_already_in_lobby_keyboard,
    get_code_entry_keyboard,
    get_create_confirm_keyboard,
    get_create_mode_keyboard,
    get_create_privacy_keyboard,
    get_create_role_keyboard,
    get_create_size_keyboard,
    get_found_lobby_keyboard,
    get_invalid_code_keyboard,
    get_join_role_keyboard,
    get_leave_done_keyboard,
    get_lobby_full_keyboard,
    get_lobby_members_keyboard,
    get_lobby_waiting_keyboard,
    get_no_lobby_keyboard,
    get_play_main_keyboard,
    get_role_search_prompt_keyboard,
    get_role_search_results_keyboard,
    get_topic_keyboard,
)
from src.render.lobby_render import (
    render_active_lobby_started,
    render_create_confirm,
    render_create_mode,
    render_create_privacy,
    render_create_role,
    render_create_size,
    render_create_topic,
    render_found_lobby,
    render_lobby_info,
    render_lobby_waiting,
    render_no_lobby,
    render_join_role,
    render_play_main,
    render_quick_no_lobby,
    role_name,
)
from src.render.menu import _render
from src.repositories import lobby_member_repo, lobby_repo
from src.services import lobby_message_service
from src.services.lobby_service import (
    LobbyError,
    close_lobby,
    create_lobby,
    join_lobby,
    leave_lobby,
    start_lobby,
)
from src.services.matchmaking_service import find_available_lobby, find_next_lobby
from src.services.notification_service import (
    notify_lobby_closed,
    notify_lobby_started,
    notify_owner_changed,
    notify_user_joined,
    notify_user_left,
)
from src.services.user_service import ensure_from_effective_user
from src.services.user_state_service import (
    clear_create_state,
    clear_pending_action,
    get_create_state,
    set_create_state,
    set_pending_action,
)
from src.utils.display_name import format_display_name


async def handle_play_callback(update: Update, action: str, value: str, extra: str) -> bool:
    if action in {"main", ""}:
        await _render(update, render_play_main(), get_play_main_keyboard())
        return True
    if action == "create":
        await _show_create_topic(update)
        return True
    if action == "find":
        await _render(update, "🔎 Поиск лобби\n\nВыбери тему:", get_topic_keyboard("find"))
        return True
    if action == "quick":
        await _render(
            update,
            "⚡ Быстрый вход\n\nВыбери тему, и бот попробует сразу подключить тебя к свободному лобби.",
            get_topic_keyboard("quick"),
        )
        return True
    if action == "code":
        await _set_pending_code_action(update)
        return True
    return False


async def handle_create_callback(update: Update, action: str, value: str, extra: str) -> None:
    if action == "topic" and value in TOPICS:
        with get_session() as session:
            user = _ensure_user(session, update)
            set_create_state(session, user, {"topic": value})
            session.commit()
        await _render(update, render_create_mode(value), get_create_mode_keyboard())
        return

    if action == "mode" and value in {"chat", "rp"}:
        with get_session() as session:
            user = _ensure_user(session, update)
            state = set_create_state(session, user, {"mode": value, "role": None})
            session.commit()
        if value == "rp":
            await _render(update, render_create_role(state["topic"]), get_create_role_keyboard(state["topic"]))
            return
        await _render(update, render_create_size(), get_create_size_keyboard("create:back:mode"))
        return

    if action == "role":
        with get_session() as session:
            user = _ensure_user(session, update)
            state = get_create_state(user)
            topic = state.get("topic")
            role = _resolve_role(topic, value)
            state = set_create_state(session, user, {"role": role})
            clear_pending_action(user)
            session.commit()
        max_size = len(ROLES_BY_TOPIC.get(topic or "", {})) if topic else 5
        await _render(update, render_create_size(), get_create_size_keyboard(max_size=max_size))
        return

    if action == "roles":
        with get_session() as session:
            user = _ensure_user(session, update)
            state = get_create_state(user)
            topic = state.get("topic")
        await _render(
            update,
            render_create_role(topic),
            get_create_role_keyboard(topic, _safe_page(value)),
        )
        return

    if action == "role_search":
        with get_session() as session:
            user = _ensure_user(session, update)
            state = get_create_state(user)
            topic = state.get("topic")
            if topic not in ROLES_BY_TOPIC:
                session.commit()
                await _show_create_topic(update)
                return
            set_pending_action(user, PENDING_CREATE_ROLE_SEARCH)
            session.commit()
        await _render(
            update,
            "🔎 Поиск роли\n\nНапиши имя роли или часть имени. Например: Твайлайт, Спаркл, 8-Бит.",
            get_role_search_prompt_keyboard("create:roles:0"),
        )
        return

    if action == "size" and value in {"2", "3", "4", "5"}:
        with get_session() as session:
            user = _ensure_user(session, update)
            state = get_create_state(user)
            max_size = len(ROLES_BY_TOPIC.get(state.get("topic") or "", {}))
            if state.get("mode") == "rp" and int(value) > max_size:
                session.commit()
                await _render(
                    update,
                    "Для этой темы недостаточно уникальных ролей на такой размер лобби.",
                    get_create_size_keyboard(max_size=max_size),
                )
                return
            set_create_state(session, user, {"max_players": int(value)})
            session.commit()
        await _render(update, render_create_privacy(), get_create_privacy_keyboard())
        return

    if action == "privacy" and value in {"public", "private"}:
        with get_session() as session:
            user = _ensure_user(session, update)
            state = set_create_state(session, user, {"privacy": value})
            session.commit()
        await _render(update, render_create_confirm(state), get_create_confirm_keyboard())
        return

    if action == "confirm":
        await _confirm_create_lobby(update, update.get_bot())
        return

    if action == "edit":
        await _show_create_topic(update)
        return

    if action == "from_find" and value in TOPICS:
        with get_session() as session:
            user = _ensure_user(session, update)
            set_create_state(session, user, {"topic": value})
            session.commit()
        await _render(update, render_create_mode(value), get_create_mode_keyboard())
        return

    if action == "back":
        await _handle_create_back(update, value)
        return

    await _answer_unavailable(update)


async def handle_find_callback(update: Update, action: str, value: str, extra: str) -> None:
    if action == "topic_menu":
        await _render(update, "🔎 Поиск лобби\n\nВыбери тему:", get_topic_keyboard("find"))
        return

    if action == "topic" and value in TOPICS:
        await _show_found_lobby(update, value)
        return

    if action == "next" and value in TOPICS:
        with get_session() as session:
            user = _ensure_user(session, update)
            lobby = find_next_lobby(session, value, extra, user_id=user.id)
        if lobby is None:
            await _render(update, render_no_lobby(value), get_no_lobby_keyboard(value, f"find:topic:{value}"))
            return
        await _render(update, render_found_lobby(lobby), get_found_lobby_keyboard(lobby.code, value))
        return

    await _answer_unavailable(update)


async def handle_quick_callback(update: Update, action: str, value: str, extra: str) -> None:
    if action != "topic" or value not in TOPICS:
        await _answer_unavailable(update)
        return

    with get_session() as session:
        try:
            user = _ensure_user(session, update)
            if user.current_lobby_id is not None:
                raise LobbyError("already_in_lobby", "Ты уже находишься в лобби.")
            lobby = find_available_lobby(session, value, user_id=user.id)
            if lobby is not None and lobby.mode == "rp":
                taken_roles = lobby_member_repo.list_taken_roles(session, lobby.id)
                session.commit()
                await _render(
                    update,
                    render_join_role(lobby),
                    get_join_role_keyboard(lobby.code, lobby.topic, taken_roles),
                )
                return
            if lobby is not None:
                lobby = join_lobby(session, user, lobby.code)
            auto_start = False
            if lobby is not None and lobby.players_count == lobby.max_players:
                start_lobby(session, user, lobby.code, force=True)
                auto_start = True
            session.commit()
        except LobbyError as exc:
            session.rollback()
            await _show_lobby_error(update, exc)
            return
        except Exception:
            session.rollback()
            logger.exception("Quick join failed")
            await _render(update, "Не удалось быстро войти в лобби.", get_play_main_keyboard())
            return

    if lobby is None:
        await _render(
            update,
            render_quick_no_lobby(value),
            get_no_lobby_keyboard(value, f"quick:topic:{value}", "play:main"),
        )
        return

    await notify_user_joined(update.get_bot(), lobby.id, user.id)
    if auto_start:
        await notify_lobby_started(update.get_bot(), lobby.id)
        await _render(update, render_active_lobby_started(lobby), get_active_lobby_keyboard(lobby.code))
        return
    await _show_lobby_waiting(update, lobby.code)


async def handle_lobby_callback(update: Update, action: str, value: str, extra: str) -> None:
    if action == "join":
        await _join_lobby_from_callback(update, value)
        return
    if action == "role":
        await _join_lobby_from_callback(update, value, extra)
        return
    if action == "roles":
        await _show_join_role_page(update, value, _safe_page(extra))
        return
    if action == "role_search":
        await _start_join_role_search(update, value)
        return
    if action == "refresh":
        await _show_lobby_waiting(update, value)
        return
    if action == "invite":
        await _show_invite(update, value)
        return
    if action == "start":
        await _start_lobby_callback(update, value)
        return
    if action == "leave":
        await _leave_lobby_callback(update, value)
        return
    if action == "close":
        await _close_lobby_callback(update, value)
        return
    if action == "info":
        await _show_lobby_info(update, value)
        return
    if action == "members":
        await _show_lobby_members(update, value)
        return
    if action == "info_current":
        await _show_current_lobby_info(update)
        return
    if action == "leave_current":
        await _leave_lobby_callback(update, None)
        return
    await _answer_unavailable(update)


async def lobby_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return

    with get_session() as session:
        try:
            user = _ensure_user(session, update)
            if user.pending_action == PENDING_CREATE_ROLE_SEARCH:
                await _handle_create_role_search_message(update, session, user)
                return
            if user.pending_action and user.pending_action.startswith(PENDING_JOIN_ROLE_SEARCH_PREFIX):
                await _handle_join_role_search_message(update, session, user)
                return
            if user.pending_action == PENDING_ENTER_LOBBY_CODE:
                code = (update.message.text or "").replace(" ", "").upper()
                if not code:
                    await update.message.reply_text("Отправь код лобби текстом.")
                    session.commit()
                    return
                try:
                    if user.current_lobby_id is not None:
                        raise LobbyError("already_in_lobby", "Ты уже находишься в лобби.")
                    lobby = lobby_repo.get_by_code(session, code)
                    if lobby is not None and lobby.mode == "rp":
                        _validate_lobby_joinable_for_role_selection(lobby)
                        taken_roles = lobby_member_repo.list_taken_roles(session, lobby.id)
                        clear_pending_action(user)
                        session.commit()
                        await update.message.reply_text(
                            render_join_role(lobby),
                            reply_markup=get_join_role_keyboard(lobby.code, lobby.topic, taken_roles),
                        )
                        return
                    lobby = join_lobby(session, user, code)
                    clear_pending_action(user)
                    auto_start = False
                    if lobby.players_count == lobby.max_players:
                        start_lobby(session, user, lobby.code, force=True)
                        auto_start = True
                    session.commit()
                except LobbyError as exc:
                    session.rollback()
                    if exc.code == "not_found":
                        await update.message.reply_text(
                            "❌ Лобби с таким кодом не найдено.",
                            reply_markup=get_invalid_code_keyboard(),
                        )
                    else:
                        await update.message.reply_text(exc.message)
                    return

                await update.message.reply_text(
                    render_active_lobby_started(lobby) if auto_start else render_lobby_waiting(lobby),
                    reply_markup=get_active_lobby_keyboard(lobby.code)
                    if auto_start
                    else get_lobby_waiting_keyboard(lobby.code, lobby.owner_id == user.id),
                )
                await notify_user_joined(update.get_bot(), lobby.id, user.id)
                if auto_start:
                    await notify_lobby_started(update.get_bot(), lobby.id)
                return

            if user.current_lobby_id is None:
                session.commit()
                await update.message.reply_text("Ты сейчас не находишься в активном лобби.")
                return
            lobby = lobby_repo.get_by_id(session, user.current_lobby_id)
            if lobby is None or lobby.status == "closed":
                user.current_lobby_id = None
                session.commit()
                await update.message.reply_text("Это лобби уже закрыто.")
                return
            if lobby.status != "active":
                session.commit()
                await update.message.reply_text("Лобби ещё не активно. Дождись запуска.")
                return
            payload = lobby_message_service.payload_from_telegram_message(update.message)
            if payload is None:
                session.commit()
                return
            lobby_id = lobby.id
            sender_id = user.id
            session.commit()
        except Exception:
            session.rollback()
            logger.exception("Lobby message handler failed")
            await update.message.reply_text("Не удалось обработать сообщение.")
            return

    await lobby_message_service.send_message_to_lobby(update.get_bot(), lobby_id, sender_id, payload)


async def close_expired_lobbies(context: ContextTypes.DEFAULT_TYPE) -> None:
    await close_expired_lobbies_for_bot(context.bot)


async def close_expired_lobbies_for_bot(bot) -> None:
    with get_session() as session:
        try:
            expired = lobby_repo.list_expired(session, datetime.utcnow())
            lobby_ids = [lobby.id for lobby in expired]
            for lobby in expired:
                close_lobby(session, lobby.id, "expired")
            session.commit()
        except Exception:
            session.rollback()
            logger.exception("Failed to close expired lobbies")
            return

    for lobby_id in lobby_ids:
        await notify_lobby_closed(bot, lobby_id, "expired")


async def start_lobby_background_tasks(application) -> None:
    job_queue = getattr(application, "_job_queue", None)
    if job_queue is not None:
        return
    if application.bot_data.get("lobby_expiration_task_started"):
        return
    application.bot_data["lobby_expiration_task_started"] = True
    application.create_task(_expiration_loop(application), name="rolehub-lobby-expiration")


async def _expiration_loop(application) -> None:
    while True:
        await asyncio.sleep(60)
        await close_expired_lobbies_for_bot(application.bot)


def register_lobby_message_handler(application) -> None:
    application.add_handler(
        MessageHandler(
            (filters.TEXT & ~filters.COMMAND) | filters.PHOTO | filters.Sticker.ALL | filters.VOICE,
            lobby_message_handler,
        )
    )
    job_queue = getattr(application, "_job_queue", None)
    if job_queue is not None:
        job_queue.run_repeating(close_expired_lobbies, interval=60, first=60)


async def _show_create_topic(update: Update) -> None:
    with get_session() as session:
        user = _ensure_user(session, update)
        clear_create_state(user)
        session.commit()
    await _render(update, render_create_topic(), get_topic_keyboard("create"))


async def _set_pending_code_action(update: Update) -> None:
    with get_session() as session:
        user = _ensure_user(session, update)
        set_pending_action(user, PENDING_ENTER_LOBBY_CODE)
        session.commit()
    await _render(
        update,
        "🔑 Вход по коду\n\nОтправь код лобби следующим сообщением.",
        get_code_entry_keyboard(),
    )


async def _confirm_create_lobby(update: Update, bot) -> None:
    with get_session() as session:
        try:
            user = _ensure_user(session, update)
            state = get_create_state(user)
            _validate_create_state(state)
            lobby = create_lobby(session, user, state)
            clear_create_state(user)
            session.commit()
        except LobbyError as exc:
            session.rollback()
            await _show_lobby_error(update, exc)
            return
        except Exception:
            session.rollback()
            logger.exception("Create lobby failed")
            await _render(update, "Не удалось создать лобби.", get_play_main_keyboard())
            return
    await _render(update, render_lobby_waiting(lobby), get_lobby_waiting_keyboard(lobby.code, True))


async def _join_lobby_from_callback(update: Update, code: str, role: str | None = None) -> None:
    with get_session() as session:
        try:
            user = _ensure_user(session, update)
            if user.current_lobby_id is not None:
                raise LobbyError("already_in_lobby", "Ты уже находишься в лобби.")
            lobby = lobby_repo.get_by_code(session, code)
            if lobby is None:
                raise LobbyError("not_found", "Лобби с таким кодом не найдено.")
            if lobby.mode == "rp" and role is None:
                _validate_lobby_joinable_for_role_selection(lobby)
                taken_roles = lobby_member_repo.list_taken_roles(session, lobby.id)
                session.commit()
                await _render(
                    update,
                    render_join_role(lobby),
                    get_join_role_keyboard(lobby.code, lobby.topic, taken_roles),
                )
                return
            if role == "random":
                taken_roles = lobby_member_repo.list_taken_roles(session, lobby.id)
                role = _resolve_random_free_role(lobby.topic, taken_roles)
            lobby = join_lobby(session, user, code, role=role)
            clear_pending_action(user)
            auto_start = False
            if lobby.players_count == lobby.max_players:
                start_lobby(session, user, lobby.code, force=True)
                auto_start = True
            session.commit()
        except LobbyError as exc:
            session.rollback()
            await _show_lobby_error(update, exc)
            return
        except Exception:
            session.rollback()
            logger.exception("Join lobby failed")
            await _render(update, "Не удалось войти в лобби.", get_play_main_keyboard())
            return

    await notify_user_joined(update.get_bot(), lobby.id, user.id)
    if auto_start:
        await notify_lobby_started(update.get_bot(), lobby.id)
        await _render(update, render_active_lobby_started(lobby), get_active_lobby_keyboard(lobby.code))
        return
    await _show_lobby_waiting(update, lobby.code)


async def _start_lobby_callback(update: Update, code: str) -> None:
    with get_session() as session:
        try:
            user = _ensure_user(session, update)
            lobby = start_lobby(session, user, code)
            session.commit()
        except LobbyError as exc:
            session.rollback()
            await _show_lobby_error(update, exc)
            return
        except Exception:
            session.rollback()
            logger.exception("Start lobby failed")
            await _render(update, "Не удалось запустить лобби.", get_play_main_keyboard())
            return
    await notify_lobby_started(update.get_bot(), lobby.id)
    await _render(update, render_active_lobby_started(lobby), get_active_lobby_keyboard(lobby.code, True))


async def _leave_lobby_callback(update: Update, code: str | None) -> None:
    with get_session() as session:
        try:
            user = _ensure_user(session, update)
            user_id = user.id
            lobby, closed, owner_changed = leave_lobby(session, user, code)
            lobby_id = lobby.id
            session.commit()
        except LobbyError as exc:
            session.rollback()
            await _show_lobby_error(update, exc)
            return
        except Exception:
            session.rollback()
            logger.exception("Leave lobby failed")
            await _render(update, "Не удалось выйти из лобби.", get_play_main_keyboard())
            return

    await _render(update, "🚪 Ты вышел из лобби.", get_leave_done_keyboard())
    if closed:
        await notify_lobby_closed(update.get_bot(), lobby_id, "empty")
        return
    await notify_user_left(update.get_bot(), lobby_id, user_id)
    if owner_changed:
        await notify_owner_changed(update.get_bot(), lobby_id)


async def _close_lobby_callback(update: Update, code: str) -> None:
    with get_session() as session:
        try:
            user = _ensure_user(session, update)
            lobby = lobby_repo.get_by_code(session, code)
            if lobby is None:
                raise LobbyError("not_found", "Лобби не найдено.")
            if lobby.owner_id != user.id:
                raise LobbyError("not_owner", "Закрыть лобби может только владелец.")
            lobby_id = lobby.id
            close_lobby(session, lobby.id, "manual")
            session.commit()
        except LobbyError as exc:
            session.rollback()
            await _show_lobby_error(update, exc)
            return
        except Exception:
            session.rollback()
            logger.exception("Close lobby failed")
            await _render(update, "Не удалось закрыть лобби.", get_play_main_keyboard())
            return

    await _render(update, "🏁 Лобби закрыто.", get_leave_done_keyboard())
    await notify_lobby_closed(update.get_bot(), lobby_id, "manual")


async def _show_lobby_waiting(update: Update, code: str) -> None:
    with get_session() as session:
        user = _ensure_user(session, update)
        lobby = lobby_repo.get_by_code(session, code)
        if lobby is None:
            await _render(update, "Это лобби уже закрыто.", get_play_main_keyboard())
            return
        member = lobby_member_repo.get_joined_member(session, lobby.id, user.id)
        if member is None:
            await _render(update, "Это действие больше недоступно. Открой актуальное меню.", get_play_main_keyboard())
            return
        keyboard = (
            get_active_lobby_keyboard(lobby.code, member.is_owner)
            if lobby.status == "active"
            else get_lobby_waiting_keyboard(lobby.code, member.is_owner)
        )
        text = render_active_lobby_started(lobby) if lobby.status == "active" else render_lobby_waiting(lobby)
    await _render(update, text, keyboard)


async def _show_join_role_page(update: Update, code: str, page: int = 0) -> None:
    with get_session() as session:
        try:
            user = _ensure_user(session, update)
            if user.current_lobby_id is not None:
                raise LobbyError("already_in_lobby", "Ты уже находишься в лобби.")
            lobby = lobby_repo.get_by_code(session, code)
            if lobby is None:
                raise LobbyError("not_found", "Лобби с таким кодом не найдено.")
            _validate_lobby_joinable_for_role_selection(lobby)
            taken_roles = lobby_member_repo.list_taken_roles(session, lobby.id)
            session.commit()
        except LobbyError as exc:
            session.rollback()
            await _show_lobby_error(update, exc)
            return

    await _render(
        update,
        render_join_role(lobby),
        get_join_role_keyboard(lobby.code, lobby.topic, taken_roles, page),
    )


async def _start_join_role_search(update: Update, code: str) -> None:
    with get_session() as session:
        try:
            user = _ensure_user(session, update)
            if user.current_lobby_id is not None:
                raise LobbyError("already_in_lobby", "Ты уже находишься в лобби.")
            lobby = lobby_repo.get_by_code(session, code)
            if lobby is None:
                raise LobbyError("not_found", "Лобби с таким кодом не найдено.")
            _validate_lobby_joinable_for_role_selection(lobby)
            set_pending_action(user, f"{PENDING_JOIN_ROLE_SEARCH_PREFIX}{lobby.code}")
            session.commit()
        except LobbyError as exc:
            session.rollback()
            await _show_lobby_error(update, exc)
            return

    await _render(
        update,
        "🔎 Поиск роли\n\nНапиши имя роли или часть имени. Например: Твайлайт, Спаркл, 8-Бит.",
        get_role_search_prompt_keyboard(f"lobby:roles:{code}:0"),
    )


async def _show_invite(update: Update, code: str) -> None:
    with get_session() as session:
        lobby = lobby_repo.get_by_code(session, code)
        if lobby is None:
            await _answer_unavailable(update)
            return
        if lobby.privacy == "private":
            text = f"📨 Приглашение\n\nКод приватного лобби: {lobby.code}"
        else:
            text = "📨 Это открытое лобби доступно через поиск."
    await _render(update, text, get_lobby_waiting_keyboard(code, True))


async def _show_lobby_info(update: Update, code: str) -> None:
    with get_session() as session:
        user = _ensure_user(session, update)
        lobby = lobby_repo.get_by_code(session, code)
        if lobby is None:
            await _answer_unavailable(update)
            return
        member = lobby_member_repo.get_joined_member(session, lobby.id, user.id)
        is_owner = bool(member and member.is_owner)
    await _render(update, render_lobby_info(lobby), get_active_lobby_keyboard(lobby.code, is_owner))


async def _show_current_lobby_info(update: Update) -> None:
    with get_session() as session:
        user = _ensure_user(session, update)
        lobby = lobby_repo.get_current_for_user(session, user)
        if lobby is None:
            await _render(update, "Ты сейчас не находишься в лобби.", get_play_main_keyboard())
            return
        code = lobby.code
    await _show_lobby_info(update, code)


async def _show_lobby_members(update: Update, code: str) -> None:
    with get_session() as session:
        lobby = lobby_repo.get_by_code(session, code)
        if lobby is None:
            await _answer_unavailable(update)
            return
        members = lobby_member_repo.list_joined_users(session, lobby.id)
        lines = ["👥 Участники лобби\n"]
        for index, (member, user) in enumerate(members, start=1):
            crown = " 👑" if member.is_owner else ""
            name = role_name(lobby.topic, member.role) if lobby.mode == "rp" else format_display_name(user)
            lines.append(f"{index}. {name}{crown}")
    await _render(update, "\n".join(lines), get_lobby_members_keyboard(code))


async def _show_found_lobby(update: Update, topic: str) -> None:
    with get_session() as session:
        user = _ensure_user(session, update)
        lobby = find_available_lobby(session, topic, user_id=user.id)
    if lobby is None:
        await _render(update, render_no_lobby(topic), get_no_lobby_keyboard(topic, f"find:topic:{topic}"))
        return
    await _render(update, render_found_lobby(lobby), get_found_lobby_keyboard(lobby.code, topic))


async def _handle_create_role_search_message(update: Update, session, user) -> None:
    query = (update.message.text or "").strip()
    state = get_create_state(user)
    topic = state.get("topic")
    results = search_roles(topic, query)
    session.commit()

    if not results:
        await update.message.reply_text(
            "Роль не найдена. Напиши другое имя или часть имени.",
            reply_markup=get_role_search_prompt_keyboard("create:role_search"),
        )
        return

    await update.message.reply_text(
        "Нашёл роли. Выбери нужную:",
        reply_markup=get_role_search_results_keyboard(
            "create:role",
            results,
            "create:role_search",
        ),
    )


async def _handle_join_role_search_message(update: Update, session, user) -> None:
    query = (update.message.text or "").strip()
    code = user.pending_action.removeprefix(PENDING_JOIN_ROLE_SEARCH_PREFIX)
    lobby = lobby_repo.get_by_code(session, code)
    if lobby is None:
        clear_pending_action(user)
        session.commit()
        await update.message.reply_text("Лобби не найдено.", reply_markup=get_play_main_keyboard())
        return

    try:
        _validate_lobby_joinable_for_role_selection(lobby)
    except LobbyError as exc:
        clear_pending_action(user)
        session.commit()
        await update.message.reply_text(exc.message, reply_markup=get_play_main_keyboard())
        return

    taken_roles = lobby_member_repo.list_taken_roles(session, lobby.id)
    results = search_roles(lobby.topic, query, taken_roles)
    session.commit()

    if not results:
        await update.message.reply_text(
            "Роль не найдена или уже занята. Напиши другое имя или часть имени.",
            reply_markup=get_role_search_prompt_keyboard(f"lobby:role_search:{code}"),
        )
        return

    await update.message.reply_text(
        "Нашёл свободные роли. Выбери нужную:",
        reply_markup=get_role_search_results_keyboard(
            f"lobby:role:{code}",
            results,
            f"lobby:role_search:{code}",
        ),
    )


async def _handle_create_back(update: Update, value: str) -> None:
    with get_session() as session:
        user = _ensure_user(session, update)
        state = get_create_state(user)
    if value == "topic":
        await _show_create_topic(update)
    elif value == "mode":
        await _render(update, render_create_mode(state.get("topic")), get_create_mode_keyboard())
    elif value == "role_or_mode":
        if state.get("mode") == "rp":
            await _render(update, render_create_role(state.get("topic")), get_create_role_keyboard(state.get("topic")))
        else:
            await _render(update, render_create_mode(state.get("topic")), get_create_mode_keyboard())
    elif value == "size":
        await _render(update, render_create_size(), get_create_size_keyboard())
    elif value == "privacy":
        await _render(update, render_create_privacy(), get_create_privacy_keyboard())
    else:
        await _answer_unavailable(update)


async def _show_lobby_error(update: Update, exc: LobbyError) -> None:
    if exc.code == "already_in_lobby":
        await _render(update, "Ты уже находишься в лобби.", get_already_in_lobby_keyboard())
    elif exc.code == "full":
        await _render(update, "Это лобби уже заполнено.", get_lobby_full_keyboard())
    elif exc.code == "closed":
        await _render(update, "Это лобби уже закрыто.", get_play_main_keyboard())
    else:
        await _render(update, exc.message, get_play_main_keyboard())


def _ensure_user(session, update: Update):
    return ensure_from_effective_user(session, update.effective_user)


def _resolve_role(topic: str | None, role: str) -> str | None:
    roles = ROLES_BY_TOPIC.get(topic or "", {})
    if role == "random":
        return random.choice(list(roles.keys())) if roles else None
    return role if role in roles else None


def _resolve_random_free_role(topic: str | None, taken_roles: set[str]) -> str | None:
    roles = [
        role
        for role in ROLES_BY_TOPIC.get(topic or "", {})
        if role not in taken_roles
    ]
    return random.choice(roles) if roles else None


def _safe_page(value: str) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def _validate_lobby_joinable_for_role_selection(lobby) -> None:
    if lobby.status == "closed":
        raise LobbyError("closed", "Это лобби уже закрыто.")
    if lobby.status != "waiting":
        raise LobbyError("not_waiting", "Это лобби уже не ожидает участников.")
    if lobby.players_count >= lobby.max_players:
        raise LobbyError("full", "Это лобби уже заполнено.")


def _validate_create_state(state: dict) -> None:
    required = {"topic", "mode", "max_players", "privacy"}
    if not required.issubset(state):
        raise LobbyError("invalid_state", "Настройки лобби неполные. Начни создание заново.")


async def _answer_unavailable(update: Update) -> None:
    if update.callback_query is not None:
        await update.callback_query.answer("Действие недоступно")
