"""Handlers для lobby-механики RoleHub."""

import asyncio
import random
from datetime import datetime

from telegram import Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

from src.constants.pending_actions import (
    PENDING_CREATE_ROLE_SEARCH,
    PENDING_CREATE_MAX_PLAYERS,
    PENDING_ENTER_LOBBY_CODE,
    PENDING_JOIN_ROLE_SEARCH_PREFIX,
    PENDING_SET_DISPLAY_NAME,
)
from src.constants.roles import ROLES_BY_TOPIC, search_roles
from src.core.database import get_session
from src.core.logger import logger
from src.keyboards.lobby_keyboard import (
    BTN_BACK,
    BTN_CLOSE,
    BTN_CREATE_CONFIRM,
    BTN_CREATE_LOBBY,
    BTN_CREATE_OWN,
    BTN_EDIT,
    BTN_FIND_ANOTHER,
    BTN_FIND_LOBBY,
    BTN_FIND_ROLE,
    BTN_INFO,
    BTN_INVITE,
    BTN_JOIN,
    BTN_LEAVE,
    BTN_MAIN_MENU,
    BTN_MEMBERS,
    BTN_NEXT,
    BTN_PLAY,
    BTN_PRIVATE,
    BTN_PUBLIC,
    BTN_RANDOM_FREE_ROLE,
    BTN_RANDOM_ROLE,
    BTN_REFRESH,
    BTN_RETURN_TO_LOBBY,
    BTN_SEARCH_AGAIN,
    BTN_SEARCH_BY_CODE,
    BTN_SEARCH_MORE,
    BTN_SELECT_TOPIC,
    BTN_START,
    BTN_TRY_AGAIN,
    CB_CREATE_ROLE_PAGE_PREFIX,
    CB_CREATE_ROLE_PREFIX,
    CB_CREATE_SEARCH_ROLE_PREFIX,
    CB_FIND_ROLE,
    CB_JOIN_ROLE_PAGE_PREFIX,
    CB_JOIN_ROLE_PREFIX,
    CB_JOIN_SEARCH_ROLE_PREFIX,
    CB_LOBBY_LIST_PAGE_PREFIX,
    CB_LOBBY_SELECT_PREFIX,
    CB_RANDOM_FREE_ROLE,
    CB_RANDOM_ROLE,
    CB_SEARCH_MORE,
    CB_TOPIC_PREFIX,
    get_active_lobby_reply_keyboard,
    get_already_in_lobby_reply_keyboard,
    get_code_entry_reply_keyboard,
    get_create_confirm_reply_keyboard,
    get_create_privacy_reply_keyboard,
    get_create_role_inline_keyboard,
    get_create_role_search_results_inline_keyboard,
    get_done_reply_keyboard,
    get_find_main_reply_keyboard,
    get_found_lobby_reply_keyboard,
    get_invalid_code_reply_keyboard,
    get_join_role_inline_keyboard,
    get_join_role_search_results_inline_keyboard,
    get_lobby_info_reply_keyboard,
    get_lobby_list_inline_keyboard,
    get_lobby_full_reply_keyboard,
    get_lobby_members_reply_keyboard,
    get_lobby_waiting_reply_keyboard,
    get_navigation_reply_keyboard,
    get_no_lobby_reply_keyboard,
    get_play_main_reply_keyboard,
    get_role_search_prompt_reply_keyboard,
    get_topic_inline_keyboard,
    get_remove_lobby_reply_keyboard,
    role_by_label,
    topic_by_label,
)
from src.render.lobby_render import (
    render_active_lobby_started,
    render_create_confirm,
    render_create_role,
    render_create_topic,
    render_found_lobby,
    render_lobby_info,
    render_lobby_waiting,
    render_no_lobby,
    render_join_role,
    render_play_main,
    role_name,
    topic_name,
)
from src.render.menu import _render, showMainMenu, showSettings, showShop, showShopPremium, showSupport, showSupportFaq
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
from src.services.chat_cleanup_service import delete_known_message, remember_telegram_message, reply_text
from src.services.user_service import DisplayNameError, ensure_from_effective_user, set_display_name
from src.services.user_state_service import (
    clear_create_state,
    clear_pending_action,
    get_create_state,
    set_create_state,
    set_pending_action,
)
from src.utils.display_name import format_display_name


async def show_play_menu(update: Update) -> None:
    await _show_play_main(update)


async def show_current_lobby(update: Update) -> None:
    await _show_current_lobby(update)


async def lobby_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return

    with get_session() as session:
        try:
            user = _ensure_user(session, update)
            if await _handle_reply_keyboard_message(update, session, user):
                return
            if user.pending_action == PENDING_SET_DISPLAY_NAME:
                await _handle_display_name_message(update, session, user)
                return
            if user.pending_action == PENDING_CREATE_ROLE_SEARCH:
                await _handle_create_role_search_message(update, session, user)
                return
            if user.pending_action == PENDING_CREATE_MAX_PLAYERS:
                await _handle_create_max_players_message(update, session, user)
                return
            if user.pending_action and user.pending_action.startswith(PENDING_JOIN_ROLE_SEARCH_PREFIX):
                await _handle_join_role_search_message(update, session, user)
                return
            if user.pending_action == PENDING_ENTER_LOBBY_CODE:
                code = (update.message.text or "").replace(" ", "").upper()
                if not code:
                    await reply_text(update.message, "Отправь код лобби текстом.")
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
                        set_create_state(
                            session,
                            user,
                            {
                                "reply_scene": "join_role",
                                "code": lobby.code,
                                "topic": lobby.topic,
                                "page": 0,
                            },
                        )
                        session.commit()
                        await reply_text(
                            update.message,
                            render_join_role(lobby),
                            reply_markup=get_navigation_reply_keyboard(),
                        )
                        await _render(
                            update,
                            "Роли:",
                            get_join_role_inline_keyboard(lobby.code, lobby.topic, taken_roles),
                        )
                        return
                    lobby = join_lobby(session, user, code)
                    clear_pending_action(user)
                    is_active = lobby.status == "active"
                    set_create_state(
                        session,
                        user,
                        {
                            "reply_scene": "active_lobby" if is_active else "waiting_lobby",
                            "code": lobby.code,
                        },
                    )
                    session.commit()
                except LobbyError as exc:
                    session.rollback()
                    if exc.code == "not_found":
                        await reply_text(
                            update.message,
                            "❌ Лобби с таким кодом не найдено.",
                            reply_markup=get_invalid_code_reply_keyboard(),
                        )
                    else:
                        await reply_text(update.message, exc.message)
                    return

                await reply_text(
                    update.message,
                    render_active_lobby_started(lobby) if is_active else render_lobby_waiting(lobby),
                    reply_markup=get_active_lobby_reply_keyboard(lobby.owner_id == user.id)
                    if is_active
                    else get_lobby_waiting_reply_keyboard(lobby.owner_id == user.id),
                )
                await notify_user_joined(update.get_bot(), lobby.id, user.id)
                return

            if user.current_lobby_id is None:
                session.commit()
                await reply_text(update.message, "Ты сейчас не находишься в активном лобби.")
                return
            lobby = lobby_repo.get_by_id(session, user.current_lobby_id)
            if lobby is None or lobby.status == "closed":
                user.current_lobby_id = None
                session.commit()
                await reply_text(update.message, "Это лобби уже закрыто.")
                return
            if lobby.status != "active":
                session.commit()
                await reply_text(update.message, "Лобби ещё не активно. Дождись запуска.")
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
            await reply_text(update.message, "Не удалось обработать сообщение.")
            return

    await lobby_message_service.send_message_to_lobby(update.get_bot(), lobby_id, sender_id, payload)


