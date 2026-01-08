"""Stealer V2 Service - Enhanced stealer search with advanced filtering."""

from typing import TYPE_CHECKING

from ..models import SubdomainResponse, V2StealerResponse

if TYPE_CHECKING:
    from ..client import OathNetClient


class StealerV2Service:
    """Service for V2 stealer search operations.

    Enhanced stealer search with advanced filtering and pagination.
    """

    def __init__(self, client: "OathNetClient"):
        self._client = client

    def search(
        self,
        q: str | None = None,
        cursor: str | None = None,
        page_size: int = 25,
        sort: str | None = None,
        wildcard: bool = False,
        log_id: str | None = None,
        has_log_id: bool | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        domain: list[str] | None = None,
        subdomain: list[str] | None = None,
        username: list[str] | None = None,
        password: list[str] | None = None,
        path: list[str] | None = None,
        fields: list[str] | None = None,
        search_id: str | None = None,
    ) -> V2StealerResponse:
        """Search V2 stealer database.

        Enhanced stealer search with advanced filtering. Returns credential
        documents with associated victim log IDs.

        Args:
            q: Search query (optional if using filters)
            cursor: Pagination cursor from previous response
            page_size: Results per page (1-100, default 25)
            sort: Sort field (prefix with - for descending)
            wildcard: Enable wildcard matching
            log_id: Filter to specific victim log ID
            has_log_id: Only return results with associated logs
            from_date: Start date (ISO 8601)
            to_date: End date (ISO 8601)
            domain: Filter by domain(s)
            subdomain: Filter by subdomain(s)
            username: Filter by username(s)
            password: Filter by password(s)
            path: Filter by URL path(s)
            fields: Select specific fields to return
            search_id: Search session ID

        Returns:
            V2StealerResponse with items and pagination

        Example:
            >>> results = client.stealer.search(q="gmail.com")
            >>> for item in results.data.items:
            ...     print(f"{item.username}:{item.password}")
        """
        params = {
            "q": q,
            "cursor": cursor,
            "page_size": page_size,
            "sort": sort,
            "wildcard": wildcard if wildcard else None,
            "log_id": log_id,
            "has_log_id": has_log_id,
            "from": from_date,
            "to": to_date,
            "search_id": search_id,
        }

        # Handle array parameters with [] suffix
        if domain:
            params["domain[]"] = domain
        if subdomain:
            params["subdomain[]"] = subdomain
        if username:
            params["username[]"] = username
        if password:
            params["password[]"] = password
        if path:
            params["path[]"] = path
        if fields:
            params["fields[]"] = fields

        data = self._client.get("/service/v2/stealer/search", params=params)
        return V2StealerResponse.model_validate(data)

    def subdomain(
        self,
        domain: str,
        q: str | None = None,
    ) -> SubdomainResponse:
        """Extract subdomains from stealer data.

        Extracts unique subdomains found in stealer logs for a given domain.

        Args:
            domain: Domain to search for subdomains
            q: Additional query filter

        Returns:
            SubdomainResponse with list of subdomains

        Example:
            >>> result = client.stealer.subdomain("google.com")
            >>> print(result.data.subdomains)
        """
        data = self._client.get(
            "/service/v2/stealer/subdomain",
            params={"domain": domain, "q": q},
        )
        return SubdomainResponse.model_validate(data)

    def search_paginate(
        self,
        q: str | None = None,
        page_size: int = 25,
        max_pages: int | None = None,
        **kwargs,
    ):
        """Iterate through all V2 stealer search results.

        Generator that automatically handles pagination.

        Args:
            q: Search query
            page_size: Results per page
            max_pages: Maximum pages to fetch (None for all)
            **kwargs: Additional search parameters

        Yields:
            V2StealerItem objects

        Example:
            >>> for item in client.stealer.search_paginate(q="facebook.com"):
            ...     print(f"{item.log_id}: {item.username}")
        """
        cursor = None
        page = 0

        while True:
            response = self.search(
                q=q,
                cursor=cursor,
                page_size=page_size,
                **kwargs,
            )

            if not response.data or not response.data.items:
                break

            for item in response.data.items:
                yield item

            cursor = response.data.next_cursor
            if not cursor:
                break

            page += 1
            if max_pages and page >= max_pages:
                break
