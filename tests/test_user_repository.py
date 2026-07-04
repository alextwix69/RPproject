from types import SimpleNamespace

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from src.models.base import Base
from src.models.user import User
from src.services.user_service import DisplayNameError
from src.services.user_service import ensure_from_effective_user
from src.services.user_service import set_display_name
from src.services.user_service import toggle_news_notifications

from src.repositories.user_repo import (
    get_by_telegram_id,
    get_by_username,
    get_users_stats,
    list_admin_users,
    list_news_notification_users,
    list_users,
    set_role_by_telegram_id,
)

def make_effective_user(
    telegram_id: int = 100,
    username: str = "test_user",
    first_name: str = "Test",
    last_name: str = "User",
    language_code: str = "ru",
    is_bot: bool = False,
):
    """Создает тестовый аналог Telegram effective_user."""

    return SimpleNamespace(
        id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        language_code=language_code,
        is_bot=is_bot,
    )


def make_session():
    """Создает временную SQLite БД и возвращает тестовую session."""

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)

    TestSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    return TestSessionLocal()


def test_new_effective_user_creates_user():
    """Новый Telegram effective_user создает пользователя в БД."""

    session = make_session()
    effective_user = make_effective_user()

    user = ensure_from_effective_user(session, effective_user)
    session.commit()

    assert user is not None
    assert user.telegram_id == effective_user.id
    assert user.username == "test_user"
    assert user.display_name is None

    session.close()


def test_repeated_effective_user_does_not_create_duplicate():
    """Повторный Telegram effective_user не создает дубль пользователя."""

    session = make_session()
    effective_user = make_effective_user()

    user_1 = ensure_from_effective_user(session, effective_user)
    session.commit()

    user_2 = ensure_from_effective_user(session, effective_user)
    session.commit()

    users = session.scalars(select(User)).all()

    assert user_1.id == user_2.id
    assert len(users) == 1

    session.close()


def test_username_updates_on_repeated_interaction():
    """Username обновляется при повторном взаимодействии пользователя."""

    session = make_session()

    first_effective_user = make_effective_user(username="old_username")
    second_effective_user = make_effective_user(username="new_username")

    user = ensure_from_effective_user(session, first_effective_user)
    session.commit()

    updated_user = ensure_from_effective_user(session, second_effective_user)
    session.commit()

    assert user.id == updated_user.id
    assert updated_user.username == "new_username"

    session.close()


def test_is_registered_does_not_reset_on_update():
    """is_registered=True не сбрасывается при обновлении Telegram-данных."""

    session = make_session()

    first_effective_user = make_effective_user(username="old_username")
    second_effective_user = make_effective_user(username="new_username")

    user = ensure_from_effective_user(session, first_effective_user)
    user.is_registered = True
    session.commit()

    updated_user = ensure_from_effective_user(session, second_effective_user)
    session.commit()

    assert updated_user.is_registered is True
    assert updated_user.username == "new_username"

    session.close()

def test_get_by_telegram_id_type():
    session = make_session()
    effective_user = make_effective_user(telegram_id=1016417047)

    created_user = ensure_from_effective_user(session, effective_user)
    session.commit()

    found_user = get_by_telegram_id(session, effective_user.id)
    missing_user = get_by_telegram_id(session, 404)

    assert isinstance(found_user, User)
    assert found_user.id == created_user.id
    assert missing_user is None

    session.close()


def test_get_by_username_finds_user_with_at_sign_case_insensitive():
    session = make_session()
    created_user = ensure_from_effective_user(
        session,
        make_effective_user(telegram_id=1, username="SomeUser"),
    )
    session.commit()

    found_user = get_by_username(session, "@someuser")
    found_without_at = get_by_username(session, "SOMEUSER")
    missing_user = get_by_username(session, "@missing")

    assert found_user.id == created_user.id
    assert found_without_at.id == created_user.id
    assert missing_user is None

    session.close()


def test_admin_user_list_and_stats():
    session = make_session()

    user_1 = ensure_from_effective_user(
        session,
        make_effective_user(telegram_id=1, username="first"),
    )
    user_2 = ensure_from_effective_user(
        session,
        make_effective_user(telegram_id=2, username="second"),
    )
    user_2.is_registered = True
    session.commit()

    users = list_users(session, limit=10)
    stats = get_users_stats(session)

    assert [user.telegram_id for user in users] == [2, 1]
    assert stats["total"] == 2
    assert stats["registered"] == 1
    assert stats["not_registered"] == 1
    assert stats["bots"] == 0

    session.close()


def test_news_notifications_enabled_by_default_and_can_be_toggled():
    session = make_session()
    user = ensure_from_effective_user(session, make_effective_user())

    assert user.news_notifications_enabled is True

    enabled = toggle_news_notifications(user)
    session.commit()

    assert enabled is False
    assert user.news_notifications_enabled is False

    session.close()


def test_list_news_notification_users_returns_only_enabled_humans():
    session = make_session()
    enabled_user = ensure_from_effective_user(
        session,
        make_effective_user(telegram_id=1, username="enabled"),
    )
    disabled_user = ensure_from_effective_user(
        session,
        make_effective_user(telegram_id=2, username="disabled"),
    )
    bot_user = ensure_from_effective_user(
        session,
        make_effective_user(telegram_id=3, username="bot", is_bot=True),
    )
    disabled_user.news_notifications_enabled = False
    session.commit()

    users = list_news_notification_users(session)

    assert [user.id for user in users] == [enabled_user.id]
    assert bot_user not in users

    session.close()


def test_set_role_by_telegram_id_changes_user_role():
    session = make_session()
    user = ensure_from_effective_user(session, make_effective_user(telegram_id=1))
    session.commit()

    updated_user = set_role_by_telegram_id(session, 1, "admin")
    missing_user = set_role_by_telegram_id(session, 404, "admin")
    session.commit()

    assert updated_user.id == user.id
    assert updated_user.role == "admin"
    assert missing_user is None

    session.close()


def test_list_admin_users_returns_only_role_admin_humans():
    session = make_session()
    admin_user = ensure_from_effective_user(
        session,
        make_effective_user(telegram_id=1, username="admin"),
    )
    normal_user = ensure_from_effective_user(
        session,
        make_effective_user(telegram_id=2, username="normal"),
    )
    bot_admin = ensure_from_effective_user(
        session,
        make_effective_user(telegram_id=3, username="bot_admin", is_bot=True),
    )
    admin_user.role = "admin"
    bot_admin.role = "admin"
    session.commit()

    users = list_admin_users(session)

    assert [user.id for user in users] == [admin_user.id]
    assert normal_user not in users
    assert bot_admin not in users

    session.close()


def test_set_display_name_saves_normalized_unique_name():
    session = make_session()
    user = ensure_from_effective_user(session, make_effective_user())

    set_display_name(session, user, "  Alice   Rolehub  ")
    session.commit()

    assert user.display_name == "Alice Rolehub"
    assert user.is_registered is True

    session.close()


def test_set_display_name_rejects_duplicate_case_insensitive_name():
    session = make_session()
    user_1 = ensure_from_effective_user(
        session,
        make_effective_user(telegram_id=1, username="first"),
    )
    user_2 = ensure_from_effective_user(
        session,
        make_effective_user(telegram_id=2, username="second"),
    )
    set_display_name(session, user_1, "Alice")
    session.commit()

    try:
        set_display_name(session, user_2, "alice")
    except DisplayNameError as exc:
        assert exc.code == "taken"
    else:
        raise AssertionError("Duplicate display name should be rejected.")

    session.close()
