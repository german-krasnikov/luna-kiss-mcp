"""Pure data + utility functions for CDP domains. No class/state."""

NETWORK_PRESETS: dict[str, dict] = {
    "online": {"offline": False, "latency": 0, "download": -1, "upload": -1},
    "offline": {"offline": True, "latency": 0, "download": 0, "upload": 0},
    "slow": {"offline": False, "latency": 400, "download": 400_000, "upload": 400_000},
    "3g": {"offline": False, "latency": 400, "download": 400_000, "upload": 400_000},
    "4g": {"offline": False, "latency": 70, "download": 4_000_000, "upload": 3_000_000},
}


def offset_to_line(source: str, offset: int) -> int:
    """Return 1-based line number for byte offset in source."""
    return source.count("\n", 0, offset) + 1


def truncate_lines(lines: list, n: int) -> list:
    """Cap list to n entries; append '... (+K more)' line if truncated."""
    if len(lines) <= n:
        return lines
    extra = len(lines) - n
    return lines[:n] + [f"... (+{extra} more)"]
