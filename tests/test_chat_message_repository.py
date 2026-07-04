from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models.base import Base
from src.repositories.chat_message_repo import (
    get_active_screen,
    list_clearable_messages,
    remember_message,
)


def make_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestSessionLocal = sessionmaker(bind=engine)
    return TestSessionLocal()


def test_active_screen_is_not_clearable_and_replaces_previous_active_screen():
    session = make_session()

    remember_message(session, chat_id=100, message_id=1, is_active_screen=True)
    remember_message(session, chat_id=100, message_id=2, is_active_screen=True)
    remember_message(session, chat_id=100, message_id=3, is_notify=True)
    session.commit()

    active_screen = get_active_screen(session, 100)
    clearable_messages = list_clearable_messages(session, 100)

    assert active_screen.message_id == 2
    assert [message.message_id for message in clearable_messages] == [3, 1]

    session.close()
