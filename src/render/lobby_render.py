"""Тексты экранов lobby-механики."""

from src.constants.roles import ROLES_BY_TOPIC
from src.constants.topics import TOPICS
from src.models.lobby import Lobby

MODE_NAMES = {"chat": "Обычное общение", "rp": "Ролевая игра"}
PRIVACY_NAMES = {"public": "Открытое", "private": "Приватное"}
STATUS_NAMES = {"waiting": "ожидание игроков", "active": "активно", "closed": "закрыто"}


def topic_name(topic: str | None) -> str:
    return TOPICS.get(topic or "", "Не выбрано")


def mode_name(mode: str | None) -> str:
    return MODE_NAMES.get(mode or "", "Не выбрано")


def privacy_name(privacy: str | None) -> str:
    return PRIVACY_NAMES.get(privacy or "", "Не выбрано")


def role_name(topic: str | None, role: str | None) -> str:
    if not role:
        return "-"
    return ROLES_BY_TOPIC.get(topic or "", {}).get(role, role)


def render_play_main() -> str:
    return "🎮 Играть\n\nВыбери действие:"


def render_create_topic() -> str:
    return "➕ Создание лобби\n\nВыбери тему:"


def render_create_mode(topic: str) -> str:
    return f"🎮 Тема: {topic_name(topic)}\n\nВыбери режим:"


def render_create_role(topic: str) -> str:
    return f"🎭 Ролевая игра\n\nТема: {topic_name(topic)}\n\nВыбери роль:"


def render_create_size() -> str:
    return "👥 Размер лобби\n\nСколько участников нужно?"


def render_create_privacy() -> str:
    return "🔐 Тип лобби\n\nВыбери доступность:"


def render_create_confirm(state: dict) -> str:
    return (
        "✅ Проверь настройки лобби\n\n"
        f"Тема: {topic_name(state.get('topic'))}\n"
        f"Режим: {mode_name(state.get('mode'))}\n"
        f"Роль: {role_name(state.get('topic'), state.get('role'))}\n"
        f"Игроков: {state.get('max_players')}\n"
        f"Тип: {privacy_name(state.get('privacy'))}\n\n"
        "Создать лобби?"
    )


def render_lobby_waiting(lobby: Lobby) -> str:
    code_line = f"\nКод: {lobby.code}\n" if lobby.privacy == "private" else "\n"
    return (
        "🚀 Лобби\n\n"
        f"Тема: {topic_name(lobby.topic)}\n"
        f"Режим: {mode_name(lobby.mode)}\n"
        f"Игроков: {lobby.players_count}/{lobby.max_players}\n"
        f"Тип: {privacy_name(lobby.privacy)}\n"
        f"Статус: {STATUS_NAMES.get(lobby.status, lobby.status)}\n"
        f"{code_line}\n"
        "Ожидаем участников..."
    )


def render_lobby_info(lobby: Lobby) -> str:
    return (
        "ℹ️ Информация о лобби\n\n"
        f"Тема: {topic_name(lobby.topic)}\n"
        f"Режим: {mode_name(lobby.mode)}\n"
        f"Игроков: {lobby.players_count}/{lobby.max_players}\n"
        f"Статус: {STATUS_NAMES.get(lobby.status, lobby.status)}\n"
        f"Тип: {privacy_name(lobby.privacy)}"
    )


def render_active_lobby_started(lobby: Lobby) -> str:
    return (
        "🚀 Лобби активно!\n\n"
        f"Тема: {topic_name(lobby.topic)}\n"
        f"Участников: {lobby.players_count}/{lobby.max_players}\n\n"
        "Теперь пиши сообщения прямо сюда — бот отправит их участникам лобби."
    )


def render_found_lobby(lobby: Lobby) -> str:
    return (
        "🔎 Найдено лобби\n\n"
        f"Тема: {topic_name(lobby.topic)}\n"
        f"Режим: {mode_name(lobby.mode)}\n"
        f"Игроков: {lobby.players_count}/{lobby.max_players}"
    )


def render_join_role(lobby: Lobby) -> str:
    return (
        "🎭 Выбор роли\n\n"
        f"Тема: {topic_name(lobby.topic)}\n"
        f"Лобби: {lobby.players_count}/{lobby.max_players}\n\n"
        "Выбери свободную роль для входа:"
    )


def render_no_lobby(topic: str) -> str:
    return (
        "😕 Свободных лобби нет\n\n"
        f"По теме {topic_name(topic)} пока нет открытых лобби."
    )


def render_quick_no_lobby(topic: str) -> str:
    return (
        "⚡ Свободных лобби нет\n\n"
        f"Можно создать новое лобби по теме {topic_name(topic)}."
    )
