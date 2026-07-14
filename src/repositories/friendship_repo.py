"""SQL-операции для связей друзей."""

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from src.models.friendship import Friendship


def get_between_users(session: Session, user_id: int, other_user_id: int) -> Friendship | None:
    stmt = select(Friendship).where(
        or_(
            (Friendship.requester_id == user_id) & (Friendship.addressee_id == other_user_id),
            (Friendship.requester_id == other_user_id) & (Friendship.addressee_id == user_id),
        )
    )
    return session.scalar(stmt)


def create_request(session: Session, requester_id: int, addressee_id: int) -> Friendship:
    friendship = Friendship(
        requester_id=requester_id,
        addressee_id=addressee_id,
        status="pending",
    )
    session.add(friendship)
    return friendship
