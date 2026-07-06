"""Best-effort очистка личного чата с ботом."""

from telegram import Message, Update
from telegram.error import BadRequest, Forbidden

from src.core.database import get_session
from src.core.logger import logger
from src.repositories.chat_message_repo import (
    forget_messages,
    forget_message_by_telegram_id,
    get_active_screen,
    list_clearable_messages,
    remember_message,
)


def remember_telegram_message(
    message: Message | None,
    is_notify: bool = False,
    is_active_screen: bool = False,
) -> None:
    if message is None or message.chat_id is None or message.message_id is None:
        return

    with get_session() as session:
        remember_message(
            session,
            chat_id=message.chat_id,
            message_id=message.message_id,
            is_notify=is_notify,
            is_active_screen=is_active_screen,
        )
        session.commit()


async def reply_text(
    message: Message,
    *args,
    is_notify: bool = False,
    is_active_screen: bool = False,
    **kwargs,
) -> Message:
    sent_message = await message.reply_text(*args, **kwargs)
    active_screen = is_active_screen or kwargs.get("reply_markup") is not None
    remember_telegram_message(
        sent_message,
        is_notify=is_notify,
        is_active_screen=active_screen,
    )
    return sent_message


async def track_incoming_message(update: Update, _context) -> None:
    remember_telegram_message(update.effective_message)


async def edit_active_screen(update: Update, text: str, reply_markup=None) -> bool:
    if update.effective_chat is None:
        return False

    chat_id = update.effective_chat.id
    with get_session() as session:
        active_message = get_active_screen(session, chat_id)

    if active_message is None:
        return False

    try:
        sent_message = await update.get_bot().edit_message_text(
            chat_id=chat_id,
            message_id=active_message.message_id,
            text=text,
            reply_markup=reply_markup,
        )
        if sent_message is not True:
            remember_telegram_message(sent_message, is_active_screen=True)
        return True
    except BadRequest as exc:
        if "message is not modified" in str(exc).lower():
            return True
        return False
    except Forbidden:
        return False


async def delete_known_message(message: Message | None) -> bool:
    if message is None or message.chat_id is None or message.message_id is None:
        return False

    try:
        await message.delete()
    except (BadRequest, Forbidden):
        return False
    except Exception:
        logger.exception(
            "Failed to delete message %s in chat %s",
            message.message_id,
            message.chat_id,
        )
        return False

    with get_session() as session:
        forget_message_by_telegram_id(session, message.chat_id, message.message_id)
        session.commit()
    return True


async def clear_chat(update: Update) -> int:
    if update.effective_chat is None:
        return 0

    chat_id = update.effective_chat.id
    with get_session() as session:
        messages = list_clearable_messages(session, chat_id)

    deleted = 0
    forgotten_ids = []
    for message in messages:
        try:
            await update.get_bot().delete_message(
                chat_id=chat_id,
                message_id=message.message_id,
            )
            deleted += 1
        except (BadRequest, Forbidden):
            logger.info(
                "Cannot delete message %s in chat %s",
                message.message_id,
                chat_id,
            )
        except Exception:
            logger.exception(
                "Failed to delete message %s in chat %s",
                message.message_id,
                chat_id,
            )
        forgotten_ids.append(message.id)

    with get_session() as session:
        forget_messages(session, forgotten_ids)
        session.commit()

    return deleted
