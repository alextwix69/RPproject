"""
Настройка логирования приложения.

Здесь обычно задаются формат сообщений, уровень логов, вывод в консоль и/или
файлы. Единая настройка логирования помогает handlers, services и scripts
писать события в одном стиле.
"""

import logging

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger(__name__)

logger.info("app started")



