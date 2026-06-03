"""Centralized configuration helpers."""
from __future__ import annotations
import os
import pathlib

SCREENSHOT_FORMAT: str = os.environ.get("LUNA_SCREENSHOT_FORMAT", "jpeg")
SCREENSHOT_QUALITY: int = int(os.environ.get("LUNA_SCREENSHOT_QUALITY", "60"))
SCREENSHOT_MAX_WIDTH: int = int(os.environ.get("LUNA_SCREENSHOT_MAX_WIDTH", "0"))


def data_dir() -> pathlib.Path:
    return pathlib.Path(os.environ.get("LUNA_MCP_DATA_DIR", str(pathlib.Path.home() / ".luna_mcp")))
