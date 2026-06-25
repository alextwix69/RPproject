from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from src.callbacks.main_menu import (
    MainMenuIntent,
    get_main_menu_response_text,
    resolve_main_menu_callback,
)
from src.core.database import get_session
from src.keyboards.inline_buttons import THEME_BACK_CALLBACK, THEME_TITLES
from src.keyboards.kb_build import build_choose_theme, build_main_menu
from src.services.user_service import ensure_from_effective_user


MAIN_MENU_TEXT = "Главное меню:"


async def _ensure_callback_user(update: Update) -> None:
    with get_session() as session:
        try:
            ensure_from_effective_user(session, update.effective_user)
            session.commit()
        except Exception:
            session.rollback()
            raise


async def main_menu_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query

    if query is None:
        return

    await query.answer()
    await _ensure_callback_user(update)

    intent = resolve_main_menu_callback(query.data or "")

    if intent == MainMenuIntent.PLAY:
        await query.edit_message_text(
            get_main_menu_response_text(intent),
            reply_markup=build_choose_theme(),
        )
        return

    await query.edit_message_text(get_main_menu_response_text(intent))


async def choose_theme_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query

    if query is None:
        return

    await query.answer()
    await _ensure_callback_user(update)

    if query.data == THEME_BACK_CALLBACK:
        await query.edit_message_text(
            MAIN_MENU_TEXT,
            reply_markup=build_main_menu(),
        )
        return

    theme_title = THEME_TITLES.get(query.data or "")
    if theme_title is None:
        await query.edit_message_text("Неизвестная тема. Вернись в меню и выбери ещё раз.")
        return

    await query.edit_message_text(f"Тема выбрана: {theme_title}")


def register_main_menu_handler(application) -> None:
    application.add_handler(CallbackQueryHandler(main_menu_handler, pattern=r"^main:"))
    application.add_handler(CallbackQueryHandler(choose_theme_handler, pattern=r"^theme:"))
