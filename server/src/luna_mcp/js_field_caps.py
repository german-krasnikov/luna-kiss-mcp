"""Python mirror of JS readComponentFields caps.

These constants MUST stay in sync with the vars in luna_helpers.js.
"""
FIELD_CAP = 20   # max fields returned per component
VALUE_CAP = 120  # max chars per serialized field value


def truncate_value(val: str) -> str:
    """Truncate val to VALUE_CAP chars, appending ellipsis if cut."""
    if len(val) <= VALUE_CAP:
        return val
    return val[:VALUE_CAP] + "…"


def format_more_marker(count: int) -> str:
    """Return '+K more fields' marker string."""
    return f"+{count} more fields"
