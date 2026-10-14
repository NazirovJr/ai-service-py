import re


def chunk(text: str | None, chunk_size: int, overlap: int) -> list[str]:
    """
    Режет текст на куски.
    Args:
        text: исходный текст, может быть None.
        chunk_size: размер куска в символах.
        overlap: Наложение

    Returns:
        Список кусков; пустой список для None или пустого текста.

    Raises:
        ValueError: если chunk_size <= 0 или overlap < 0 или chunk_size <= overlap.
    """

    if overlap < 0:
        raise ValueError(f"chunk size {chunk_size} must be > 0 and overlap {overlap} >= 0")

    if chunk_size <= overlap:
        raise ValueError(f"chunk size {chunk_size} must be > overlap {overlap}")

    if text is None:
        return []

    text = text.strip()
    normalized = re.sub(r"\s+", " ", text)

    if len(normalized) == 0:
        return []

    if len(normalized) <= chunk_size:
        return [normalized]

    result: list[str] = []
    start: int = 0
    step: int = chunk_size - overlap
    while start < len(normalized):
        result.append(normalized[start : chunk_size + start])

        if start + chunk_size >= len(normalized):
            break

        start += step

    return result
