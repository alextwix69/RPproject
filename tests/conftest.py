"""
Общие настройки и фикстуры pytest.

Здесь обычно создаются тестовый бот, тестовая база данных, mock-сервисы,
event loop и другие объекты, которые нужны нескольким тестовым модулям.
"""
import pytest

from src.core.config import get_owner_ids

def test_get_owner_ids():
    assert get_owner_ids() == [1016417047, 592341623]
