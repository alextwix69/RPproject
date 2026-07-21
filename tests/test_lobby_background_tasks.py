import asyncio
from types import SimpleNamespace

from src.handlers.play_lobby import (
    start_lobby_background_tasks,
    stop_lobby_background_tasks,
)


def test_fallback_expiration_task_is_cancelled_on_shutdown():
    async def scenario():
        application = SimpleNamespace(_job_queue=None, bot_data={}, bot=object())

        await start_lobby_background_tasks(application)
        task = application.bot_data["lobby_expiration_task"]

        assert not task.done()

        await stop_lobby_background_tasks(application)

        assert task.cancelled()
        assert "lobby_expiration_task" not in application.bot_data

    asyncio.run(scenario())


def test_fallback_expiration_task_is_started_only_once():
    async def scenario():
        application = SimpleNamespace(_job_queue=None, bot_data={}, bot=object())

        await start_lobby_background_tasks(application)
        first_task = application.bot_data["lobby_expiration_task"]
        await start_lobby_background_tasks(application)

        assert application.bot_data["lobby_expiration_task"] is first_task

        await stop_lobby_background_tasks(application)

    asyncio.run(scenario())
