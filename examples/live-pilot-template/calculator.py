"""Small deterministic fixture for a private coding-agent pilot."""


def median(values: list[float]) -> float:
    """Return the median without mutating the input."""

    if not values:
        raise ValueError("median requires at least one value")
    ordered = sorted(values)
    middle = len(ordered) // 2
    return ordered[middle]
