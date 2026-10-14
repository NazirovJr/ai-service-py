"""HTTP-слой для параллельного опроса источников."""

from fastapi import APIRouter, status

from ai_service_py.deps import HttpClientDep
from ai_service_py.domain.parallel import fetch_all
from ai_service_py.schemes import FetchRequest, FetchResponse

router = APIRouter(prefix="/fetch", tags=["fetch"])


@router.post("/all", response_model=FetchResponse, status_code=status.HTTP_200_OK)
async def fetch_urls(payload: FetchRequest, client: HttpClientDep) -> FetchResponse:
    bodies = await fetch_all(payload.urls, client)
    return FetchResponse(
        bodies=bodies,
        requested=len(payload.urls),
        succeeded=len(bodies),
    )