async def lobby_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or query.data is None:
        return

    await query.answer()
    data = query.data

    with get_session() as session:
        try:
            user = _ensure_user(session, update)
            state = get_create_state(user)
            scene = state.get("reply_scene")

            if data.startswith(CB_LOBBY_LIST_PAGE_PREFIX) and scene == "lobby_list":
                page = _callback_int(data, CB_LOBBY_LIST_PAGE_PREFIX)
                topic = state.get("topic")
                set_create_state(session, user, {"reply_scene": "lobby_list", "page": page, "topic": topic})
                lobbies = lobby_repo.list_available_active(session, topic=topic, user_id=user.id)
                page_lobbies, safe_page, pages_count = _paginate_lobbies(lobbies, page)
                session.commit()
                await query.edit_message_reply_markup(
                    reply_markup=get_lobby_list_inline_keyboard(
                        _lobby_list_buttons(page_lobbies),
                        safe_page,
                        pages_count,
                    )
                )
                return

            if data.startswith(CB_LOBBY_SELECT_PREFIX) and scene == "lobby_list":
                code = data.removeprefix(CB_LOBBY_SELECT_PREFIX)
                session.commit()
                await _join_lobby_from_reply(update, code)
                await _delete_callback_message(update)
                return

            if data.startswith(CB_TOPIC_PREFIX):
                topic = data.removeprefix(CB_TOPIC_PREFIX)
                if scene == "create_topic":
                    set_create_state(session, user, {"reply_scene": "create_role", "topic": topic, "page": 0})
                    session.commit()
                    await _render_role_choice(update, render_create_role(topic), get_create_role_inline_keyboard(topic))
                    await _delete_callback_message(update)
                    return
                if scene == "find_topic":
                    set_create_state(session, user, {"reply_scene": "lobby_list", "topic": topic, "page": 0})
                    session.commit()
                    await _show_lobby_list(update, topic=topic, page=0)
                    await _delete_callback_message(update)
                    return

            if data.startswith(CB_CREATE_ROLE_PAGE_PREFIX) and scene == "create_role":
                topic = state.get("topic")
                page = _callback_int(data, CB_CREATE_ROLE_PAGE_PREFIX)
                if page == int(state.get("page", 0) or 0):
                    session.commit()
                    return
                set_create_state(session, user, {"reply_scene": "create_role", "page": page})
                session.commit()
                await query.edit_message_reply_markup(reply_markup=get_create_role_inline_keyboard(topic, page))
                return

            if data.startswith(CB_JOIN_ROLE_PAGE_PREFIX) and scene == "join_role":
                code = state.get("code")
                topic = state.get("topic")
                page = _callback_int(data, CB_JOIN_ROLE_PAGE_PREFIX)
                if page == int(state.get("page", 0) or 0):
                    session.commit()
                    return
                lobby = lobby_repo.get_by_code(session, code) if code else None
                taken_roles = set()
                if lobby is not None:
                    taken_roles = lobby_member_repo.list_taken_roles(session, lobby.id)
                set_create_state(session, user, {"reply_scene": "join_role", "page": page})
                session.commit()
                await query.edit_message_reply_markup(
                    reply_markup=get_join_role_inline_keyboard(code, topic, taken_roles, page)
                )
                return

            if data == CB_FIND_ROLE and scene == "create_role":
                set_pending_action(user, PENDING_CREATE_ROLE_SEARCH)
                set_create_state(session, user, {"reply_scene": "create_role_search"})
                session.commit()
                await _render(
                    update,
                    "🔎 Поиск роли\n\nНапиши имя роли или часть имени. Например: Твайлайт, Спаркл, 8-Бит.",
                    get_role_search_prompt_reply_keyboard(),
                )
                await _delete_callback_message(update)
                return

            if data == CB_FIND_ROLE and scene == "join_role":
                code = state.get("code")
                topic = state.get("topic")
                set_pending_action(user, f"{PENDING_JOIN_ROLE_SEARCH_PREFIX}{code}")
                set_create_state(session, user, {"reply_scene": "join_role_search", "code": code, "topic": topic})
                session.commit()
                await _render(update, "🔎 Поиск роли\n\nНапиши имя роли или часть имени.", get_role_search_prompt_reply_keyboard())
                await _delete_callback_message(update)
                return

            if data == CB_RANDOM_ROLE and scene == "create_role":
                topic = state.get("topic")
                role = _resolve_role(topic, "random")
                await _select_create_role_reply(update, session, user, topic, role, was_random=True)
                await _delete_callback_message(update)
                return

            if data == CB_RANDOM_FREE_ROLE and scene == "join_role":
                code = state.get("code")
                session.commit()
                await _join_lobby_from_reply(update, code, "random")
                await _delete_callback_message(update)
                return

            if data.startswith(CB_CREATE_ROLE_PREFIX) and scene == "create_role":
                topic = state.get("topic")
                role = _resolve_role(topic, data.removeprefix(CB_CREATE_ROLE_PREFIX))
                await _select_create_role_reply(update, session, user, topic, role)
                await _delete_callback_message(update)
                return

            if data.startswith(CB_JOIN_ROLE_PREFIX) and scene == "join_role":
                code = state.get("code")
                topic = state.get("topic")
                role = _resolve_role(topic, data.removeprefix(CB_JOIN_ROLE_PREFIX))
                session.commit()
                await _join_lobby_from_reply(update, code, role)
                await _delete_callback_message(update)
                return

            if data == CB_SEARCH_MORE and scene == "create_role_search_results":
                set_pending_action(user, PENDING_CREATE_ROLE_SEARCH)
                set_create_state(session, user, {"reply_scene": "create_role_search"})
                session.commit()
                await _render(update, "🔎 Поиск роли\n\nНапиши имя роли или часть имени.", get_role_search_prompt_reply_keyboard())
                await _delete_callback_message(update)
                return

            if data == CB_SEARCH_MORE and scene == "join_role_search_results":
                code = state.get("code")
                topic = state.get("topic")
                set_pending_action(user, f"{PENDING_JOIN_ROLE_SEARCH_PREFIX}{code}")
                set_create_state(session, user, {"reply_scene": "join_role_search", "code": code, "topic": topic})
                session.commit()
                await _render(update, "🔎 Поиск роли\n\nНапиши имя роли или часть имени.", get_role_search_prompt_reply_keyboard())
                await _delete_callback_message(update)
                return

            if data.startswith(CB_CREATE_SEARCH_ROLE_PREFIX) and scene == "create_role_search_results":
                topic = state.get("topic")
                role = _resolve_role(topic, data.removeprefix(CB_CREATE_SEARCH_ROLE_PREFIX))
                await _select_create_role_reply(update, session, user, topic, role)
                await _delete_callback_message(update)
                return

            if data.startswith(CB_JOIN_SEARCH_ROLE_PREFIX) and scene == "join_role_search_results":
                code = state.get("code")
                topic = state.get("topic")
                role = _resolve_role(topic, data.removeprefix(CB_JOIN_SEARCH_ROLE_PREFIX))
                session.commit()
                await _join_lobby_from_reply(update, code, role)
                await _delete_callback_message(update)
                return

            session.commit()
        except Exception:
            session.rollback()
            logger.exception("Lobby callback handler failed")
            await _render(update, "Не удалось обработать действие.", get_play_main_reply_keyboard())


