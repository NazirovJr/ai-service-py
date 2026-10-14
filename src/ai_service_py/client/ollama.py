"""Клиент Ollama: стриминг ответа модели в формате Server-Sent Events."""

import asyncio
import json
import logging
from collections.abc import AsyncIterator

import ollama
from fastapi import Request

from ai_service_py.config import Settings

logger = logging.getLogger(__name__)


def _sse(event: str, data: dict[str, object]) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


async def stream_llm_response(
    prompt: str,
    request: Request,
    settings: Settings,
) -> AsyncIterator[str]:
    client = ollama.AsyncClient(host=settings.llm_base_url)

    try:
        yield _sse("status", {"status": "connected"})

        response = await client.chat(
            model=settings.llm_model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )

        async for item in response:
            if await request.is_disconnected():
                logger.info("Клиент отключился, прерываем стрим")
                return

            text_chunk = item["message"]["content"]
            if not text_chunk:
                continue
            yield _sse("token", {"text": text_chunk, "type": "token"})

        yield _sse("status", {"status": "finished"})

    except asyncio.CancelledError:
        logger.info("Стрим отменён")
        raise
    except Exception:
        logger.exception("Ошибка стрима LLM")
        yield _sse("error", {"message": "internal error"})
