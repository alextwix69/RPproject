"""Временные состояния пользователя для lobby-сценариев."""

from sqlalchemy.orm import Session

from src.models.user import User


def set_create_state(session: Session, user: User, patch: dict) -> dict:
    state = dict(user.create_state or {})
    state.update(patch)
    user.create_state = state
    return state


def get_create_state(user: User) -> dict:
    return dict(user.create_state or {})


def clear_create_state(user: User) -> None:
    user.create_state = None


def set_pending_action(user: User, action: str) -> None:
    user.pending_action = action


def get_pending_action(user: User) -> str | None:
    return user.pending_action


def clear_pending_action(user: User) -> None:
    user.pending_action = None
