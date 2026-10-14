"""Параллельный опрос HTTP-источников.

Домен: про FastAPI не знает, клиент получает аргументом.
"""

import asyncio
import logging

import httpx

logger = logging.getLogger(__name__)


async def send_request(client: httpx.AsyncClient, url: str) -> str:
    """Запрашивает один URL и возвращает тело ответа.

    Args:
        client: общий клиент — переиспользует пул соединений.
        url: адрес запроса.

    Returns:
        Тело ответа.

    Raises:
        httpx.HTTPStatusError: если сервер ответил 4xx/5xx.
        httpx.RequestError: ошибка сети или таймаут.
    """
    response = await client.get(url)
    response.raise_for_status()
    return response.text


async def fetch_all(urls: list[str], client: httpx.AsyncClient) -> list[str]:
    """Опрашивает все URL одновременно.

    Упавшие URL исключаются из результата и попадают в лог, поэтому
    соответствие индексов со входным списком НЕ сохраняется.

    Args:
        urls: список адресов.
        client: общий HTTP-клиент.

    Returns:
        Тела успешных ответов.

    Raises:
        asyncio.CancelledError: если задача была отменена — пробрасываем,
            иначе отмена перестанет работать.
    """
    outcomes = await asyncio.gather(
        *(send_request(client, url) for url in urls),
        return_exceptions=True,
    )

    results: list[str] = []
    for url, outcome in zip(urls, outcomes, strict=True):
        if isinstance(outcome, asyncio.CancelledError):
            raise outcome
        if isinstance(outcome, BaseException):
            logger.warning("Не удалось получить %s: %s", url, outcome)
            continue
        results.append(outcome)

    return results
