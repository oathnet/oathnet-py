"""Search Service - Breach and Stealer search endpoints."""

from typing import TYPE_CHECKING

from ..models import (
    BreachSearchResponse,
    SearchSessionResponse,
    StealerSearchResponse,
)

if TYPE_CHECKING:
    from ..client import OathNetClient


class SearchService:
    """Service for search operations.

    Includes search session initialization, breach search, and legacy stealer search.
    """

    def __init__(self, client: "OathNetClient"):
        self._client = client

    def init_session(self, query: str) -> SearchSessionResponse:
        """Initialize a search session.

        Creates a new search session for a given query. Returns session info
        with available services and quota information.

        Args:
            query: The search query (email, username, domain, etc.)

        Returns:
            SearchSessionResponse with session ID and service availability

        Example:
            >>> session = client.search.init_session("user@example.com")
            >>> print(f"Session ID: {session.data.session.id}")
        """
        data = self._client.post(
            "/service/search/init",
            json={"query": query},
        )
        return SearchSessionResponse.model_validate(data)

    def breach(
        self,
        q: str,
        cursor: str | None = None,
        dbnames: str | list[str] | None = None,
        search_id: str | None = None,
    ) -> BreachSearchResponse:
        """Search breach database.

        Searches across breach databases for leaked credentials and data.

        Args:
            q: Search query (email, username, domain, etc.)
            cursor: Pagination cursor from previous response
            dbnames: Filter to specific breach databases (comma-separated or list)
            search_id: Search session ID from init_session()

        Returns:
            BreachSearchResponse with results and pagination cursor

        Example:
            >>> results = client.search.breach("winterfox")
            >>> for result in results.data.results:
            ...     print(f"{result.email} from {result.dbname}")
        """
        params = {
            "q": q,
            "cursor": cursor,
            "search_id": search_id,
        }

        # Handle dbnames as comma-separated string or list
        if dbnames:
            if isinstance(dbnames, list):
                params["dbnames"] = ",".join(dbnames)
            else:
                params["dbnames"] = dbnames

        data = self._client.get("/service/search-breach", params=params)
        return BreachSearchResponse.model_validate(data)

    def stealer(
        self,
        q: str,
        cursor: str | None = None,
        dbnames: str | None = None,
        search_id: str | None = None,
    ) -> StealerSearchResponse:
        """Search stealer database (legacy endpoint).

        Searches stealer log databases for credential entries.

        Args:
            q: Search query
            cursor: Pagination cursor from previous response
            dbnames: Filter to specific databases
            search_id: Search session ID from init_session()

        Returns:
            StealerSearchResponse with results containing LOG field

        Example:
            >>> results = client.search.stealer("diddy")
            >>> for result in results.data.results:
            ...     print(result.LOG)
        """
        params = {
            "q": q,
            "cursor": cursor,
            "dbnames": dbnames,
            "search_id": search_id,
        }

        data = self._client.get("/service/search-stealer", params=params)
        return StealerSearchResponse.model_validate(data)

    def breach_paginate(
        self,
        q: str,
        dbnames: str | list[str] | None = None,
        search_id: str | None = None,
        max_pages: int | None = None,
    ):
        """Iterate through all breach search results.

        Generator that automatically handles pagination.

        Args:
            q: Search query
            dbnames: Filter to specific databases
            search_id: Search session ID
            max_pages: Maximum number of pages to fetch (None for all)

        Yields:
            BreachResult objects

        Example:
            >>> for result in client.search.breach_paginate("example.com"):
            ...     print(result.email)
        """
        cursor = None
        page = 0

        while True:
            response = self.breach(
                q=q,
                cursor=cursor,
                dbnames=dbnames,
                search_id=search_id,
            )

            if not response.data or not response.data.results:
                break

            for result in response.data.results:
                yield result

            cursor = response.data.cursor
            if not cursor:
                break

            page += 1
            if max_pages and page >= max_pages:
                break

    def stealer_paginate(
        self,
        q: str,
        dbnames: str | None = None,
        search_id: str | None = None,
        max_pages: int | None = None,
    ):
        """Iterate through all stealer search results.

        Generator that automatically handles pagination.

        Args:
            q: Search query
            dbnames: Filter to specific databases
            search_id: Search session ID
            max_pages: Maximum number of pages to fetch (None for all)

        Yields:
            StealerResult objects
        """
        cursor = None
        page = 0

        while True:
            response = self.stealer(
                q=q,
                cursor=cursor,
                dbnames=dbnames,
                search_id=search_id,
            )

            if not response.data or not response.data.results:
                break

            for result in response.data.results:
                yield result

            cursor = response.data.cursor
            if not cursor:
                break

            page += 1
            if max_pages and page >= max_pages:
                break