async def _handle_reply_keyboard_message(update: Update, session, user) -> bool:
    if update.message is None or update.message.text is None:
        return False

    text = update.message.text.strip()
    state = get_create_state(user)
    scene = state.get("reply_scene")

    if scene is None and user.current_lobby_id is not None and text in {BTN_MEMBERS, BTN_INFO, BTN_CLOSE, BTN_LEAVE}:
        lobby = lobby_repo.get_by_id(session, user.current_lobby_id)
        if lobby is not None:
            scene = "active_lobby" if lobby.status == "active" else "waiting_lobby"
            state = set_create_state(session, user, {"reply_scene": scene, "code": lobby.code})

    if text == BTN_MAIN_MENU:
        clear_pending_action(user)
        clear_create_state(user)
        session.commit()
        await _show_main_menu_and_remove_reply_keyboard(update)
        return True

    if text == BTN_BACK:
        await _handle_reply_back(update, session, user, state, scene)
        return True

    if text == BTN_LEAVE and user.current_lobby_id is not None:
        session.commit()
        await _leave_current_lobby(update)
        return True

    if text == BTN_PLAY:
        clear_pending_action(user)
        set_create_state(session, user, {"reply_scene": "play_main"})
        has_current_lobby = _has_current_open_lobby(session, user)
        session.commit()
        await _render(update, render_play_main(), get_play_main_reply_keyboard(has_current_lobby))
        return True

    if text in {BTN_CREATE_LOBBY, BTN_CREATE_OWN}:
        clear_pending_action(user)
        clear_create_state(user)
        set_create_state(session, user, {"reply_scene": "create_privacy", "mode": "rp"})
        session.commit()
        await _render(update, "➕ Создание лобби\n\nВыбери тип лобби:", get_create_privacy_reply_keyboard())
        return True

    if text in {BTN_FIND_LOBBY, BTN_FIND_ANOTHER}:
        clear_pending_action(user)
        set_create_state(session, user, {"reply_scene": "find_topic"})
        session.commit()
        await _render_topic_choice(update, "🔎 Найти лобби\n\nВыбери тему:")
        return True

    if scene == "play_main":
        return False

    if scene == "find_main":
        if text == BTN_SEARCH_BY_CODE:
            set_pending_action(user, PENDING_ENTER_LOBBY_CODE)
            set_create_state(session, user, {"reply_scene": "code_entry"})
            session.commit()
            await _render(
                update,
                "🔑 Вход по коду\n\nОтправь код лобби следующим сообщением.",
                get_code_entry_reply_keyboard(),
            )
            return True
        if text == BTN_SELECT_TOPIC:
            set_create_state(session, user, {"reply_scene": "find_topic"})
            session.commit()
            await _render_topic_choice(update, "🔎 Поиск лобби\n\nВыбери тему:")
            return True
        return False

    if scene == "create_privacy" and text in {BTN_PUBLIC, BTN_PRIVATE}:
        privacy = "public" if text == BTN_PUBLIC else "private"
        set_create_state(session, user, {"reply_scene": "create_topic", "privacy": privacy})
        session.commit()
        await _render_topic_choice(update, render_create_topic())
        return True

    if scene == "create_topic":
        topic = topic_by_label(text)
        if topic is None:
            return False
        set_create_state(session, user, {"reply_scene": "create_role", "topic": topic, "page": 0})
        session.commit()
        await _render_role_choice(update, render_create_role(topic), get_create_role_inline_keyboard(topic))
        return True

    if scene == "create_role":
        return await _handle_create_role_reply(update, session, user, state, text)

    if scene == "create_role_search_results":
        return await _handle_create_role_search_result_reply(update, session, user, state, text)

    if scene == "create_confirm":
        if text == BTN_CREATE_CONFIRM:
            session.commit()
            await _confirm_create_lobby(update, update.get_bot())
            return True
        if text == BTN_EDIT:
            clear_create_state(user)
            set_create_state(session, user, {"reply_scene": "create_privacy", "mode": "rp"})
            session.commit()
            await _render(update, "➕ Создание лобби\n\nВыбери тип лобби:", get_create_privacy_reply_keyboard())
            return True
        return False

    if scene == "find_topic":
        topic = topic_by_label(text)
        if topic is None:
            return False
        session.commit()
        await _show_lobby_list(update, topic=topic, page=0)
        return True

    if scene == "found_lobby":
        code = state.get("code")
        topic = state.get("topic")
        if text == BTN_JOIN and code:
            session.commit()
            await _join_lobby_from_reply(update, code)
            return True
        if text == BTN_NEXT and topic and code:
            session.commit()
            await _show_next_lobby(update, topic, code)
            return True
        return False

    if scene == "no_lobby":
        topic = state.get("topic")
        if text == BTN_SEARCH_AGAIN and topic:
            session.commit()
            await _show_found_lobby(update, topic)
            return True
        return False

    if scene == "join_role":
        return await _handle_join_role_reply(update, session, user, state, text)

    if scene == "join_role_search_results":
        return await _handle_join_role_search_result_reply(update, session, user, state, text)

    if scene == "lobby_list":
        return False

    if scene == "code_entry" and text == BTN_TRY_AGAIN:
        set_pending_action(user, PENDING_ENTER_LOBBY_CODE)
        session.commit()
        await _render(
            update,
            "🔑 Вход по коду\n\nОтправь код лобби следующим сообщением.",
            get_code_entry_reply_keyboard(),
        )
        return True

    if scene == "waiting_lobby":
        return await _handle_waiting_lobby_reply(update, session, user, state, text)

    if scene in {"active_lobby", "lobby_info", "lobby_members"}:
        return await _handle_active_lobby_reply(update, session, user, state, scene, text)

    if text == BTN_RETURN_TO_LOBBY:
        session.commit()
        await _show_current_lobby(update)
        return True

    return False


