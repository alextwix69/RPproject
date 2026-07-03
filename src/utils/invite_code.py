"""Генерация коротких кодов лобби."""

import secrets

ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def generate_lobby_code(length: int = 6) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))
