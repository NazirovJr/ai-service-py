"""Провайдеры зависимостей для Depends. Только достать и отдать — без логики."""

from typing import Annotated

import httpx
from fastapi import Depends, Request

from ai_service_py.config import Settings, get_settings


def get_http_client(request: Request) -> httpx.AsyncClient:
    """Отдаёт общий HTTP-клиент, созданный в lifespan."""
    client: httpx.AsyncClient = request.app.state.http_client
    return client


HttpClientDep = Annotated[httpx.AsyncClient, Depends(get_http_client)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
