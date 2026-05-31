"""Centralized configuration helpers."""
from __future__ import annotations
import os
import pathlib


def data_dir() -> pathlib.Path:
    return pathlib.Path(os.environ.get("LUNA_MCP_DATA_DIR", str(pathlib.Path.home() / ".luna_mcp")))
