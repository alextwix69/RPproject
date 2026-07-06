from src.models.lobby import Lobby
from src.render.lobby_render import render_lobby_waiting


def test_public_waiting_lobby_shows_code():
    lobby = Lobby(
        code="ABCD12",
        topic="brawl_stars",
        mode="rp",
        owner_id=1,
        max_players=15,
        players_count=1,
        privacy="public",
        status="waiting",
    )

    assert "Код: ABCD12" in render_lobby_waiting(lobby)
