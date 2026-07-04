"""Админские права и управление ролями."""

from src.core.config import get_owner_ids
from src.core.database import get_session
from src.models.user import User
from src.repositories.user_repo import get_by_telegram_id, set_role_by_telegram_id


def is_owner_telegram_id(telegram_id: int | None) -> bool:
    """Проверяет владельца по OWNER_IDS из .env."""

    return telegram_id is not None and telegram_id in get_owner_ids()


def is_owner_effective_user(effective_user) -> bool:
    if effective_user is None:
        return False
    return is_owner_telegram_id(effective_user.id)


def is_admin_telegram_id(telegram_id: int | None) -> bool:
    """Проверяет админские права только по роли пользователя в БД."""

    if telegram_id is None:
        return False

    with get_session() as session:
        user = get_by_telegram_id(session, telegram_id)
        return bool(user is not None and user.role == "admin")


def is_admin_effective_user(effective_user) -> bool:
    if effective_user is None:
        return False
    return is_admin_telegram_id(effective_user.id)


def grant_admin_role(telegram_id: int) -> User | None:
    with get_session() as session:
        user = set_role_by_telegram_id(session, telegram_id, "admin")
        session.commit()
        return user


def revoke_admin_role(telegram_id: int) -> User | None:
    with get_session() as session:
        user = set_role_by_telegram_id(session, telegram_id, "user")
        session.commit()
        return user
