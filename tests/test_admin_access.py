from src.core.config import get_owner_ids
from src.services.admin_service import is_admin_telegram_id, is_owner_telegram_id


def test_get_owner_ids_falls_back_to_legacy_admin_ids(monkeypatch):
    monkeypatch.delenv("OWNER_IDS", raising=False)
    monkeypatch.setenv("ADMIN_IDS", "1016417047, 592341623")

    assert get_owner_ids() == [1016417047, 592341623]


def test_owner_ids_take_priority_over_legacy_admin_ids(monkeypatch):
    monkeypatch.setenv("OWNER_IDS", "1,2")
    monkeypatch.setenv("ADMIN_IDS", "1016417047")

    assert get_owner_ids() == [1, 2]


def test_owner_is_admin_without_database_role(monkeypatch):
    monkeypatch.setenv("OWNER_IDS", "1016417047")

    assert is_owner_telegram_id(1016417047) is True
    assert is_admin_telegram_id(1016417047) is True
