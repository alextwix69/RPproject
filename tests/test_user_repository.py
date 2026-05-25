from types import SimpleNamespace

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from src.models.base import Base
from src.models.user import User
from src.repositories.user_repo import ensure_from_effective_user


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

    session