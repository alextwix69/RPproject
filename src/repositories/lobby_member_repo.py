"""Репозиторий участников лобби."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.lobby import LobbyMember
from src.models.user import User


def get_member(session: Session, lobby_id: int, user_id: int) -> LobbyMember | None:
    return session.scalar(
        select(LobbyMember).where(
            LobbyMember.lobby_id == lobby_id,
            LobbyMember.user_id == user_id,
        )
    )


def get_joined_member(
    session: Session,
    lobby_id: int,
    user_id: int,
) -> LobbyMember | None:
    return session.scalar(
        select(LobbyMember).where(
            LobbyMember.lobby_id == lobby_id,
            LobbyMember.user_id == user_id,
            LobbyMember.status == "joined",
        )
    )


def list_joined(session: Session, lobby_id: int) -> list[LobbyMember]:
    stmt = (
        select(LobbyMember)
        .where(LobbyMember.lobby_id == lobby_id, LobbyMember.status == "joined")
        .order_by(LobbyMember.is_owner.desc(), LobbyMember.joined_at.asc(), LobbyMember.id.asc())
    )
    return list(session.scalars(stmt).all())


def list_joined_users(session: Session, lobby_id: int) -> list[tuple[LobbyMember, User]]:
    stmt = (
        select(LobbyMember, User)
        .join(User, User.id == LobbyMember.user_id)
        .where(LobbyMember.lobby_id == lobby_id, LobbyMember.status == "joined")
        .order_by(LobbyMember.is_owner.desc(), LobbyMember.joined_at.asc(), LobbyMember.id.asc())
    )
    return list(session.execute(stmt).all())


def create_member(session: Session, **values) -> LobbyMember:
    member = LobbyMember(**values)
    session.add(member)
    session.flush()
    return member


def first_non_owner_joined(session: Session, lobby_id: int, old_owner_id: int) -> LobbyMember | None:
    return session.scalar(
        select(LobbyMember)
        .where(
            LobbyMember.lobby_id == lobby_id,
            LobbyMember.status == "joined",
            LobbyMember.user_id != old_owner_id,
        )
        .order_by(LobbyMember.joined_at.asc(), LobbyMember.id.asc())
    )
