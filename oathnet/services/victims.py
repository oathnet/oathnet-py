"""Victims Service - V2 victim profiles and files."""

from pathlib import Path
from typing import TYPE_CHECKING

from ..models import (
    FileContentResponse,
    ManifestResponse,
    V2VictimsResponse,
)

if TYPE_CHECKING:
    from ..client import OathNetClient


class VictimsService:
    """Service for V2 victims operations.

    Search victim profiles and access their files.
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
        from_date: str | None = None,
        to_date: str | None = None,
        total_docs_min: int | None = None,
        total_docs_max: int | None = None,
        email: list[str] | None = None,
        ip: list[str] | None = None,
        hwid: list[str] | None = None,
        discord_id: list[str] | None = None,
        username: list[str] | None = None,
        fields: list[str] | None = None,
        search_id: str | None = None,
    ) -> V2VictimsResponse:
        """Search victim profiles.

        Search for victim profiles (aggregated log metadata). Each victim
        represents a compromised machine with device info, IPs, emails,
        Discord IDs, etc.

        Args:
            q: Search query
            cursor: Pagination cursor
            page_size: Results per page (default 25)
            sort: Sort field (prefix with - for descending)
            wildcard: Enable wildcard matching
            log_id: Filter to specific log ID
            from_date: Start date (ISO 8601)
            to_date: End date (ISO 8601)
            total_docs_min: Minimum document count in log
            total_docs_max: Maximum document count in log
            email: Filter by email(s)
            ip: Filter by IP(s)
            hwid: Filter by hardware ID(s)
            discord_id: Filter by Discord ID(s)
            username: Filter by device username(s)
            fields: Select specific fields to return
            search_id: Search session ID

        Returns:
            V2VictimsResponse with victim items and pagination

        Example:
            >>> results = client.victims.search(q="gmail")
            >>> for victim in results.data.items:
            ...     print(f"{victim.log_id}: {victim.device_emails}")
        """
        params = {
            "q": q,
            "cursor": cursor,
            "page_size": page_size,
            "sort": sort,
            "wildcard": wildcard if wildcard else None,
            "log_id": log_id,
            "from": from_date,
            "to": to_date,
            "total_docs_min": total_docs_min,
            "total_docs_max": total_docs_max,
            "search_id": search_id,
        }

        # Handle array parameters
        if email:
            params["email[]"] = email
        if ip:
            params["ip[]"] = ip
        if hwid:
            params["hwid[]"] = hwid
        if discord_id:
            params["discord_id[]"] = discord_id
        if username:
            params["username[]"] = username
        if fields:
            params["fields[]"] = fields

        data = self._client.get("/service/v2/victims/search", params=params)
        return V2VictimsResponse.model_validate(data)

    def get_manifest(self, log_id: str) -> ManifestResponse:
        """Get victim manifest (file tree).

        Retrieves the complete file tree structure for a victim log.
        Use file IDs from the tree to download individual files.

        Args:
            log_id: Victim log ID

        Returns:
            ManifestResponse with file tree structure

        Example:
            >>> manifest = client.victims.get_manifest("vic_001_user")
            >>> print(manifest.data.victim_tree)
        """
        data = self._client.get(f"/service/v2/victims/{log_id}")
        # API returns unwrapped response, wrap it
        if "success" not in data:
            data = {"success": True, "data": data}
        return ManifestResponse.model_validate(data)

    def get_file(self, log_id: str, file_id: str) -> FileContentResponse:
        """Get victim file content.

        Downloads the content of a specific file from a victim log.

        Args:
            log_id: Victim log ID
            file_id: File ID from the manifest

        Returns:
            FileContentResponse with file content

        Example:
            >>> content = client.victims.get_file("vic_001", "file_abc")
            >>> print(content.data.content)
        """
        data = self._client.get(f"/service/v2/victims/{log_id}/files/{file_id}")
        return FileContentResponse.model_validate(data)

    def download_archive(
        self, log_id: str, output_path: str | Path | None = None
    ) -> bytes | Path:
        """Download victim archive as ZIP.

        Downloads the complete victim log as a ZIP archive.

        Args:
            log_id: Victim log ID
            output_path: Path to save the archive (optional)

        Returns:
            bytes if no output_path, Path to saved file otherwise

        Example:
            >>> # Save to file
            >>> path = client.victims.download_archive("vic_001", "victim.zip")
            >>> # Or get raw bytes
            >>> data = client.victims.download_archive("vic_001")
        """
        raw_bytes = self._client.get_raw(f"/service/v2/victims/{log_id}/archive")

        if output_path:
            path = Path(output_path)
            path.write_bytes(raw_bytes)
            return path

        return raw_bytes

    def search_paginate(
        self,
        q: str | None = None,
        page_size: int = 25,
        max_pages: int | None = None,
        **kwargs,
    ):
        """Iterate through all victim search results.

        Generator that automatically handles pagination.

        Args:
            q: Search query
            page_size: Results per page
            max_pages: Maximum pages to fetch (None for all)
            **kwargs: Additional search parameters

        Yields:
            V2VictimItem objects
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