async def _handle_reply_back(update: Update, session, user, state: dict, scene: str | None) -> None:
    if scene in {None, "play_main"} and state.get("menu_scene"):
        await _handle_menu_back_from_lobby_router(update, session, user, state)
        return

    if scene in {None, "play_main"}:
        clear_pending_action(user)
        clear_create_state(user)
        session.commit()
        await _show_main_menu_and_remove_reply_keyboard(update)
        return

    if scene in {"create_privacy", "find_main", "find_topic"}:
        clear_pending_action(user)
        set_create_state(session, user, {"reply_scene": "play_main"})
        has_current_lobby = _has_current_open_lobby(session, user)
        session.commit()
        await _render(update, render_play_main(), get_play_main_reply_keyboard(has_current_lobby))
        return

    if scene == "create_topic":
        set_create_state(session, user, {"reply_scene": "create_privacy"})
        session.commit()
        await _render(update, "➕ Создание лобби\n\nВыбери тип лобби:", get_create_privacy_reply_keyboard())
        return

    if scene in {"create_role", "create_role_search", "create_role_search_results"}:
        set_create_state(session, user, {"reply_scene": "create_topic"})
        clear_pending_action(user)
        session.commit()
        await _render_topic_choice(update, render_create_topic())
        return

    if scene == "create_max_players":
        topic = state.get("topic")
        set_create_state(session, user, {"reply_scene": "create_role"})
        clear_pending_action(user)
        session.commit()
        await _render_role_choice(update, render_create_role(topic), get_create_role_inline_keyboard(topic))
        return

    if scene == "create_confirm":
        topic = state.get("topic")
        set_create_state(session, user, {"reply_scene": "create_max_players"})
        set_pending_action(user, PENDING_CREATE_MAX_PLAYERS)
        session.commit()
        await _render(update, _render_create_max_players_prompt(topic), get_navigation_reply_keyboard())
        return

    if scene in {"find_topic", "code_entry"}:
        clear_pending_action(user)
        set_create_state(session, user, {"reply_scene": "find_main"})
        session.commit()
        await _render(update, "🔎 Найти лобби\n\nВыбери способ поиска:", get_find_main_reply_keyboard())
        return

    if scene in {"found_lobby", "no_lobby"}:
        set_create_state(session, user, {"reply_scene": "find_topic"})
        session.commit()
        await _render_topic_choice(update, "🔎 Поиск лобби\n\nВыбери тему:")
        return

    if scene in {"join_role", "join_role_search", "join_role_search_results"}:
        clear_pending_action(user)
        topic = state.get("topic")
        set_create_state(session, user, {"reply_scene": "lobby_list", "page": 0, "topic": topic})
        session.commit()
        await _show_lobby_list(update, topic=topic, page=0)
        return

    if scene == "lobby_list":
        set_create_state(session, user, {"reply_scene": "find_topic"})
        session.commit()
        await _render_topic_choice(update, "🔎 Найти лобби\n\nВыбери тему:")
        return

    if scene == "lobby_members":
        code = state.get("code")
        session.commit()
        await _show_lobby_info(update, code)
        return

    if scene == "lobby_info":
        code = state.get("code")
        session.commit()
        await _show_lobby_waiting(update, code)
        return

    has_current_lobby = _has_current_open_lobby(session, user)
    session.commit()
    await _render(update, render_play_main(), get_play_main_reply_keyboard(has_current_lobby))


async def _handle_menu_back_from_lobby_router(update: Update, session, user, state: dict) -> None:
    menu_scene = state.get("menu_scene")
    if menu_scene == "support_faq_answer":
        set_create_state(session, user, {"menu_scene": "support_faq"})
        session.commit()
        await showSupportFaq(update)
        return
    if menu_scene in {"support_faq", "support"}:
        set_create_state(session, user, {"menu_scene": "support"})
        session.commit()
        await showSupport(update)
        return
    if menu_scene == "shop_premium":
        set_create_state(session, user, {"menu_scene": "shop"})
        session.commit()
        await showShopPremium(update)
        return
    if menu_scene == "shop":
        set_create_state(session, user, {"menu_scene": "shop"})
        session.commit()
        await showShop(update)
        return
    if menu_scene == "settings":
        set_create_state(session, user, {"menu_scene": "settings"})
        session.commit()
        await showSettings(update)
        return

    clear_pending_action(user)
    clear_create_state(user)
    session.commit()
    await _show_main_menu_and_remove_reply_keyboard(update)


async def _handle_create_role_reply(update: Update, session, user, state: dict, text: str) -> bool:
    topic = state.get("topic")
    page = int(state.get("page", 0) or 0)

    if text == "◀️":
        page = max(0, page - 1)
        set_create_state(session, user, {"reply_scene": "create_role", "page": page})
        session.commit()
        await _render_role_choice(update, render_create_role(topic), get_create_role_inline_keyboard(topic, page))
        return True

    if text == "▶️":
        page += 1
        set_create_state(session, user, {"reply_scene": "create_role", "page": page})
        session.commit()
        await _render_role_choice(update, render_create_role(topic), get_create_role_inline_keyboard(topic, page))
        return True

    if text == BTN_FIND_ROLE:
        set_pending_action(user, PENDING_CREATE_ROLE_SEARCH)
        set_create_state(session, user, {"reply_scene": "create_role_search"})
        session.commit()
        await _render(
            update,
            "🔎 Поиск роли\n\nНапиши имя роли или часть имени. Например: Твайлайт, Спаркл, 8-Бит.",
            get_role_search_prompt_reply_keyboard(),
        )
        return True

    if text == BTN_RANDOM_ROLE:
        role = _resolve_role(topic, "random")
        return await _select_create_role_reply(update, session, user, topic, role, was_random=True)

    role = role_by_label(topic, text)
    if role is None:
        return False
    return await _select_create_role_reply(update, session, user, topic, role)


async def _select_create_role_reply(
    update: Update,
    session,
    user,
    topic: str | None,
    role: str | None,
    was_random: bool = False,
) -> bool:
    state = set_create_state(
        session,
        user,
        {"reply_scene": "create_max_players", "role": role},
    )
    clear_pending_action(user)
    set_pending_action(user, PENDING_CREATE_MAX_PLAYERS)
    session.commit()
    await _render(update, _render_create_max_players_prompt(topic), get_navigation_reply_keyboard())
    return True


async def _handle_create_role_search_result_reply(update: Update, session, user, state: dict, text: str) -> bool:
    if text == BTN_SEARCH_MORE:
        set_pending_action(user, PENDING_CREATE_ROLE_SEARCH)
        set_create_state(session, user, {"reply_scene": "create_role_search"})
        session.commit()
        await _render(update, "🔎 Поиск роли\n\nНапиши имя роли или часть имени.", get_role_search_prompt_reply_keyboard())
        return True

    topic = state.get("topic")
    role = role_by_label(topic, text)
    if role is None:
        return False
    return await _select_create_role_reply(update, session, user, topic, role)


async def _handle_join_role_reply(update: Update, session, user, state: dict, text: str) -> bool:
    code = state.get("code")
    topic = state.get("topic")
    page = int(state.get("page", 0) or 0)

    if text == "◀️":
        page = max(0, page - 1)
        set_create_state(session, user, {"reply_scene": "join_role", "page": page})
        session.commit()
        await _show_join_role_page(update, code, page)
        return True

    if text == "▶️":
        page += 1
        set_create_state(session, user, {"reply_scene": "join_role", "page": page})
        session.commit()
        await _show_join_role_page(update, code, page)
        return True

    if text == BTN_FIND_ROLE:
        set_pending_action(user, f"{PENDING_JOIN_ROLE_SEARCH_PREFIX}{code}")
        set_create_state(session, user, {"reply_scene": "join_role_search", "code": code, "topic": topic})
        session.commit()
        await _render(update, "🔎 Поиск роли\n\nНапиши имя роли или часть имени.", get_role_search_prompt_reply_keyboard())
        return True

    if text == BTN_RANDOM_FREE_ROLE:
        session.commit()
        await _join_lobby_from_reply(update, code, "random")
        return True

    role = role_by_label(topic, text)
    if role is None:
        return False
    session.commit()
    await _join_lobby_from_reply(update, code, role)
    return True


