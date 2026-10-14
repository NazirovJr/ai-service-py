"""Общие фикстуры для api-тестов."""

from collections.abc import AsyncIterator, Iterator

import httpx
import pytest
from fastapi import FastAPI

from ai_service_py.config import Settings
from ai_service_py.main import create_app


@pytest.fixture
def settings() -> Settings:
    return Settings(debug=True, log_level="DEBUG", http_timeout_seconds=1.0)


@pytest.fixture
def app(settings: Settings) -> Iterator[FastAPI]:
    application = create_app(settings)
    yield application
    application.dependency_overrides.clear()


@pytest.fixture
async def api_client(app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    """Вызывает приложение напрямую через ASGI — без сети и uvicorn."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
