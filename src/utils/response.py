from typing import Any, Optional


def envelope(data: Any = None, error: Optional[str] = None) -> dict[str, Any]:
    """Standard API response envelope used by every endpoint."""
    return {"data": data, "error": error}
