"""Профили пользователей и действия друзей."""

from datetime import datetime

from src.models.user import User
from src.repositories import friendship_repo
from src.repositories.user_repo import find_by_nickname


class FriendActionError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def set_avatar_file_id(user: User, file_id: str) -> User:
    user.avatar_file_id = file_id
    return user


def find_user_for_friend_search(session, current_user: User, query: str) -> User | None:
    found_user = find_by_nickname(session, query)
    if found_user is None or found_user.id == current_user.id:
        return None
    return found_user


def add_friend(session, requester: User, addressee: User):
    if requester.id == addressee.id:
        raise FriendActionError("self", "🪞 Нельзя отправить приглашение самому себе. Найди другого героя ✨")

    existing = friendship_repo.get_between_users(session, requester.id, addressee.id)
    if existing is not None:
        if existing.status == "pending":
            raise FriendActionError("pending", "💌 Приглашение этому герою уже отправлено. Осталось дождаться ответа ✨")
        raise FriendActionError("exists", "🤝 Этот герой уже среди твоих друзей 🌟")

    return friendship_repo.create_request(session, requester.id, addressee.id)


def format_last_online(value: datetime | None) -> str:
    if value is None:
        return "скрыто туманом ✨"
    return value.strftime("%d.%m.%Y %H:%M")


def render_profile_text(user: User, is_self: bool = False) -> str:
    title = "👑✨ Твой профиль героя" if is_self else "👤✨ Профиль героя"
    display_name = user.display_name or "имя ещё не выбрано"
    username = f"@{user.username}" if user.username else "-"
    avatar = "сияет в профиле ✨" if user.avatar_file_id else "ещё не выбран"

    return (
        f"{title}\n\n"
        f"🌟 Имя: {display_name}\n"
        f"💌 Telegram: {username}\n"
        f"🖼 Портрет: {avatar}\n"
        f"🕰 Последний визит: {format_last_online(user.last_seen_at)}"
    )
