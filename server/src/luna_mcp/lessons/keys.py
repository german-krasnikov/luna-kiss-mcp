"""Stable hash keys for typemap-aware lesson lookup."""
import hashlib


def class_hash(js_class_name: str) -> str:
    """Stable 16-char identifier per class name. Hides project-specific names."""
    return hashlib.sha256(js_class_name.encode()).hexdigest()[:16]


def sig_hash(class_signature: dict) -> str:
    """8-char hash of sorted methods + fields. Detects renames/removals."""
    methods = sorted(class_signature.get("methods", []))
    fields = sorted(class_signature.get("fields", []))
    canonical = "|".join(methods) + "##" + "|".join(fields)
    return hashlib.sha256(canonical.encode()).hexdigest()[:8]


def make_key(js_class_name: str, signature: dict, typemap_version: str = "") -> tuple:
    return class_hash(js_class_name), sig_hash(signature), typemap_version
