"""Тексты экранов lobby-механики."""

from src.constants.roles import ROLES_BY_TOPIC
from src.constants.topics import TOPICS
from src.models.lobby import Lobby

MODE_NAMES = {"rp": "ролевая история 🎭"}
PRIVACY_NAMES = {"public": "открытый мир 🌍", "private": "тайный мир 🔒"}
STATUS_NAMES = {"waiting": "ждём героев ✨", "active": "приключение идёт 🌟", "closed": "мир закрыт 🌙"}


def topic_name(topic: str | None) -> str:
    return TOPICS.get(topic or "", "ещё не выбрано ✨")


def mode_name(mode: str | None) -> str:
    return MODE_NAMES.get(mode or "", "ещё не выбрано ✨")


def privacy_name(privacy: str | None) -> str:
    return PRIVACY_NAMES.get(privacy or "", "ещё не выбрано ✨")


def role_name(topic: str | None, role: str | None) -> str:
    if not role:
        return "-"
    return ROLES_BY_TOPIC.get(topic or "", {}).get(role, role)


def render_play_main() -> str:
    return "🌌✨ Врата миров открыты!\n\nСоздай собственную историю или найди приключение:"


def render_create_topic() -> str:
    return "✨🏰 Создание нового мира\n\nВ какую вселенную отправимся?"


def render_create_role(topic: str) -> str:
    return f"🎭✨ Выбор героя\n\nВселенная: {topic_name(topic)}\n\nКем ты станешь в этой истории?"


def render_create_privacy() -> str:
    return "🔐✨ Тайна нового мира\n\nКто сможет войти в твоё приключение?"


def render_create_confirm(state: dict) -> str:
    return (
        "👑✨ Проверь свиток нового мира\n\n"
        f"🌌 Вселенная: {topic_name(state.get('topic'))}\n"
        f"🎭 Твоя роль: {role_name(state.get('topic'), state.get('role'))}\n"
        f"👥 Героев: {state.get('max_players', 15)}\n"
        f"🔐 Доступ: {privacy_name(state.get('privacy'))}\n\n"
        "Всё готово? Открываем портал! 🚀"
    )


def render_lobby_waiting(lobby: Lobby) -> str:
    return (
        "🏰✨ Твой мир готов\n\n"
        f"🔑 Волшебный код: {lobby.code}\n"
        f"🌌 Вселенная: {topic_name(lobby.topic)}\n"
        f"🎭 История: {mode_name(lobby.mode)}\n"
        f"👥 Героев: {lobby.players_count}/{lobby.max_players}\n"
        f"🔐 Доступ: {privacy_name(lobby.privacy)}\n"
        f"✨ Сейчас: {STATUS_NAMES.get(lobby.status, lobby.status)}\n"
        "\n"
        "Зовём новых героев в приключение... 🌟"
    )


def render_lobby_info(lobby: Lobby) -> str:
    return (
        "📜✨ Свиток этого мира\n\n"
        f"🔑 Волшебный код: {lobby.code}\n"
        f"🌌 Вселенная: {topic_name(lobby.topic)}\n"
        f"🎭 История: {mode_name(lobby.mode)}\n"
        f"👥 Героев: {lobby.players_count}/{lobby.max_players}\n"
        f"✨ Сейчас: {STATUS_NAMES.get(lobby.status, lobby.status)}\n"
        f"🔐 Доступ: {privacy_name(lobby.privacy)}"
    )


def render_active_lobby_started(lobby: Lobby) -> str:
    return (
        "🚀✨ Портал открыт — приключение началось!\n\n"
        f"🔑 Волшебный код: {lobby.code}\n"
        f"🌌 Вселенная: {topic_name(lobby.topic)}\n"
        f"👥 Героев: {lobby.players_count}/{lobby.max_players}\n\n"
        "Пиши сообщения прямо сюда — магия RoleHub доставит их всем героям этого мира 💫"
    )


def render_found_lobby(lobby: Lobby) -> str:
    return (
        "🔮✨ Подходящий мир найден!\n\n"
        f"🔑 Волшебный код: {lobby.code}\n"
        f"🌌 Вселенная: {topic_name(lobby.topic)}\n"
        f"🎭 История: {mode_name(lobby.mode)}\n"
        f"👥 Героев: {lobby.players_count}/{lobby.max_players}"
    )


def render_join_role(lobby: Lobby) -> str:
    return (
        "🎭✨ Выбери своего героя\n\n"
        f"🔑 Волшебный код: {lobby.code}\n"
        f"🌌 Вселенная: {topic_name(lobby.topic)}\n"
        f"👥 В мире: {lobby.players_count}/{lobby.max_players}\n\n"
        "Какая свободная роль станет твоей? 👑"
    )


def render_no_lobby(topic: str) -> str:
    return (
        "🌙✨ Порталы пока молчат\n\n"
        f"Во вселенной {topic_name(topic)} сейчас нет открытых миров. Но ты можешь создать первый! 👑"
    )


def render_quick_no_lobby(topic: str) -> str:
    return (
        "⚡✨ Свободных миров пока нет\n\n"
        f"Создай новое приключение во вселенной {topic_name(topic)} и стань его первым героем 👑"
    )
