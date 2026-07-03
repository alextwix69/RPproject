"""Сохранение и рассылка сообщений активного лобби."""

from dataclasses import dataclass

from telegram import Bot, Message

from src.core.database import get_session
from src.core.logger import logger
from src.repositories import lobby_member_repo, lobby_message_repo
from src.repositories.user_repo import get_by_id
from src.utils.display_name import format_display_name


@dataclass
class LobbyMessagePayload:
    message_type: str
    text: str | None = None
    file_id: str | None = None


def format_sender_name(user) -> str:
    return format_display_name(user)


def payload_from_telegram_message(message: Message) -> LobbyMessagePayload | None:
    if message.text:
        return LobbyMessagePayload("text", text=message.text)
    if message.photo:
        return LobbyMessagePayload(
            "photo",
            text=message.caption,
            file_id=message.photo[-1].file_id,
        )
    if message.sticker:
        return LobbyMessagePayload("sticker", file_id=message.sticker.file_id)
    if message.voice:
        return LobbyMessagePayload("voice", file_id=message.voice.file_id)
    return None


async def send_message_to_lobby(
    bot: Bot,
    lobby_id: int,
    sender_id: int,
    payload: LobbyMessagePayload,
) -> None:
    with get_session() as session:
        try:
            sender = get_by_id(session, sender_id)
            recipients = lobby_member_repo.list_joined_users(session, lobby_id)
            save_lobby_message(session, lobby_id, sender_id, payload)
            session.commit()
        except Exception:
            session.rollback()
            logger.exception("Failed to save lobby message")
            raise

    sender_name = format_sender_name(sender)
    for _member, recipient in recipients:
        if recipient.id == sender_id:
            continue
        try:
            if payload.message_type == "text":
                await bot.send_message(
                    chat_id=recipient.telegram_id,
                    text=f"💬 {sender_name}:\n{payload.text}",
                )
            elif payload.message_type == "photo":
                caption = f"📷 {sender_name}"
                if payload.text:
                    caption = f"{caption}\n{payload.text}"
                await bot.send_photo(
                    chat_id=recipient.telegram_id,
                    photo=payload.file_id,
                    caption=caption,
                )
            elif payload.message_type == "sticker":
                await bot.send_sticker(chat_id=recipient.telegram_id, sticker=payload.file_id)
                await bot.send_message(
                    chat_id=recipient.telegram_id,
                    text=f"🧩 Стикер от {sender_name}",
                )
            elif payload.message_type == "voice":
                await bot.send_voice(chat_id=recipient.telegram_id, voice=payload.file_id)
                await bot.send_message(
                    chat_id=recipient.telegram_id,
                    text=f"🎙 Голосовое от {sender_name}",
                )
        except Exception:
            logger.exception("Failed to send lobby message to user %s", recipient.id)


def save_lobby_message(session, lobby_id: int, sender_id: int, payload: LobbyMessagePayload):
    return lobby_message_repo.create_message(
        session,
        lobby_id=lobby_id,
        sender_id=sender_id,
        message_type=payload.message_type,
        text=payload.text,
        file_id=payload.file_id,
    )
