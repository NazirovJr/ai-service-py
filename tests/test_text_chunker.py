"""Тесты chunk() — порт TextChunkerTest.java (урок 0.2) на pytest."""

from itertools import pairwise

import pytest

from ai_service_py.domain.text_chunker import chunk

# --- пустой вход ---------------------------------------------------------


@pytest.mark.parametrize("text", [None, "", "   ", "\n\t  \r\n"])
def test_empty_input_returns_empty_list(text: str | None) -> None:
    assert chunk(text, 10, 0) == []


# --- короткий текст ------------------------------------------------------


def test_text_shorter_than_chunk_size_returns_single_chunk() -> None:
    assert chunk("короткий", 100, 0) == ["короткий"]


def test_text_exactly_chunk_size_returns_single_chunk() -> None:
    assert chunk("abcd", 4, 0) == ["abcd"]


# --- нормализация пробелов ----------------------------------------------


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("  a b  ", "a b"),
        ("a\n\n  b", "a b"),
        ("a\t\tb", "a b"),
        ("a   b   c", "a b c"),
        ("\n  много\r\n\tпробелов  \n", "много пробелов"),
    ],
)
def test_whitespace_is_collapsed(raw: str, expected: str) -> None:
    assert chunk(raw, 100, 0) == [expected]


# --- нарезка -------------------------------------------------------------


def test_split_without_overlap() -> None:
    assert chunk("abcdefghij", 4, 0) == ["abcd", "efgh", "ij"]


def test_split_with_overlap() -> None:
    assert chunk("abcdefghij", 4, 1) == ["abcd", "defg", "ghij"]


def test_exact_division_has_no_trailing_duplicate() -> None:
    # 10 символов, шаг 5 — делится нацело, лишнего куска быть не должно
    assert chunk("abcdefghij", 5, 0) == ["abcde", "fghij"]


def test_no_empty_chunks() -> None:
    result = chunk("abcdefghijklmnop", 5, 2)
    assert all(result), f"пустой кусок в результате: {result}"


def test_no_data_loss() -> None:
    # при overlap=0 склейка кусков должна вернуть исходный текст
    text = "abcdefghijklmnop"
    assert "".join(chunk(text, 5, 0)) == text


def test_overlap_is_respected() -> None:
    chunks = chunk("abcdefghij", 4, 1)
    for prev, nxt in pairwise(chunks):
        assert prev[-1:] == nxt[:1]


# --- валидация -----------------------------------------------------------


@pytest.mark.parametrize("chunk_size", [0, -1, -100])
def test_non_positive_chunk_size_raises(chunk_size: int) -> None:
    with pytest.raises(ValueError):
        chunk("текст", chunk_size, 0)


@pytest.mark.parametrize("overlap", [-1, -10])
def test_negative_overlap_raises(overlap: int) -> None:
    with pytest.raises(ValueError):
        chunk("текст", 10, overlap)


@pytest.mark.parametrize("overlap", [10, 11])
def test_overlap_not_less_than_chunk_size_raises(overlap: int) -> None:
    # step <= 0 → окно не двигается → бесконечный цикл
    with pytest.raises(ValueError):
        chunk("текст", 10, overlap)


def test_validation_runs_before_none_check() -> None:
    # кривые параметры — ошибка программиста, она важнее отсутствия данных
    with pytest.raises(ValueError):
        chunk(None, 0, 0)
