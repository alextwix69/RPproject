"""
Обработчик команды /start и первичного входа пользователя.

Здесь обычно формируется приветствие, проверяется состояние пользователя,
показывается главное меню и запускаются первые шаги регистрации или знакомства
с ботом.
"""

from src.core.logger import logger
from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes
)

from src.keyboards.main_menu import build_main_menu

START_MESSAGE = (
    "Добро пожаловать в RoleHub!\n"
)

# что делает бот при start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("start()")

    await update.message.reply_text(
        START_MESSAGE,
        reply_markup=build_main_menu()
    )

# связь вызова /start и функции start()
def register_start_handler(application) -> None:
    application.add_handler(CommandHandler("start", start))
