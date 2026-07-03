"""Бизнес-логика лобби."""

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from src.core.logger import logger
from src.models.lobby import Lobby
from src.models.user import User
from src.repositories import lobby_member_repo, lobby_repo
from src.constants.roles import ROLES_BY_TOPIC
from src.utils.invite_code import generate_lobby_code

WAITING_TTL = timedelta(minutes=30)
ACTIVE_TTL = timedelta(hours=2)


class LobbyError(Exception):
    """Понятная бизнес-ошибка lobby-сценария."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def create_lobby(session: Session, user: User, payload: dict) -> Lobby:
    if user.current_lobby_id is not None:
        raise LobbyError("already_in_lobby", "Ты уже находишься в лобби.")

    if payload["mode"] == "rp":
        _validate_rp_role(lobby=None, topic=payload["topic"], role=payload.get("role"))
        if int(payload["max_players"]) > len(ROLES_BY_TOPIC.get(payload["topic"], {})):
            raise LobbyError("too_many_players", "Для этой темы недостаточно уникальных ролей.")

    code = _generate_unique_code(session)
    now = datetime.utcnow()
    lobby = lobby_repo.create(
        session,
        code=code,
        topic=payload["topic"],
        mode=payload["mode"],
        owner_id=user.id,
        max_players=int(payload["max_players"]),
        players_count=1,
        privacy=payload["privacy"],
        status="waiting",
        created_at=now,
        updated_at=now,
        expires_at=now + WAITING_TTL,
    )
    lobby_member_repo.create_member(
        session,
        lobby_id=lobby.id,
        user_id=user.id,
        role=payload.get("role"),
        is_owner=True,
        status="joined",
        joined_at=now,
    )
    user.current_lobby_id = lobby.id
    return lobby


def join_lobby(
    session: Session,
    user: User,
    code: str,
    role: str | None = None,
) -> Lobby:
    if user.current_lobby_id is not None:
        raise LobbyError("already_in_lobby", "Ты уже находишься в лобби.")

    lobby = lobby_repo.get_by_code(session, code)
    if lobby is None:
        raise LobbyError("not_found", "Лобби с таким кодом не найдено.")
    if lobby.status == "closed":
        raise LobbyError("closed", "Это лобби уже закрыто.")
    if lobby.status != "waiting":
        raise LobbyError("not_waiting", "Это лобби уже не ожидает участников.")
    if lobby.players_count >= lobby.max_players:
        raise LobbyError("full", "Это лобби уже заполнено.")
    if lobby.mode == "rp":
        _validate_rp_role(lobby=lobby, topic=lobby.topic, role=role)
        if lobby_member_repo.is_role_taken(session, lobby.id, role):
            raise LobbyError("role_taken", "Эта роль уже занята. Выбери другую.")

    now = datetime.utcnow()
    member = lobby_member_repo.get_member(session, lobby.id, user.id)
    if member is None:
        lobby_member_repo.create_member(
            session,
            lobby_id=lobby.id,
            user_id=user.id,
            role=role,
            is_owner=False,
            status="joined",
            joined_at=now,
        )
    else:
        member.role = role
        member.is_owner = False
        member.status = "joined"
        member.joined_at = now
        member.left_at = None

    lobby.players_count = min(lobby.max_players, lobby.players_count + 1)
    user.current_lobby_id = lobby.id
    return lobby


def leave_lobby(session: Session, user: User, code: str | None = None) -> tuple[Lobby, bool, bool]:
    lobby = _resolve_lobby_for_user(session, user, code)
    member = lobby_member_repo.get_joined_member(session, lobby.id, user.id)
    if member is None:
        raise LobbyError("not_member", "Ты не состоишь в этом лобби.")

    was_owner = member.is_owner
    now = datetime.utcnow()
    member.status = "left"
    member.left_at = now
    member.is_owner = False
    user.current_lobby_id = None
    lobby.players_count = max(0, lobby.players_count - 1)

    owner_changed = False
    if was_owner and lobby.players_count > 0:
        new_owner = lobby_member_repo.first_non_owner_joined(session, lobby.id, user.id)
        if new_owner is not None:
            new_owner.is_owner = True
            lobby.owner_id = new_owner.user_id
            owner_changed = True

    closed = False
    if lobby.players_count == 0:
        _close_lobby_in_session(session, lobby, "empty")
        closed = True

    return lobby, closed, owner_changed


def start_lobby(session: Session, user: User, code: str, force: bool = False) -> Lobby:
    lobby = lobby_repo.get_by_code(session, code)
    if lobby is None:
        raise LobbyError("not_found", "Лобби с таким кодом не найдено.")
    if lobby.status == "closed":
        raise LobbyError("closed", "Это лобби уже закрыто.")
    if lobby.status == "active":
        return lobby
    if lobby.owner_id != user.id and not force:
        raise LobbyError("not_owner", "Запустить лобби может только владелец.")
    if lobby.players_count < 2 and not force:
        raise LobbyError("not_enough_players", "Для запуска нужно минимум 2 участника.")

    now = datetime.utcnow()
    lobby.status = "active"
    lobby.activated_at = now
    lobby.expires_at = now + ACTIVE_TTL
    return lobby


def close_lobby(session: Session, lobby_id: int, reason: str) -> Lobby:
    lobby = lobby_repo.get_by_id(session, lobby_id)
    if lobby is None:
        raise LobbyError("not_found", "Лобби не найдено.")
    _close_lobby_in_session(session, lobby, reason)
    return lobby


def get_lobby_by_code(session: Session, code: str) -> Lobby | None:
    return lobby_repo.get_by_code(session, code)


def get_current_lobby(session: Session, user: User) -> Lobby | None:
    return lobby_repo.get_current_for_user(session, user)


def render_lobby_status(lobby: Lobby) -> str:
    return f"{lobby.players_count}/{lobby.max_players}"


def _generate_unique_code(session: Session) -> str:
    for _ in range(20):
        code = generate_lobby_code()
        if lobby_repo.get_by_code(session, code) is None:
            return code
    logger.error("Could not generate unique lobby code")
    raise LobbyError("code_generation_failed", "Не удалось создать код лобби.")


def _validate_rp_role(lobby: Lobby | None, topic: str, role: str | None) -> None:
    if not role:
        raise LobbyError("role_required", "Для ролевой игры нужно выбрать роль.")
    if role not in ROLES_BY_TOPIC.get(topic, {}):
        raise LobbyError("invalid_role", "Такой роли нет для этой темы.")


def _resolve_lobby_for_user(session: Session, user: User, code: str | None) -> Lobby:
    lobby = lobby_repo.get_by_code(session, code) if code else get_current_lobby(session, user)
    if lobby is None:
        raise LobbyError("not_found", "Лобби не найдено.")
    if user.current_lobby_id != lobby.id:
        raise LobbyError("not_member", "Ты не состоишь в этом лобби.")
    return lobby


def _close_lobby_in_session(session: Session, lobby: Lobby, reason: str) -> None:
    now = datetime.utcnow()
    lobby.status = "closed"
    lobby.closed_at = now
    for _member, joined_user in lobby_member_repo.list_joined_users(session, lobby.id):
        joined_user.current_lobby_id = None
