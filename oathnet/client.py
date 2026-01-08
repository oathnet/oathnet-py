"""OathNet SDK Client."""

from typing import TYPE_CHECKING, Any

import httpx

from .exceptions import (
    AuthenticationError,
    NotFoundError,
    OathNetError,
    QuotaExceededError,
    RateLimitError,
    ServiceUnavailableError,
    ValidationError,
)

if TYPE_CHECKING:
    from .services.bulk import BulkSearchService
    from .services.exports import ExportsService
    from .services.file_search import FileSearchService
    from .services.osint import OSINTService
    from .services.search import SearchService
    from .services.stealer_v2 import StealerV2Service
    from .services.utility import UtilityService
    from .services.victims import VictimsService


class OathNetClient:
    """OathNet API Client.

    Args:
        api_key: Your OathNet API key
        base_url: API base URL (default: https://oathnet.org/api)
        timeout: Request timeout in seconds (default: 30)

    Example:
        >>> client = OathNetClient("your-api-key")
        >>> results = client.search.breach("user@example.com")
        >>> print(f"Found {results.data.results_found} results")
    """

    DEFAULT_BASE_URL = "https://oathnet.org/api"
    DEFAULT_TIMEOUT = 30.0

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        if not api_key:
            raise ValueError("API key is required")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        self._http_client = httpx.Client(
            base_url=self.base_url,
            headers={"x-api-key": self.api_key},
            timeout=self.timeout,
        )

        # Service instances (lazy loaded)
        self._search: "SearchService | None" = None
        self._stealer: "StealerV2Service | None" = None
        self._victims: "VictimsService | None" = None
        self._file_search: "FileSearchService | None" = None
        self._exports: "ExportsService | None" = None
        self._osint: "OSINTService | None" = None
        self._bulk: "BulkSearchService | None" = None
        self._utility: "UtilityService | None" = None

    def close(self) -> None:
        """Close the HTTP client."""
        self._http_client.close()

    def __enter__(self) -> "OathNetClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path (e.g., /service/search-breach)
            params: Query parameters
            json: JSON body for POST requests

        Returns:
            Response data as dictionary

        Raises:
            AuthenticationError: Invalid or missing API key
            ValidationError: Invalid request parameters
            NotFoundError: Resource not found
            QuotaExceededError: Daily quota exceeded
            RateLimitError: Rate limit exceeded
            OathNetError: Other API errors
        """
        # Clean params
        if params:
            params = {k: v for k, v in params.items() if v is not None}

        try:
            response = self._http_client.request(
                method=method,
                url=path,
                params=params,
                json=json,
            )
        except httpx.TimeoutException as e:
            raise OathNetError(f"Request timed out: {e}")
        except httpx.RequestError as e:
            raise OathNetError(f"Request failed: {e}")

        return self._handle_response(response)

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Handle API response and raise appropriate exceptions."""
        # Handle binary responses (archives, downloads)
        content_type = response.headers.get("content-type", "")
        if "application/zip" in content_type or "application/octet-stream" in content_type:
            # Return raw bytes wrapped in a dict
            return {"_raw_bytes": response.content}

        # Parse JSON response
        try:
            data = response.json()
        except Exception:
            if response.status_code >= 400:
                raise OathNetError(
                    f"HTTP {response.status_code}: {response.text}",
                    response_data={},
                )
            # For non-JSON successful responses
            return {"_raw_text": response.text}

        # Check for API-level errors
        if response.status_code == 401:
            message = data.get("message", "Invalid API key")
            raise AuthenticationError(message, response_data=data)

        if response.status_code == 403:
            message = data.get("message", "Access forbidden")
            # Check if it's a quota error
            if "quota" in message.lower():
                meta = data.get("data", {}).get("_meta", {}).get("lookups", {})
                raise QuotaExceededError(
                    message,
                    used_today=meta.get("used_today", 0),
                    daily_limit=meta.get("daily_limit", 0),
                    response_data=data,
                )
            raise OathNetError(message, response_data=data)

        if response.status_code == 404:
            message = data.get("message", "Not found")
            raise NotFoundError(message, response_data=data)

        if response.status_code == 429:
            message = data.get("message", "Rate limit exceeded")
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                message,
                retry_after=int(retry_after) if retry_after else None,
                response_data=data,
            )

        if response.status_code == 503:
            message = data.get("message", "Service unavailable")
            raise ServiceUnavailableError(message, response_data=data)

        if response.status_code >= 400:
            message = data.get("message", f"HTTP {response.status_code}")
            errors = data.get("errors", {})

            # Check for auth errors that may come as 400
            if "credentials" in message.lower() or "api key" in message.lower():
                raise AuthenticationError(message, response_data=data)

            if response.status_code == 400:
                raise ValidationError(message, errors=errors, response_data=data)
            raise OathNetError(message, response_data=data)

        # Check for success field in response
        if isinstance(data, dict) and data.get("success") is False:
            message = data.get("message", "Request failed")
            errors = data.get("errors", {})

            # Check for specific error types
            error_msg = errors.get("error", "") if isinstance(errors, dict) else ""
            if "not found" in message.lower() or "not found" in error_msg.lower():
                raise NotFoundError(message, response_data=data)
            if "required" in message.lower():
                raise ValidationError(message, errors=errors, response_data=data)
            if "invalid" in message.lower() and "api key" in message.lower():
                raise AuthenticationError(message, response_data=data)

            # Generic error
            raise OathNetError(message, response_data=data)

        return data

    def get(
        self, path: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Make a GET request."""
        return self._request("GET", path, params=params)

    def post(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a POST request."""
        return self._request("POST", path, params=params, json=json)

    def get_raw(self, path: str, params: dict[str, Any] | None = None) -> bytes:
        """Make a GET request and return raw bytes."""
        if params:
            params = {k: v for k, v in params.items() if v is not None}

        response = self._http_client.get(path, params=params)

        if response.status_code >= 400:
            self._handle_response(response)

        return response.content

    # ============================================
    # SERVICE ACCESSORS
    # ============================================

    @property
    def search(self) -> "SearchService":
        """Search service for breach and stealer queries."""
        if self._search is None:
            from .services.search import SearchService

            self._search = SearchService(self)
        return self._search

    @property
    def stealer(self) -> "StealerV2Service":
        """V2 Stealer search service."""
        if self._stealer is None:
            from .services.stealer_v2 import StealerV2Service

            self._stealer = StealerV2Service(self)
        return self._stealer

    @property
    def victims(self) -> "VictimsService":
        """V2 Victims service for victim profiles and files."""
        if self._victims is None:
            from .services.victims import VictimsService

            self._victims = VictimsService(self)
        return self._victims

    @property
    def file_search(self) -> "FileSearchService":
        """V2 File search service for searching within victim files."""
        if self._file_search is None:
            from .services.file_search import FileSearchService

            self._file_search = FileSearchService(self)
        return self._file_search

    @property
    def exports(self) -> "ExportsService":
        """V2 Exports service for exporting search results."""
        if self._exports is None:
            from .services.exports import ExportsService

            self._exports = ExportsService(self)
        return self._exports

    @property
    def osint(self) -> "OSINTService":
        """OSINT service for platform lookups."""
        if self._osint is None:
            from .services.osint import OSINTService

            self._osint = OSINTService(self)
        return self._osint

    @property
    def bulk(self) -> "BulkSearchService":
        """Bulk search service for batch queries."""
        if self._bulk is None:
            from .services.bulk import BulkSearchService

            self._bulk = BulkSearchService(self)
        return self._bulk

    @property
    def utility(self) -> "UtilityService":
        """Utility service for autocomplete and helpers."""
        if self._utility is None:
            from .services.utility import UtilityService

            self._utility = UtilityService(self)
        return self._utility
