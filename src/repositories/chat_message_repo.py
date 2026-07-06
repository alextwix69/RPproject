"""Хранение Telegram message_id для очистки чата."""

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from src.models.chat_message import ChatMessage


def remember_message(
    session: Session,
    chat_id: int,
    message_id: int,
    is_notify: bool = False,
    is_active_screen: bool = False,
) -> ChatMessage:
    message = session.scalar(
        select(ChatMessage)
        .where(
            ChatMessage.chat_id == chat_id,
            ChatMessage.message_id == message_id,
        )
        .order_by(ChatMessage.id.desc())
        .limit(1)
    )
    if message is None:
        message = ChatMessage(
            chat_id=chat_id,
            message_id=message_id,
            is_notify=is_notify,
            is_active_screen=is_active_screen,
        )
        session.add(message)
    else:
        message.is_notify = is_notify
        message.is_active_screen = is_active_screen

    if is_active_screen:
        session.execute(
            update(ChatMessage)
            .where(ChatMessage.chat_id == chat_id)
            .where(ChatMessage.message_id != message_id)
            .values(is_active_screen=False)
        )

    return message


def get_active_screen(session: Session, chat_id: int) -> ChatMessage | None:
    stmt = (
        select(ChatMessage)
        .where(ChatMessage.chat_id == chat_id)
        .where(ChatMessage.is_active_screen.is_(True))
        .order_by(ChatMessage.message_id.desc())
        .limit(1)
    )
    return session.scalar(stmt)


def list_clearable_messages(session: Session, chat_id: int) -> list[ChatMessage]:
    stmt = (
        select(ChatMessage)
        .where(ChatMessage.chat_id == chat_id)
        .where(ChatMessage.is_active_screen.is_(False))
        .order_by(ChatMessage.message_id.desc())
    )
    return list(session.scalars(stmt).all())


def forget_messages(session: Session, message_ids: list[int]) -> None:
    if not message_ids:
        return

    session.execute(delete(ChatMessage).where(ChatMessage.id.in_(message_ids)))


def forget_message_by_telegram_id(session: Session, chat_id: int, message_id: int) -> None:
    session.execute(
        delete(ChatMessage).where(
            ChatMessage.chat_id == chat_id,
            ChatMessage.message_id == message_id,
        )
    )
