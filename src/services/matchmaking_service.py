"""Поиск и быстрый вход в открытые лобби."""

from sqlalchemy.orm import Session

from src.models.lobby import Lobby
from src.models.user import User
from src.repositories import lobby_repo
from src.services.lobby_service import join_lobby


def find_available_lobby(
    session: Session,
    topic: str,
    skip_code: str | None = None,
    user_id: int | None = None,
) -> Lobby | None:
    return lobby_repo.find_available(session, topic, skip_code=skip_code, user_id=user_id)


def find_next_lobby(
    session: Session,
    topic: str,
    current_code: str,
    user_id: int | None = None,
) -> Lobby | None:
    return find_available_lobby(session, topic, skip_code=current_code, user_id=user_id)


def quick_join(session: Session, user: User, topic: str) -> Lobby | None:
    lobby = find_available_lobby(session, topic, user_id=user.id)
    if lobby is None:
        return None
    return join_lobby(session, user, lobby.code)
