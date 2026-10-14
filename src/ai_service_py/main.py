"""Точка входа: сборка приложения. Логики здесь нет."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from ai_service_py.config import Settings, get_settings
from ai_service_py.routes import chunk, fetch, health, stream

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup / shutdown. Всё, что живёт дольше одного запроса."""
    settings = get_settings()
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    )

    async with httpx.AsyncClient(
        timeout=httpx.Timeout(settings.http_timeout_seconds, connect=5.0),
        limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
    ) as client:
        app.state.http_client = client
        app.state.settings = settings
        logger.info("Приложение запущено: %s v%s", settings.app_name, settings.version)
        yield
    logger.info("Приложение остановлено")


def create_app(settings: Settings | None = None) -> FastAPI:
    """Фабрика приложения — чтобы в тестах собрать его с другими настройками."""
    settings = settings or get_settings()

    application = FastAPI(
        title=settings.app_name,
        version=settings.version,
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
    )

    application.include_router(health.router)
    application.include_router(chunk.router, prefix="/api/v1")
    application.include_router(fetch.router, prefix="/api/v1")
    application.include_router(stream.router, prefix="/api/v1")

    return application


app = create_app()
