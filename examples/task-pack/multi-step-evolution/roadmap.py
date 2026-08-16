"""Small roadmap helpers used by the evolution fixture."""


def item_ids(items: list[dict]) -> list[str]:
    """Return item IDs in their declared order."""

    return [item["id"] for item in items]


def completed_item_ids(items: list[dict]) -> list[str]:
    """Return completed item IDs in their declared order."""

    return [item["id"] for item in items if item["status"] == "completed"]
