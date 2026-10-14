"""Health-check. Версии в пути нет: эндпоинт для k8s, не для клиентов."""

import time

from fastapi import APIRouter

from ai_service_py.deps import SettingsDep
from ai_service_py.schemes import HealthResponse

router = APIRouter(prefix="/health", tags=["ops"])


@router.get("/check", response_model=HealthResponse)
async def health_check(settings: SettingsDep) -> HealthResponse:
    return HealthResponse(status="ok", version=settings.version, timestamp=time.time())
