"""Utility Service - Autocomplete and helper endpoints."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import OathNetClient


class UtilityService:
    """Service for utility operations.

    Includes database name autocomplete and other helpers.
    """

    def __init__(self, client: "OathNetClient"):
        self._client = client

    def dbname_autocomplete(self, q: str) -> list[str]:
        """Get database name autocomplete suggestions.

        Returns matching database names for the given query.

        Args:
            q: Partial database name to search

        Returns:
            List of matching database names

        Example:
            >>> suggestions = client.utility.dbname_autocomplete("linked")
            >>> print(suggestions)  # ["linkedin_2012", "linkedin_2021", ...]
        """
        data = self._client.get(
            "/service/dbname-autocomplete",
            params={"q": q},
        )

        # Response is a direct array, not wrapped
        if isinstance(data, list):
            return data

        # Handle case where it might be wrapped
        if isinstance(data, dict) and "data" in data:
            return data["data"]

        return []
