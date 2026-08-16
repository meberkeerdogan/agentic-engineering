"""Progress calculations for roadmap items."""

from roadmap import completed_item_ids


def completed_count(items: list[dict]) -> int:
    """Return the number of completed items."""

    return len(completed_item_ids(items))
