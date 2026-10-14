"""Тесты Pydantic-моделей агента поддержки.

Заведомо невалидные данные подаём через model_validate(dict), а не через
конструктор: именно так данные и приходят от LLM (JSON → dict), и статический
анализатор не мешает проверять то, что должно падать в рантайме.
"""

from typing import Any

import pytest
from pydantic import ValidationError

from ai_service_py.schemes import AgentReply, Classification, Route


def test_agent_reply_correct_object() -> None:
    reply = AgentReply(
        route=Route.ORDER,
        reason="Testing",
        answer="It is testing answer",
        sources=["[1]Test", "[2]Test"],
        total_tokens=3,
    )
    assert reply.answer == "It is testing answer"
    assert reply.sources == ["[1]Test", "[2]Test"]
    assert reply.total_tokens == 3
    assert reply.route == Route.ORDER
    assert reply.reason == "Testing"


def test_agent_reply_lt_zero() -> None:
    with pytest.raises(ValidationError):
        AgentReply(
            route=Route.ORDER,
            reason="Testing",
            answer="It is testing answer",
            sources=["[1]Test", "[2]Test"],
            total_tokens=-3,
        )


def test_agent_reply_eq_zero() -> None:
    agent_obj = AgentReply(
        route=Route.ORDER,
        reason="Testing",
        answer="It is testing answer",
        sources=["[1]Test", "[2]Test"],
        total_tokens=0,
    )

    assert agent_obj.total_tokens == 0


def test_agent_reply_more_field() -> None:
    payload: dict[str, Any] = {
        "route": "ORDER",
        "reason": "Testing",
        "answer": "It is testing answer",
        "sources": ["[1]Test", "[2]Test"],
        "total_tokens": 3,
        "not_exists_field": True,
    }
    with pytest.raises(ValidationError):
        AgentReply.model_validate(payload)


def test_agent_json_round_trip_and_coercion() -> None:
    apply_json = """
    {
      "route": "ORDER",
      "reason": "Testing",
      "answer": "It is testing answer",
      "sources": ["[1]Test", "[2]Test"],
      "total_tokens": "3"
    }
    """

    agent = AgentReply.model_validate_json(apply_json)

    assert agent.answer == "It is testing answer"
    assert agent.sources == ["[1]Test", "[2]Test"]
    assert agent.total_tokens == 3
    assert agent.route == Route.ORDER
    assert agent.reason == "Testing"

    agent.sources.append("[3]NewSource")
    agent.total_tokens += 10

    json_string = agent.model_dump_json()

    assert isinstance(json_string, str)
    reparsed_agent = AgentReply.model_validate_json(json_string)
    assert reparsed_agent.sources == ["[1]Test", "[2]Test", "[3]NewSource"]
    assert reparsed_agent.total_tokens == 13
    assert reparsed_agent.route == Route.ORDER
    assert reparsed_agent.reason == "Testing"
    assert reparsed_agent.answer == "It is testing answer"
    assert reparsed_agent == agent


def test_agent_reply_sources_default_field() -> None:
    first_agent = AgentReply(
        route=Route.ORDER, reason="Testing", answer="It is testing answer", total_tokens=3
    )

    assert first_agent.sources == []
    first_agent.sources.append("[1]Test")
    first_agent.sources.append("[2]Test")

    assert first_agent.sources == ["[1]Test", "[2]Test"]

    second_agent = AgentReply(
        route=Route.ORDER, reason="Testing", answer="It is testing answer", total_tokens=3
    )

    assert second_agent.sources == []


def test_agent_reply_answer_lt_length() -> None:
    with pytest.raises(ValidationError):
        AgentReply(
            route=Route.ORDER,
            reason="Testing",
            answer="    ",
            sources=["[1]Test", "[2]Test"],
            total_tokens=3,
        )


def test_agent_reply_invalid_route() -> None:
    # защита от галлюцинации модели: маршрут вне перечисления не пройдёт
    payload: dict[str, Any] = {
        "route": "NOT_EXISTS",
        "reason": "Testing",
        "answer": "It is testing answer",
        "sources": ["[1]Test", "[2]Test"],
        "total_tokens": 3,
    }
    with pytest.raises(ValidationError):
        AgentReply.model_validate(payload)


def test_agent_classification_invalid_route() -> None:
    with pytest.raises(ValidationError):
        Classification.model_validate({"route": "NOT_EXISTS", "reason": "Testing"})


def test_agent_classification_more_field() -> None:
    payload: dict[str, Any] = {
        "route": "ORDER",
        "reason": "Testing",
        "one_more_field": "Hello",
    }
    with pytest.raises(ValidationError):
        Classification.model_validate(payload)


def test_agent_classification_correct_object() -> None:
    cl_obj = Classification(route=Route.ORDER, reason="Testing")

    assert cl_obj.route == Route.ORDER
    assert cl_obj.reason == "Testing"
