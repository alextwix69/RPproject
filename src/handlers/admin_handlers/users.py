"""Admin commands for viewing Telegram users stored in the database."""

from __future__ import annotations

import csv
from datetime import datetime
from io import BytesIO, StringIO

from telegram import InputFile, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

from src.core.config import get_admin_ids
from src.core.database import get_session
from src.keyboards.kb_build import build_admin_panel
from src.models.user import User
from src.repositories.user_repo import (
    get_by_telegram_id,
    get_users_stats,
    list_all_users,
    list_users,
)


def _is_admin(update: Update) -> bool:
    return (
        update.effective_user is not None
        and update.effective_user.id in get_admin_ids()
    )


async def _deny(update: Update) -> None:
    if update.callback_query is not None:
        await update.callback_query.answer("Нет доступа", show_alert=True)
        return

    if update.message is not None:
        await update.message.reply_text("Нет доступа")


def _format_datetime(value: datetime | None) -> str:
    if value is None:
        return "-"

    return value.strftime("%d.%m.%Y %H:%M:%S")


def _format_username(user: User) -> str:
    if user.username:
        return f"@{user.username}"

    return "-"


def _format_full_name(user: User) -> str:
    full_name = " ".join(
        part
        for part in (user.first_name, user.last_name)
        if part
    ).strip()

    return full_name or "-"


def _format_display_name(user: User) -> str:
    if user.username:
        return f"@{user.username}"

    return _format_full_name(user)


def _format_user_short(user: User, number: int) -> str:
    return (
        f"{number}. {_format_display_name(user)}\n"
        f"TG ID: {user.telegram_id}\n"
        f"Имя: {_format_full_name(user)}\n"
        f"Язык: {user.language_code or '-'}\n"
        f"Первый вход: {_format_datetime(user.first_seen_at)}\n"
        f"Последний вход: {_format_datetime(user.last_seen_at)}"
    )


def _format_user_full(user: User) -> str:
    return (
        "Пользователь\n\n"
        f"DB ID: {user.id}\n"
        f"TG ID: {user.telegram_id}\n"
        f"Отображение: {_format_display_name(user)}\n"
        f"Username: {_format_username(user)}\n"
        f"Имя: {_format_full_name(user)}\n"
        f"Язык: {user.language_code or '-'}\n"
        f"Бот: {'да' if user.is_bot else 'нет'}\n"
        f"Роль: {user.role}\n"
        f"Первый вход: {_format_datetime(user.first_seen_at)}\n"
        f"Последний вход: {_format_datetime(user.last_seen_at)}\n"
        f"Создан: {_format_datetime(user.created_at)}\n"
        f"Обновлен: {_format_datetime(user.updated_at)}"
    )


def _users_text(limit: int = 10) -> str:
    with get_session() as session:
        users = list_users(session, limit=limit)

    if not users:
        return "В базе пока нет пользователей."

    parts = ["Последние пользователи:\n"]
    parts.extend(_format_user_short(user, index) for index, user in enumerate(users, 1))
    return "\n\n".join(parts)


def _stats_text() -> str:
    with get_session() as session:
        stats = get_users_stats(session)

    return (
        "Статистика пользователей\n\n"
        f"Всего в базе: {stats['total']}\n"
        f"Боты: {stats['bots']}\n"
        f"Активны сегодня: {stats['active_today']}\n"
        f"Активны за 7 дней: {stats['active_week']}"
    )


def _users_csv_file() -> InputFile:
    with get_session() as session:
        users = list_all_users(session)

    text_buffer = StringIO()
    writer = csv.writer(text_buffer)
    writer.writerow(
        [
            "db_id",
            "telegram_id",
            "display_name",
            "username",
            "full_name",
            "first_name",
            "last_name",
            "language_code",
            "is_bot",
            "role",
            "first_seen_at",
            "last_seen_at",
            "created_at",
            "updated_at",
        ]
    )

    for user in users:
        writer.writerow(
            [
                user.id,
                user.telegram_id,
                _format_display_name(user),
                user.username,
                _format_full_name(user),
                user.first_name,
                user.last_name,
                user.language_code,
                user.is_bot,
                user.role,
                _format_datetime(user.first_seen_at),
                _format_datetime(user.last_seen_at),
                _format_datetime(user.created_at),
                _format_datetime(user.updated_at),
            ]
        )

    bytes_buffer = BytesIO(text_buffer.getvalue().encode("utf-8-sig"))
    bytes_buffer.name = "users.csv"
    return InputFile(bytes_buffer, filename="users.csv")


def _parse_limit(context: ContextTypes.DEFAULT_TYPE, default: int = 10) -> int:
    if not context.args:
        return default

    try:
        return max(1, min(int(context.args[0]), 50))
    except ValueError:
        return default


async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update):
        await _deny(update)
        return

    if update.message is None:
        return

    await update.message.reply_text(_users_text(limit=_parse_limit(context)))


async def user_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update):
        await _deny(update)
        return

    if update.message is None:
        return

    if not context.args:
        await update.message.reply_text("Использование: /user <telegram_id>")
        return

    try:
        telegram_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Telegram ID должен быть числом.")
        return

    with get_session() as session:
        user = get_by_telegram_id(session, telegram_id)

    if user is None:
        await update.message.reply_text("Пользователь не найден.")
        return

    await update.message.reply_text(_format_user_full(user))


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update):
        await _deny(update)
        return

    if update.message is not None:
        await update.message.reply_text(_stats_text())


async def export_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update):
        await _deny(update)
        return

    if update.message is not None:
        await update.message.reply_document(
            document=_users_csv_file(),
            caption="Экспорт пользователей из БД",
        )


async def admin_users_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query

    if query is None:
        return

    if not _is_admin(update):
        await _deny(update)
        return

    if query.data == "admin:users":
        await query.answer()
        await query.edit_message_text(_users_text(), reply_markup=build_admin_panel())
        return

    if query.data == "admin:stats":
        await query.answer()
        await query.edit_message_text(_stats_text(), reply_markup=build_admin_panel())
        return

    if query.data == "admin:export_users":
        await query.answer("Готовлю CSV")
        if query.message is not None:
            await query.message.reply_document(
                document=_users_csv_file(),
                caption="Экспорт пользователей из БД",
            )


def register_admin_users_handlers(application) -> None:
    application.add_handler(CommandHandler("users", users_command))
    application.add_handler(CommandHandler("user", user_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("export_users", export_users_command))
    application.add_handler(
        CallbackQueryHandler(
            admin_users_callback,
            pattern=r"^admin:(users|stats|export_users)$",
        )
    )
