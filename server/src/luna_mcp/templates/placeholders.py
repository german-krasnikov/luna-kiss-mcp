"""Placeholder engine: {{var}} and {{var|default}} substitution."""
import re
import shlex

_RE = re.compile(r'\{\{\s*(\w+)(?:\s*\|\s*([^}]+?))?\s*\}\}')
_NEEDS_QUOTE_CHARS = set(' \t"\'\\')


class PlaceholderError(Exception):
    pass


def _quote_if_needed(v: str) -> str:
    if not v or any(c in v for c in _NEEDS_QUOTE_CHARS):
        return shlex.quote(v)
    return v


def expand(template_text: str, kwargs: dict) -> str:
    """Substitute {{var}} or {{var|default}}. Raises PlaceholderError if unresolved."""
    def _sub(m):
        name = m.group(1)
        default = m.group(2)
        if name in kwargs:
            value = str(kwargs[name])
        elif default is not None:
            value = default.strip()
        else:
            raise PlaceholderError(f"missing required arg: {name}")
        if "\n" in value:
            raise PlaceholderError(f"value for '{name}' contains newline")
        return _quote_if_needed(value)
    return _RE.sub(_sub, template_text)


def parse_args(args_str: str) -> dict:
    """Parse 'key=value key=value' (shlex-aware for quoted values)."""
    out = {}
    for part in shlex.split(args_str):
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        out[k.strip()] = v.strip()
    return out
