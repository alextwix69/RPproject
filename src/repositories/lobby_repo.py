"""Репозиторий лобби."""

from datetime import datetime

from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from src.models.lobby import Lobby, LobbyMember
from src.models.user import User


def get_by_code(session: Session, code: str) -> Lobby | None:
    return session.scalar(select(Lobby).where(Lobby.code == code.upper()))


def get_by_id(session: Session, lobby_id: int) -> Lobby | None:
    return session.scalar(select(Lobby).where(Lobby.id == lobby_id))


def create(session: Session, **values) -> Lobby:
    lobby = Lobby(**values)
    session.add(lobby)
    session.flush()
    return lobby


def find_available(
    session: Session,
    topic: str,
    skip_code: str | None = None,
    user_id: int | None = None,
) -> Lobby | None:
    stmt = (
        select(Lobby)
        .where(
            Lobby.topic == topic,
            Lobby.privacy == "public",
            Lobby.status == "waiting",
            Lobby.players_count < Lobby.max_players,
        )
        .order_by(Lobby.created_at.asc(), Lobby.id.asc())
    )

    if skip_code:
        stmt = stmt.where(Lobby.code != skip_code.upper())

    if user_id is not None:
        stmt = stmt.where(
            ~exists().where(
                LobbyMember.lobby_id == Lobby.id,
                LobbyMember.user_id == user_id,
                LobbyMember.status == "joined",
            )
        )

    return session.scalar(stmt)


def list_expired(session: Session, now: datetime) -> list[Lobby]:
    stmt = select(Lobby).where(
        Lobby.status.in_(("waiting", "active")),
        Lobby.expires_at < now,
    )
    return list(session.scalars(stmt).all())


def get_current_for_user(session: Session, user: User) -> Lobby | None:
    if user.current_lobby_id is None:
        return None
    return get_by_id(session, user.current_lobby_id)
