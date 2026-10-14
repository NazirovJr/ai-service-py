"""HTTP-слой для чанкинга."""

from fastapi import APIRouter, status

from ai_service_py.domain.text_chunker import chunk
from ai_service_py.schemes import ChunkRequest, ChunkResponse

router = APIRouter(prefix="/chunker", tags=["chunking"])


@router.post(
    "",
    response_model=ChunkResponse,
    status_code=status.HTTP_200_OK,
    summary="Разбить текст на куски с перекрытием",
    responses={422: {"description": "overlap >= chunk_size или пустой текст"}},
)
async def create_chunks(payload: ChunkRequest) -> ChunkResponse:
    chunks = chunk(payload.text, payload.chunk_size, payload.overlap)
    return ChunkResponse(chunks=chunks, count=len(chunks))
