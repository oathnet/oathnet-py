"""OathNet SDK Utilities."""

from typing import Any


def clean_params(params: dict[str, Any]) -> dict[str, Any]:
    """Remove None values from params dict."""
    return {k: v for k, v in params.items() if v is not None}


def handle_array_params(params: dict[str, Any]) -> dict[str, Any]:
    """Convert list params to proper format for V2 endpoints.

    V2 endpoints use domain[], email[], etc. format.
    """
    result = {}
    for key, value in params.items():
        if value is None:
            continue
        if isinstance(value, list) and key.endswith("[]"):
            # Already has [] suffix, keep as-is
            result[key] = value
        elif isinstance(value, list):
            # Add [] suffix for array params
            result[f"{key}[]"] = value
        else:
            result[key] = value
    return result