async def _handle_join_role_search_result_reply(update: Update, session, user, state: dict, text: str) -> bool:
    code = state.get("code")
    topic = state.get("topic")
    if text == BTN_SEARCH_MORE:
        set_pending_action(user, f"{PENDING_JOIN_ROLE_SEARCH_PREFIX}{code}")
        set_create_state(session, user, {"reply_scene": "join_role_search", "code": code, "topic": topic})
        session.commit()
        await _render(update, "🔎 Поиск роли\n\nНапиши имя роли или часть имени.", get_role_search_prompt_reply_keyboard())
        return True

    role = role_by_label(topic, text)
    if role is None:
        return False
    session.commit()
    await _join_lobby_from_reply(update, code, role)
    return True


async def _handle_waiting_lobby_reply(update: Update, session, user, state: dict, text: str) -> bool:
    code = state.get("code")
    if not code:
        return False
    if text == BTN_REFRESH:
        session.commit()
        await _show_lobby_waiting(update, code)
        return True
    if text == BTN_INVITE:
        session.commit()
        await _show_invite(update, code)
        return True
    if text == BTN_START:
        session.commit()
        await _start_lobby_from_reply(update, code)
        return True
    if text == BTN_CLOSE:
        session.commit()
        await _close_lobby_from_reply(update, code)
        return True
    if text == BTN_LEAVE:
        session.commit()
        await _leave_current_lobby(update)
        return True
    return False


async def _handle_active_lobby_reply(
    update: Update,
    session,
    user,
    state: dict,
    scene: str | None,
    text: str,
) -> bool:
    code = state.get("code")
    if not code and user.current_lobby_id is not None:
        lobby = lobby_repo.get_by_id(session, user.current_lobby_id)
        code = lobby.code if lobby is not None else None
    if not code:
        return False

    if text == BTN_MEMBERS:
        session.commit()
        await _show_lobby_members(update, code)
        return True
    if text == BTN_INFO:
        session.commit()
        await _show_lobby_info(update, code)
        return True
    if text == BTN_CLOSE:
        session.commit()
        await _close_lobby_from_reply(update, code)
        return True
    if text == BTN_LEAVE:
        session.commit()
        await _leave_current_lobby(update)
        return True
    if scene == "active_lobby":
        return False
    return False


async def _show_main_menu_and_remove_reply_keyboard(update: Update) -> None:
    await _render(update, "Главное меню", get_remove_lobby_reply_keyboard())
    await showMainMenu(update)


async def _render_topic_choice(update: Update, text: str) -> None:
    await _render(update, text, get_navigation_reply_keyboard())
    await _render(update, "Темы:", get_topic_inline_keyboard())


async def _render_role_choice(update: Update, text: str, inline_keyboard) -> None:
    await _render(update, text, get_navigation_reply_keyboard())
    await _render(update, "Роли:", inline_keyboard)


async def _delete_callback_message(update: Update) -> None:
    query = update.callback_query
    if query is None:
        return

    message = query.message
    if not hasattr(message, "delete"):
        return

    await delete_known_message(message)


def _callback_int(data: str, prefix: str) -> int:
    try:
        return int(data.removeprefix(prefix))
    except ValueError:
        return 0


def _render_create_max_players_prompt(topic: str | None) -> str:
    return (
        "👥 Размер лобби\n\n"
        f"Тема: {topic_name(topic)}\n\n"
        "Напиши максимум участников комнаты числом от 2 до 50."
    )


def _parse_max_players(text: str) -> int | None:
    try:
        value = int(text)
    except ValueError:
        return None
    if 2 <= value <= 50:
        return value
    return None


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
    application.add_handler(CommandHandler("leave", leave_command))
    application.add_handler(CallbackQueryHandler(lobby_callback_handler, pattern=r"^lobby:"))
    application.add_handler(
        MessageHandler(
            (filters.TEXT & ~filters.COMMAND) | filters.PHOTO | filters.Sticker.ALL | filters.VOICE,
            lobby_message_handler,
        )
    )
    job_queue = getattr(application, "_job_queue", None)
    if job_queue is not None:
        job_queue.run_repeating(close_expired_lobbies, interval=60, first=60)


async def leave_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return
    await _leave_current_lobby(update)


async def _leave_current_lobby(update: Update) -> None:
    with get_session() as session:
        try:
            user = _ensure_user(session, update)
            user_id = user.id
            lobby, closed, owner_changed = leave_lobby(session, user)
            lobby_id = lobby.id
            clear_pending_action(user)
            clear_create_state(user)
            set_create_state(session, user, {"reply_scene": "play_main"})
            session.commit()
        except LobbyError as exc:
            session.rollback()
            await _show_lobby_error(update, exc)
            return
        except Exception:
            session.rollback()
            logger.exception("Leave lobby failed")
            await _render(update, "Не удалось выйти из лобби.", get_play_main_reply_keyboard())
            return

    await showMainMenu(update)
    if closed:
        await notify_lobby_closed(update.get_bot(), lobby_id, "empty")
        return
    await notify_user_left(update.get_bot(), lobby_id, user_id)
    if owner_changed:
        await notify_owner_changed(update.get_bot(), lobby_id)


async def _show_play_main(update: Update) -> None:
    with get_session() as session:
        user = _ensure_user(session, update)
        clear_pending_action(user)
        clear_create_state(user)
        set_create_state(session, user, {"reply_scene": "play_main"})
        has_current_lobby = _has_current_open_lobby(session, user)
        session.commit()
    await _render(update, render_play_main(), get_play_main_reply_keyboard(has_current_lobby))


async def _show_find_main(update: Update) -> None:
    with get_session() as session:
        user = _ensure_user(session, update)
        clear_pending_action(user)
        clear_create_state(user)
        set_create_state(session, user, {"reply_scene": "find_topic"})
        session.commit()
    await _render_topic_choice(update, "🔎 Найти лобби\n\nВыбери тему:")


LOBBY_LIST_PAGE_SIZE = 8


async def _show_lobby_list(update: Update, topic: str | None, page: int = 0) -> None:
    with get_session() as session:
        user = _ensure_user(session, update)
        clear_pending_action(user)
        clear_create_state(user)
        set_create_state(session, user, {"reply_scene": "lobby_list", "topic": topic, "page": page})
        lobbies = lobby_repo.list_available_active(session, topic=topic, user_id=user.id)
        page_lobbies, safe_page, pages_count = _paginate_lobbies(lobbies, page)
        session.commit()

    if not lobbies:
        await _render(
            update,
            f"🔎 Найти лобби\n\nПо теме {topic_name(topic)} сейчас нет активных открытых лобби для входа.",
            get_play_main_reply_keyboard(),
        )
        return

    await _render(
        update,
        f"🔎 Найти лобби\n\nТема: {topic_name(topic)}\nВыбери активную комнату:",
        get_navigation_reply_keyboard(),
    )
    await _render(
        update,
        "Доступные лобби:",
        get_lobby_list_inline_keyboard(_lobby_list_buttons(page_lobbies), safe_page, pages_count),
    )


