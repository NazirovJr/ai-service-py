"""Pydantic-модели HTTP-контракта."""

from enum import StrEnum
from typing import Annotated, Self

from annotated_types import Ge
from pydantic import BaseModel, ConfigDict, Field, model_validator


class Route(StrEnum):
    KNOWLEDGE = "KNOWLEDGE"
    ORDER = "ORDER"
    SMALLTALK = "SMALLTALK"


class Classification(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    route: Route
    reason: str


class AgentReply(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    route: Route
    reason: str
    answer: Annotated[str, Field(min_length=1)]
    sources: list[str] = Field(default_factory=list)
    total_tokens: Annotated[int, Ge(0)]


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: float


class ChunkRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: Annotated[str, Field(min_length=1, max_length=1_000_000)]
    chunk_size: Annotated[int, Field(gt=0, le=10_000)] = 500
    overlap: Annotated[int, Field(ge=0)] = 50

    @model_validator(mode="after")
    def overlap_less_than_chunk_size(self) -> Self:
        if self.overlap >= self.chunk_size:
            raise ValueError("overlap должен быть строго меньше chunk_size")
        return self


class ChunkResponse(BaseModel):
    chunks: list[str]
    count: int


class FetchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    urls: Annotated[list[str], Field(min_length=1, max_length=50)]


class FetchResponse(BaseModel):
    bodies: list[str]
    requested: int
    succeeded: int


class StreamRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompt: Annotated[str, Field(min_length=1, max_length=10_000)]
