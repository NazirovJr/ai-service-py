"""Тесты параллельного опроса.

Сеть не используется: httpx.MockTransport подменяет транспорт, поэтому тесты
детерминированы, мгновенны и работают в CI без интернета.
"""

import asyncio
import time
from collections.abc import AsyncIterator

import httpx
import pytest

from ai_service_py.domain.parallel import fetch_all, send_request

SLOW_RESPONSE_SECONDS = 0.3


async def handler(request: httpx.Request) -> httpx.Response:
    """Отвечает по-разному в зависимости от пути — имитация разных источников."""
    path = request.url.path
    if path == "/slow":
        await asyncio.sleep(SLOW_RESPONSE_SECONDS)
        return httpx.Response(200, text="slow-ok")
    if path == "/fail":
        return httpx.Response(500, text="boom")
    return httpx.Response(200, text="ok")


# БЫЛО: monkeypatch подменял httpx.AsyncClient внутри модуля, потому что
# fetch_all создавал клиент сам. СТАЛО: fetch_all принимает клиент
# аргументом, поэтому достаточно обычной фикстуры — патчинг не нужен.
@pytest.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as c:
        yield c


# --- одиночный запрос ----------------------------------------------------


async def test_send_request_returns_body(client: httpx.AsyncClient) -> None:
    assert await send_request(client, "https://example.test/") == "ok"


async def test_send_request_raises_on_server_error(client: httpx.AsyncClient) -> None:
    with pytest.raises(httpx.HTTPStatusError):
        await send_request(client, "https://example.test/fail")


# --- параллельность ------------------------------------------------------


async def test_requests_run_in_parallel(client: httpx.AsyncClient) -> None:
    """Три медленных запроса должны занять ~время одного, а не трёх."""
    urls = ["https://example.test/slow"] * 3

    started = time.perf_counter()
    results = await fetch_all(urls, client)
    elapsed = time.perf_counter() - started

    assert results == ["slow-ok"] * 3
    assert elapsed < SLOW_RESPONSE_SECONDS * 2, (
        f"похоже, запросы идут последовательно: {elapsed:.2f} с"
    )


# --- устойчивость к сбоям ------------------------------------------------


async def test_failure_does_not_break_others(client: httpx.AsyncClient) -> None:
    urls = [
        "https://example.test/a",
        "https://example.test/fail",
        "https://example.test/b",
    ]
    assert await fetch_all(urls, client) == ["ok", "ok"]


async def test_all_failures_return_empty_list(client: httpx.AsyncClient) -> None:
    assert await fetch_all(["https://example.test/fail"] * 2, client) == []


async def test_empty_input(client: httpx.AsyncClient) -> None:
    assert await fetch_all([], client) == []


async def test_failure_is_logged(
    client: httpx.AsyncClient, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level("WARNING"):
        await fetch_all(["https://example.test/fail"], client)
    assert "example.test/fail" in caplog.text
