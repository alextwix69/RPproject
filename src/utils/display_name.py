"""Отображаемые имена участников."""

from src.models.user import User


def format_display_name(user: User | None) -> str:
    if user is None:
        return "Участник"
    if user.username:
        return f"@{user.username}"
    if user.first_name:
        return user.first_name
    return "Участник"
