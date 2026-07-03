"""Репозиторий сообщений лобби."""

from sqlalchemy.orm import Session

from src.models.lobby import LobbyMessage


def create_message(
    session: Session,
    lobby_id: int,
    sender_id: int,
    message_type: str,
    text: str | None = None,
    file_id: str | None = None,
) -> LobbyMessage:
    message = LobbyMessage(
        lobby_id=lobby_id,
        sender_id=sender_id,
        message_type=message_type,
        text=text,
        file_id=file_id,
    )
    session.add(message)
    session.flush()
    return message
