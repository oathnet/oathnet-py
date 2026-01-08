"""OathNet SDK - Official Python client for OathNet API.

Example:
    >>> from oathnet import OathNetClient
    >>> client = OathNetClient("your-api-key")
    >>> results = client.search.breach("user@example.com")
    >>> print(f"Found {results.data.results_found} results")
"""

from .client import OathNetClient
from .exceptions import (
    AuthenticationError,
    NotFoundError,
    OathNetError,
    QuotaExceededError,
    RateLimitError,
    ServiceUnavailableError,
    ValidationError,
)

__version__ = "1.0.1"
__all__ = [
    "OathNetClient",
    "OathNetError",
    "AuthenticationError",
    "QuotaExceededError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "ServiceUnavailableError",
]
