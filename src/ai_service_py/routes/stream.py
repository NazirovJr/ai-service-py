"""HTTP-слой для стриминга ответа LLM (Server-Sent Events)."""

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from ai_service_py.client.ollama import stream_llm_response
from ai_service_py.deps import SettingsDep
from ai_service_py.schemes import StreamRequest

router = APIRouter(prefix="/stream", tags=["stream"])


@router.post("", response_class=StreamingResponse)
async def stream_tokens(
    payload: StreamRequest,
    request: Request,
    settings: SettingsDep,
) -> StreamingResponse:
    headers = {
        "Cache-Control": "no-cache, no-transform",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",  # отключает буферизацию в nginx
    }
    return StreamingResponse(
        stream_llm_response(payload.prompt, request, settings),
        headers=headers,
        media_type="text/event-stream",
    )
