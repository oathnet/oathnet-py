"""OathNet SDK Exceptions."""

from typing import Any


class OathNetError(Exception):
    """Base exception for OathNet SDK."""

    def __init__(self, message: str, response_data: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.response_data = response_data or {}

    def __str__(self) -> str:
        return self.message


class AuthenticationError(OathNetError):
    """Raised when API key is invalid or missing (401)."""

    pass


class QuotaExceededError(OathNetError):
    """Raised when daily quota is exhausted."""

    def __init__(
        self,
        message: str,
        used_today: int = 0,
        daily_limit: int = 0,
        response_data: dict[str, Any] | None = None,
    ):
        super().__init__(message, response_data)
        self.used_today = used_today
        self.daily_limit = daily_limit


class NotFoundError(OathNetError):
    """Raised when a resource is not found (404)."""

    pass


class ValidationError(OathNetError):
    """Raised when request parameters are invalid (400)."""

    def __init__(
        self,
        message: str,
        errors: dict[str, Any] | None = None,
        response_data: dict[str, Any] | None = None,
    ):
        super().__init__(message, response_data)
        self.errors = errors or {}


class RateLimitError(OathNetError):
    """Raised when rate limit is exceeded (429)."""

    def __init__(
        self,
        message: str,
        retry_after: int | None = None,
        response_data: dict[str, Any] | None = None,
    ):
        super().__init__(message, response_data)
        self.retry_after = retry_after


class ServiceUnavailableError(OathNetError):
    """Raised when a service is temporarily unavailable (503)."""

    pass
