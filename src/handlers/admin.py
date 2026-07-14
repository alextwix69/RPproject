import re

from src.core.logger import logger
from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from src.core.database import get_session
from src.keyboards.kb_build import (
    BTN_ADMIN_NOTIFY,
    BTN_ADMIN_RIGHTS,
    LEGACY_BUTTON_ALIASES,
    build_admin_panel,
    normalize_button_text,
)
from src.handlers.admin_handlers.users import register_admin_users_handlers
from src.repositories.user_repo import get_by_telegram_id, get_by_username
from src.services.admin_service import (
    grant_admin_role,
    is_admin_effective_user,
    is_owner_effective_user,
    revoke_admin_role,
)
from src.services.chat_cleanup_service import reply_text
from src.services.news_notification_service import send_news_notification

ADMIN_MESSAGE = (
    "👑✨ Админ-панель RoleHub\n\n"
    "📜 Команды хранителей из БД:\n"
    "/users - последние пользователи\n"
    "/user <telegram_id> - карточка пользователя\n"
    "/stats - статистика\n"
    "/export_users - экспорт CSV\n"
    "/notify <текст> - новостная рассылка\n\n"
    "🔐 Команды только для владельцев из OWNER_IDS:\n"
    "/makeadmin <telegram_id|@username> - выдать админские права (только владельцы)\n"
    "/removeadmin <telegram_id|@username> - забрать админские права (только владельцы)"
)

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("admin()")

    if not is_admin_effective_user(update.effective_user):
        return

    await reply_text(
        update.message,
        ADMIN_MESSAGE,
        reply_markup=build_admin_panel()
    )


async def admin_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.text is None:
        return

    if not is_admin_effective_user(update.effective_user):
        return

    text = normalize_button_text(update.message.text.strip())
    if text == BTN_ADMIN_NOTIFY:
        await reply_text(
            update.message,
            "📣✨ Новостная рассылка\n\n"
            "Отправь королевскую весточку командой:\n"
            "/notify текст новости",
            reply_markup=build_admin_panel(),
        )
        return

    if text == BTN_ADMIN_RIGHTS:
        await reply_text(
            update.message,
            "👑✨ Права админов\n\n"
            "Доступы:\n"
            "• /admin, /users, /user, /stats, /export_users, /notify — админы из БД\n"
            "• /makeadmin, /removeadmin — только владельцы из OWNER_IDS\n\n"
            "Выдать права:\n"
            "/makeadmin <telegram_id|@username>\n\n"
            "Забрать права:\n"
            "/removeadmin <telegram_id|@username>",
            reply_markup=build_admin_panel(),
        )
        return

    await reply_text(update.message, "🏗✨ Это действие хранителей пока готовится.", reply_markup=build_admin_panel())


async def notify_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin_effective_user(update.effective_user):
        return

    if update.message is None:
        return

    text = " ".join(context.args).strip()
    if not text:
        await reply_text(
            update.message,
            "Использование: /notify текст новости"
        )
        return

    await send_news_notification(update.get_bot(), text)


def _get_target_argument(context: ContextTypes.DEFAULT_TYPE) -> str | None:
    if not context.args:
        return None

    return context.args[0].strip()


def _resolve_target_telegram_id(raw_target: str | None) -> int | None:
    if not raw_target:
        return None

    if raw_target.startswith("@"):
        with get_session() as session:
            user = get_by_username(session, raw_target)
            return user.telegram_id if user is not None else None

    try:
        telegram_id = int(raw_target)
    except ValueError:
        return None

    with get_session() as session:
        user = get_by_telegram_id(session, telegram_id)
        return user.telegram_id if user is not None else None


def _target_usage(command: str) -> str:
    return f"Использование: /{command} <telegram_id|@username>"


async def makeadmin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner_effective_user(update.effective_user):
        return

    if update.message is None:
        return

    raw_target = _get_target_argument(context)
    telegram_id = _resolve_target_telegram_id(raw_target)
    if telegram_id is None:
        await reply_text(update.message, _target_usage("makeadmin"))
        return

    user = grant_admin_role(telegram_id)
    if user is None:
        await reply_text(update.message, "Пользователь с таким Telegram ID не найден в базе.")
        return

    await reply_text(update.message, f"Готово. Пользователь {telegram_id} теперь admin.")


async def removeadmin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner_effective_user(update.effective_user):
        return

    if update.message is None:
        return

    raw_target = _get_target_argument(context)
    telegram_id = _resolve_target_telegram_id(raw_target)
    if telegram_id is None:
        await reply_text(update.message, _target_usage("removeadmin"))
        return

    user = revoke_admin_role(telegram_id)
    if user is None:
        await reply_text(update.message, "Пользователь с таким Telegram ID не найден в базе.")
        return

    await reply_text(update.message, f"Готово. Пользователь {telegram_id} теперь user.")


def register_admin_handler(application) -> None:
    application.add_handler(CommandHandler("admin", admin))
    application.add_handler(CommandHandler("notify", notify_command))
    application.add_handler(CommandHandler("makeadmin", makeadmin_command))
    application.add_handler(CommandHandler("removeadmin", removeadmin_command))
    register_admin_users_handlers(application)
    application.add_handler(MessageHandler(_admin_filter(), admin_reply_handler))


def _admin_filter():
    buttons = {BTN_ADMIN_NOTIFY, BTN_ADMIN_RIGHTS}
    buttons.update(old for old, new in LEGACY_BUTTON_ALIASES.items() if new in buttons)
    pattern = "^(?:" + "|".join(re.escape(button) for button in buttons) + ")$"
    return filters.TEXT & ~filters.COMMAND & filters.Regex(pattern)