def _paginate_lobbies(lobbies: list, page: int):
    pages_count = max(1, (len(lobbies) + LOBBY_LIST_PAGE_SIZE - 1) // LOBBY_LIST_PAGE_SIZE)
    safe_page = min(max(0, page), pages_count - 1)
    start = safe_page * LOBBY_LIST_PAGE_SIZE
    return lobbies[start:start + LOBBY_LIST_PAGE_SIZE], safe_page, pages_count


def _lobby_list_buttons(lobbies: list) -> list[tuple[str, str]]:
    return [(lobby.code, _lobby_list_label(lobby)) for lobby in lobbies]


def _lobby_list_label(lobby) -> str:
    return (
        f"{topic_name(lobby.topic)} · "
        f"{lobby.players_count}/{lobby.max_players} · "
        f"{_lobby_duration_label(lobby)}"
    )


def _lobby_duration_label(lobby) -> str:
    started_at = lobby.activated_at or lobby.created_at
    if started_at is None:
        return "только началось"
    minutes = max(0, int((datetime.utcnow() - started_at).total_seconds() // 60))
    if minutes < 1:
        return "меньше минуты"
    if minutes < 60:
        return f"{minutes} мин"
    hours = minutes // 60
    rest = minutes % 60
    if rest:
        return f"{hours} ч {rest} мин"
    return f"{hours} ч"


async def _show_create_privacy(update: Update) -> None:
    with get_session() as session:
        user = _ensure_user(session, update)
        clear_pending_action(user)
        clear_create_state(user)
        set_create_state(session, user, {"reply_scene": "create_privacy", "mode": "rp"})
        session.commit()
    await _render(update, "➕ Создание лобби\n\nВыбери тип лобби:", get_create_privacy_reply_keyboard())


async def _show_create_topic(update: Update) -> None:
    with get_session() as session:
        user = _ensure_user(session, update)
        clear_pending_action(user)
        set_create_state(session, user, {"reply_scene": "create_topic"})
        session.commit()
    await _render_topic_choice(update, render_create_topic())


async def _set_pending_code_action(update: Update) -> None:
    with get_session() as session:
        user = _ensure_user(session, update)
        set_pending_action(user, PENDING_ENTER_LOBBY_CODE)
        set_create_state(session, user, {"reply_scene": "code_entry"})
        session.commit()
    await _render(
        update,
        "🔑 Вход по коду\n\nОтправь код лобби следующим сообщением.",
        get_code_entry_reply_keyboard(),
    )


async def _confirm_create_lobby(update: Update, bot) -> None:
    with get_session() as session:
        try:
            user = _ensure_user(session, update)
            state = get_create_state(user)
            _validate_create_state(state)
            lobby = create_lobby(session, user, state)
            clear_create_state(user)
            set_create_state(
                session,
                user,
                {"reply_scene": "active_lobby", "code": lobby.code},
            )
            session.commit()
        except LobbyError as exc:
            session.rollback()
            if exc.code == "not_enough_players":
                await _show_lobby_action_error(update, code, exc.message)
                return
            await _show_lobby_error(update, exc)
            return
        except Exception:
            session.rollback()
            logger.exception("Create lobby failed")
            await _render(update, "Не удалось создать лобби.", get_play_main_reply_keyboard())
            return
    await _render(update, render_active_lobby_started(lobby), get_active_lobby_reply_keyboard(True))


async def _join_lobby_from_reply(update: Update, code: str, role: str | None = None) -> None:
    was_random = role == "random"
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
                set_create_state(
                    session,
                    user,
                    {
                        "reply_scene": "join_role",
                        "code": lobby.code,
                        "topic": lobby.topic,
                        "page": 0,
                    },
                )
                session.commit()
                await _render(
                    update,
                    render_join_role(lobby),
                    get_navigation_reply_keyboard(),
                )
                await _render(
                    update,
                    "Роли:",
                    get_join_role_inline_keyboard(lobby.code, lobby.topic, taken_roles),
                )
                return
            if role == "random":
                taken_roles = lobby_member_repo.list_taken_roles(session, lobby.id)
                role = _resolve_random_free_role(lobby.topic, taken_roles)
            lobby = join_lobby(session, user, code, role=role)
            clear_pending_action(user)
            is_active = lobby.status == "active"
            set_create_state(
                session,
                user,
                {
                    "reply_scene": "active_lobby" if is_active else "waiting_lobby",
                    "code": lobby.code,
                },
            )
            session.commit()
        except LobbyError as exc:
            session.rollback()
            await _show_lobby_error(update, exc)
            return
        except Exception:
            session.rollback()
            logger.exception("Join lobby failed")
            await _render(update, "Не удалось войти в лобби.", get_play_main_reply_keyboard())
            return

    await _answer_role_selected(update, lobby.topic, role, was_random)
    await notify_user_joined(update.get_bot(), lobby.id, user.id)
    if is_active:
        await _render(update, render_active_lobby_started(lobby), get_active_lobby_reply_keyboard(lobby.owner_id == user.id))
        return
    await _show_lobby_waiting(update, lobby.code)


async def _start_lobby_from_reply(update: Update, code: str) -> None:
    with get_session() as session:
        try:
            user = _ensure_user(session, update)
            lobby = start_lobby(session, user, code)
            set_create_state(session, user, {"reply_scene": "active_lobby", "code": lobby.code})
            session.commit()
        except LobbyError as exc:
            session.rollback()
            await _show_lobby_error(update, exc)
            return
        except Exception:
            session.rollback()
            logger.exception("Start lobby failed")
            await _render(update, "Не удалось запустить лобби.", get_play_main_reply_keyboard())
            return
    await notify_lobby_started(update.get_bot(), lobby.id, exclude_user_id=user.id)
    await _render(update, render_active_lobby_started(lobby), get_active_lobby_reply_keyboard(True))


async def _show_lobby_action_error(update: Update, code: str | None, message: str) -> None:
    if not code:
        await _render(update, message, get_play_main_reply_keyboard())
        return

    with get_session() as session:
        user = _ensure_user(session, update)
        lobby = lobby_repo.get_by_code(session, code)
        if lobby is None:
            await _render(update, message, get_play_main_reply_keyboard())
            return
        member = lobby_member_repo.get_joined_member(session, lobby.id, user.id)
        if member is None:
            await _render(update, message, get_play_main_reply_keyboard())
            return
        set_create_state(
            session,
            user,
            {
                "reply_scene": "active_lobby" if lobby.status == "active" else "waiting_lobby",
                "code": lobby.code,
            },
        )
        keyboard = (
            get_active_lobby_reply_keyboard(member.is_owner)
            if lobby.status == "active"
            else get_lobby_waiting_reply_keyboard(member.is_owner)
        )
        text = render_active_lobby_started(lobby) if lobby.status == "active" else render_lobby_waiting(lobby)
        session.commit()

    await _render(update, f"{message}\n\n{text}", keyboard)


async def _close_lobby_from_reply(update: Update, code: str) -> None:
    with get_session() as session:
        try:
            user = _ensure_user(session, update)
            lobby = lobby_repo.get_by_code(session, code)
            if lobby is None:
                raise LobbyError("not_found", "Лобби не найдено.")
            if lobby.owner_id != user.id:
                raise LobbyError("not_owner", "Закрыть лобби может только владелец.")
            lobby_id = lobby.id
            closer_user_id = user.id
            close_lobby(session, lobby.id, "manual")
            clear_create_state(user)
            set_create_state(session, user, {"reply_scene": "play_main"})
            session.commit()
        except LobbyError as exc:
            session.rollback()
            await _show_lobby_error(update, exc)
            return
        except Exception:
            session.rollback()
            logger.exception("Close lobby failed")
            await _render(update, "Не удалось закрыть лобби.", get_play_main_reply_keyboard())
            return

    await showMainMenu(update)
    await notify_lobby_closed(update.get_bot(), lobby_id, "manual", exclude_user_id=closer_user_id)


async def _show_lobby_waiting(update: Update, code: str) -> None:
    with get_session() as session:
        user = _ensure_user(session, update)
        lobby = lobby_repo.get_by_code(session, code)
        if lobby is None:
            await _render(update, "Это лобби уже закрыто.", get_play_main_reply_keyboard())
            return
        member = lobby_member_repo.get_joined_member(session, lobby.id, user.id)
        if member is None:
            await _render(update, "Это действие больше недоступно. Открой актуальное меню.", get_play_main_reply_keyboard())
            return
        keyboard = (
            get_active_lobby_reply_keyboard(member.is_owner)
            if lobby.status == "active"
            else get_lobby_waiting_reply_keyboard(member.is_owner)
        )
        set_create_state(
            session,
            user,
            {
                "reply_scene": "active_lobby" if lobby.status == "active" else "waiting_lobby",
                "code": lobby.code,
            },
        )
        session.commit()
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
            set_create_state(
                session,
                user,
                {
                    "reply_scene": "join_role",
                    "code": lobby.code,
                    "topic": lobby.topic,
                    "page": page,
                },
            )
            session.commit()
        except LobbyError as exc:
            session.rollback()
            await _show_lobby_error(update, exc)
            return

    await _render(
        update,
        render_join_role(lobby),
        get_navigation_reply_keyboard(),
    )
    await _render(
        update,
        "Роли:",
        get_join_role_inline_keyboard(lobby.code, lobby.topic, taken_roles, page),
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
            set_create_state(
                session,
                user,
                {
                    "reply_scene": "join_role_search",
                    "code": lobby.code,
                    "topic": lobby.topic,
                },
            )
            session.commit()
        except LobbyError as exc:
            session.rollback()
            await _show_lobby_error(update, exc)
            return

    await _render(
        update,
        "🔎 Поиск роли\n\nНапиши имя роли или часть имени.",
        get_role_search_prompt_reply_keyboard(),
    )


async def _show_invite(update: Update, code: str) -> None:
    with get_session() as session:
        lobby = lobby_repo.get_by_code(session, code)
        if lobby is None:
            await _render(update, "Действие недоступно.", get_play_main_reply_keyboard())
            return
        if lobby.privacy == "private":
            text = f"📨 Приглашение\n\nКод приватного лобби: {lobby.code}"
        else:
            text = f"📨 Это открытое лобби доступно через поиск.\n\nКод лобби: {lobby.code}"
    await _render(update, text, get_lobby_waiting_reply_keyboard(True))


async def _show_lobby_info(update: Update, code: str) -> None:
    with get_session() as session:
        user = _ensure_user(session, update)
        lobby = lobby_repo.get_by_code(session, code)
        if lobby is None:
            await _render(update, "Действие недоступно.", get_play_main_reply_keyboard())
            return
        member = lobby_member_repo.get_joined_member(session, lobby.id, user.id)
        is_owner = bool(member and member.is_owner)
        set_create_state(session, user, {"reply_scene": "lobby_info", "code": lobby.code})
        session.commit()
    await _render(update, render_lobby_info(lobby), get_lobby_info_reply_keyboard(is_owner))


async def _show_current_lobby(update: Update) -> None:
    with get_session() as session:
        user = _ensure_user(session, update)
        lobby = lobby_repo.get_current_for_user(session, user)
        if lobby is None or lobby.status == "closed":
            if lobby is not None:
                user.current_lobby_id = None
            clear_pending_action(user)
            clear_create_state(user)
            set_create_state(session, user, {"reply_scene": "play_main"})
            session.commit()
            await _render(update, "Ты сейчас не находишься в активном лобби.", get_play_main_reply_keyboard())
            return

        member = lobby_member_repo.get_joined_member(session, lobby.id, user.id)
        if member is None:
            user.current_lobby_id = None
            clear_pending_action(user)
            clear_create_state(user)
            set_create_state(session, user, {"reply_scene": "play_main"})
            session.commit()
            await _render(update, "Ты сейчас не находишься в активном лобби.", get_play_main_reply_keyboard())
            return

        code = lobby.code
        session.commit()

    await _show_lobby_waiting(update, code)


def _has_current_open_lobby(session, user) -> bool:
    if user.current_lobby_id is None:
        return False

    lobby = lobby_repo.get_by_id(session, user.current_lobby_id)
    if lobby is None or lobby.status == "closed":
        return False

    member = lobby_member_repo.get_joined_member(session, lobby.id, user.id)
    return member is not None


async def _show_lobby_members(update: Update, code: str) -> None:
    with get_session() as session:
        user = _ensure_user(session, update)
        lobby = lobby_repo.get_by_code(session, code)
        if lobby is None:
            await _render(update, "Действие недоступно.", get_play_main_reply_keyboard())
            return
        set_create_state(session, user, {"reply_scene": "lobby_members", "code": lobby.code})
        session.commit()
        members = lobby_member_repo.list_joined_users(session, lobby.id)
        lines = ["👥 Участники лобби\n"]
        for index, (member, user) in enumerate(members, start=1):
            crown = " 👑" if member.is_owner else ""
            name = role_name(lobby.topic, member.role) if lobby.mode == "rp" else format_display_name(user)
            lines.append(f"{index}. {name}{crown}")
    await _render(update, "\n".join(lines), get_lobby_members_reply_keyboard())


async def _show_found_lobby(update: Update, topic: str) -> None:
    with get_session() as session:
        user = _ensure_user(session, update)
        lobby = find_available_lobby(session, topic, user_id=user.id)
    if lobby is None:
        with get_session() as session:
            user = _ensure_user(session, update)
            set_create_state(session, user, {"reply_scene": "no_lobby", "topic": topic})
            session.commit()
        await _render(update, render_no_lobby(topic), get_no_lobby_reply_keyboard())
        return
    with get_session() as session:
        user = _ensure_user(session, update)
        set_create_state(
            session,
            user,
            {"reply_scene": "found_lobby", "topic": topic, "code": lobby.code},
        )
        session.commit()
    await _render(update, render_found_lobby(lobby), get_found_lobby_reply_keyboard())


async def _show_next_lobby(update: Update, topic: str, current_code: str) -> None:
    with get_session() as session:
        user = _ensure_user(session, update)
        lobby = find_next_lobby(session, topic, current_code, user_id=user.id)
    if lobby is None:
        with get_session() as session:
            user = _ensure_user(session, update)
            set_create_state(session, user, {"reply_scene": "no_lobby", "topic": topic})
            session.commit()
        await _render(update, render_no_lobby(topic), get_no_lobby_reply_keyboard())
        return
    with get_session() as session:
        user = _ensure_user(session, update)
        set_create_state(
            session,
            user,
            {"reply_scene": "found_lobby", "topic": topic, "code": lobby.code},
        )
        session.commit()
    await _render(update, render_found_lobby(lobby), get_found_lobby_reply_keyboard())


async def _handle_create_role_search_message(update: Update, session, user) -> None:
    query = (update.message.text or "").strip()
    state = get_create_state(user)
    topic = state.get("topic")
    results = search_roles(topic, query)
    clear_pending_action(user)
    set_create_state(session, user, {"reply_scene": "create_role_search_results"})
    session.commit()

    if not results:
        set_pending_action(user, PENDING_CREATE_ROLE_SEARCH)
        set_create_state(session, user, {"reply_scene": "create_role_search"})
        session.commit()
        await reply_text(
            update.message,
            "Роль не найдена. Напиши другое имя или часть имени.",
            reply_markup=get_role_search_prompt_reply_keyboard(),
        )
        return

    await reply_text(
        update.message,
        "Нашёл роли. Выбери нужную:",
        reply_markup=get_navigation_reply_keyboard(),
    )
    await _render(update, "Роли:", get_create_role_search_results_inline_keyboard(results))


async def _handle_create_max_players_message(update: Update, session, user) -> None:
    max_players = _parse_max_players(update.message.text or "")
    state = get_create_state(user)
    topic = state.get("topic")
    if max_players is None:
        set_pending_action(user, PENDING_CREATE_MAX_PLAYERS)
        set_create_state(session, user, {"reply_scene": "create_max_players"})
        session.commit()
        await reply_text(
            update.message,
            "Напиши число участников от 2 до 50.",
            reply_markup=get_navigation_reply_keyboard(),
        )
        return

    state = set_create_state(
        session,
        user,
        {"reply_scene": "create_confirm", "max_players": max_players},
    )
    clear_pending_action(user)
    session.commit()
    await reply_text(
        update.message,
        render_create_confirm(state),
        reply_markup=get_create_confirm_reply_keyboard(),
    )


async def _handle_display_name_message(update: Update, session, user) -> None:
    if update.message.text is None:
        await reply_text(update.message, "Напиши имя текстом.")
        session.commit()
        return

    try:
        set_display_name(session, user, update.message.text)
        clear_pending_action(user)
        session.commit()
    except DisplayNameError as exc:
        session.commit()
        await reply_text(update.message, f"{exc.message}\n\nПопробуй ещё раз.")
        return

    await reply_text(update.message, f"Готово, теперь твоё имя: {user.display_name}.")
    await showMainMenu(update)


async def _handle_join_role_search_message(update: Update, session, user) -> None:
    query = (update.message.text or "").strip()
    code = user.pending_action.removeprefix(PENDING_JOIN_ROLE_SEARCH_PREFIX)
    lobby = lobby_repo.get_by_code(session, code)
    if lobby is None:
        clear_pending_action(user)
        session.commit()
        await reply_text(update.message, "Лобби не найдено.", reply_markup=get_play_main_reply_keyboard())
        return

    try:
        _validate_lobby_joinable_for_role_selection(lobby)
    except LobbyError as exc:
        clear_pending_action(user)
        session.commit()
        await reply_text(update.message, exc.message, reply_markup=get_play_main_reply_keyboard())
        return

    taken_roles = lobby_member_repo.list_taken_roles(session, lobby.id)
    results = search_roles(lobby.topic, query, taken_roles)
    clear_pending_action(user)
    set_create_state(
        session,
        user,
        {
            "reply_scene": "join_role_search_results",
            "code": lobby.code,
            "topic": lobby.topic,
        },
    )
    session.commit()

    if not results:
        set_pending_action(user, f"{PENDING_JOIN_ROLE_SEARCH_PREFIX}{code}")
        set_create_state(
            session,
            user,
            {
                "reply_scene": "join_role_search",
                "code": lobby.code,
                "topic": lobby.topic,
            },
        )
        session.commit()
        await reply_text(
            update.message,
            "Роль не найдена или уже занята. Напиши другое имя или часть имени.",
            reply_markup=get_role_search_prompt_reply_keyboard(),
        )
        return

    await reply_text(
        update.message,
        "Нашёл свободные роли. Выбери нужную:",
        reply_markup=get_navigation_reply_keyboard(),
    )
    await _render(update, "Роли:", get_join_role_search_results_inline_keyboard(results))


async def _show_lobby_error(update: Update, exc: LobbyError) -> None:
    if exc.code == "already_in_lobby":
        await _render(update, "Ты уже находишься в лобби.", get_already_in_lobby_reply_keyboard())
    elif exc.code == "full":
        await _render(update, "Это лобби уже заполнено.", get_lobby_full_reply_keyboard())
    elif exc.code == "closed":
        await _render(update, "Это лобби уже закрыто.", get_play_main_reply_keyboard())
    else:
        await _render(update, exc.message, get_play_main_reply_keyboard())


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


async def _answer_role_selected(
    update: Update,
    topic: str | None,
    role: str | None,
    was_random: bool = False,
) -> None:
    if not role:
        return

    text = (
        f"🎲 Тебе досталась роль: {role_name(topic, role)}"
        if was_random
        else f"🎭 Ты выбрал роль: {role_name(topic, role)}"
    )

    if update.effective_chat is not None:
        sent_message = await update.get_bot().send_message(
            chat_id=update.effective_chat.id,
            text=text,
        )
        remember_telegram_message(sent_message)
        return

    if update.message is not None:
        await reply_text(update.message, text)


def _validate_lobby_joinable_for_role_selection(lobby) -> None:
    if lobby.status == "closed":
        raise LobbyError("closed", "Это лобби уже закрыто.")
    if lobby.status not in {"waiting", "active"}:
        raise LobbyError("not_waiting", "Это лобби недоступно для входа.")
    if lobby.players_count >= lobby.max_players:
        raise LobbyError("full", "Это лобби уже заполнено.")


def _validate_create_state(state: dict) -> None:
    state.setdefault("mode", "rp")
    state.setdefault("max_players", 15)
    required = {"topic", "privacy"}
    if not required.issubset(state):
        raise LobbyError("invalid_state", "Настройки лобби неполные. Начни создание заново.")
