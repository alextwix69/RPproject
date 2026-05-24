from telegram import Update
from telegram.ext import ContextTypes


async def main_menu_handler(update: Update,
                            context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    if query.data == "Играть 🎮":
        await query.edit_message_text(
            "Начинается игра"
        )

    elif query.data == "Магазин 🛍":
        await query.edit_message_text(
            "Тут будет магазин"
        )

    elif query.data == "Настройки ⚙️":
        await query.edit_message_text(
            "Тут будут Настройки"
        )

    elif query.data == "Поддержка 🆘":
        await query.edit_message_text(
            "Тут будет поддержка"
        )