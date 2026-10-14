"""API-тесты: проверяют HTTP-контракт, а не алгоритмы."""

import httpx


async def test_health_check(api_client: httpx.AsyncClient) -> None:
    response = await api_client.get("/health/check")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"]


async def test_chunk_returns_chunks(api_client: httpx.AsyncClient) -> None:
    response = await api_client.post(
        "/api/v1/chunker",
        json={"text": "a b c d e f g h i j", "chunk_size": 4, "overlap": 1},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["count"] == len(body["chunks"])
    assert body["count"] > 1


async def test_chunk_rejects_overlap_ge_chunk_size(api_client: httpx.AsyncClient) -> None:
    response = await api_client.post(
        "/api/v1/chunker",
        json={"text": "abcdef", "chunk_size": 4, "overlap": 4},
    )
    assert response.status_code == 422
    assert "overlap" in response.text


async def test_chunk_rejects_empty_text(api_client: httpx.AsyncClient) -> None:
    response = await api_client.post("/api/v1/chunker", json={"text": ""})
    assert response.status_code == 422


async def test_chunk_rejects_unknown_field(api_client: httpx.AsyncClient) -> None:
    # extra="forbid" в ChunkRequest
    response = await api_client.post(
        "/api/v1/chunker",
        json={"text": "abc", "unexpected": 1},
    )
    assert response.status_code == 422


async def test_openapi_contains_routes(api_client: httpx.AsyncClient) -> None:
    response = await api_client.get("/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/health/check" in paths
    assert "/api/v1/chunker" in paths
    assert "/api/v1/fetch/all" in paths
    assert "/api/v1/stream" in paths
