"""Временные состояния пользователя для lobby-сценариев."""

from sqlalchemy.orm import Session

from src.models.user import User

GENERAL_MENU_SCENES = {
    "shop",
    "shop_premium",
    "settings",
    "settings_profile",
    "support",
    "support_faq",
    "support_faq_answer",
    "friends",
    "friend_found",
    "friend_profile",
}


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


def is_general_menu_scene(scene: str | None) -> bool:
    return scene in GENERAL_MENU_SCENES
