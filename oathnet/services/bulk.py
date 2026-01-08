"""Bulk Search Service - Batch search operations."""

import time
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from ..models import (
    BulkSearchCreateResponse,
    BulkSearchListResponse,
    BulkSearchStatusResponse,
)

if TYPE_CHECKING:
    from ..client import OathNetClient


class BulkSearchService:
    """Service for bulk search operations.

    Perform batch searches with multiple terms at once.
    Bulk search is asynchronous - create a job, poll for completion, then download.
    """

    def __init__(self, client: "OathNetClient"):
        self._client = client

    def create(
        self,
        terms: list[str],
        service: Literal["breach", "stealer"],
        format: Literal["json", "csv"] = "json",
        dbnames: list[str] | None = None,
    ) -> BulkSearchCreateResponse:
        """Create a bulk search job.

        Creates a bulk search job for multiple terms.

        Args:
            terms: List of search terms
            service: Search service ("breach" or "stealer")
            format: Output format ("json" or "csv")
            dbnames: Filter to specific databases

        Returns:
            BulkSearchCreateResponse with job ID

        Example:
            >>> job = client.bulk.create(
            ...     terms=["user1@example.com", "user2@example.com"],
            ...     service="breach"
            ... )
            >>> print(f"Job ID: {job.data.id}")
        """
        body = {
            "terms": terms,
            "service": service,
            "format": format,
        }

        if dbnames:
            body["dbnames"] = dbnames

        data = self._client.post("/service/bulk-search", json=body)
        return BulkSearchCreateResponse.model_validate(data)

    def get_status(self, job_id: str) -> BulkSearchStatusResponse:
        """Get bulk search job status.

        Args:
            job_id: Job ID from create()

        Returns:
            BulkSearchStatusResponse with status

        Example:
            >>> status = client.bulk.get_status("job_abc")
            >>> print(f"Status: {status.data.status}")
        """
        data = self._client.get(f"/service/bulk-search/{job_id}/status")
        return BulkSearchStatusResponse.model_validate(data)

    def list_jobs(
        self, page: int = 1, page_size: int = 10
    ) -> BulkSearchListResponse:
        """List bulk search jobs.

        Args:
            page: Page number (default 1)
            page_size: Results per page (default 10)

        Returns:
            BulkSearchListResponse with job list

        Example:
            >>> jobs = client.bulk.list_jobs()
            >>> for job in jobs.results:
            ...     print(f"{job.id}: {job.status}")
        """
        data = self._client.get(
            "/service/bulk-search/list",
            params={"page": page, "page_size": page_size},
        )
        return BulkSearchListResponse.model_validate(data)

    def download(
        self, job_id: str, output_path: str | Path | None = None
    ) -> bytes | Path:
        """Download bulk search results.

        Args:
            job_id: Job ID of completed bulk search
            output_path: Path to save results (optional)

        Returns:
            bytes if no output_path, Path to saved file otherwise

        Example:
            >>> path = client.bulk.download("job_abc", "results.json")
        """
        raw_bytes = self._client.get_raw(
            "/service/bulk-search/download",
            params={"job_id": job_id},
        )

        if output_path:
            path = Path(output_path)
            path.write_bytes(raw_bytes)
            return path

        return raw_bytes

    def wait_for_completion(
        self,
        job_id: str,
        poll_interval: float = 2.0,
        timeout: float = 600.0,
    ) -> BulkSearchStatusResponse:
        """Wait for bulk search job to complete.

        Args:
            job_id: Job ID from create()
            poll_interval: Seconds between status checks
            timeout: Maximum seconds to wait

        Returns:
            BulkSearchStatusResponse with final status

        Raises:
            TimeoutError: If job doesn't complete within timeout
        """
        start_time = time.time()

        while True:
            response = self.get_status(job_id)
            status = response.data.status if response.data else None

            if status in ("COMPLETED", "FAILED"):
                return response

            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(
                    f"Bulk search job {job_id} did not complete within {timeout}s"
                )

            time.sleep(poll_interval)

    def search(
        self,
        terms: list[str],
        service: Literal["breach", "stealer"],
        format: Literal["json", "csv"] = "json",
        output_path: str | Path | None = None,
        timeout: float = 600.0,
        **kwargs,
    ) -> bytes | Path:
        """Create bulk search, wait, and download results.

        All-in-one convenience method for bulk searching.

        Args:
            terms: List of search terms
            service: Search service ("breach" or "stealer")
            format: Output format ("json" or "csv")
            output_path: Path to save results (optional)
            timeout: Maximum seconds to wait
            **kwargs: Additional create() parameters

        Returns:
            bytes if no output_path, Path to saved file otherwise

        Example:
            >>> results = client.bulk.search(
            ...     terms=["user1@test.com", "user2@test.com"],
            ...     service="breach",
            ...     output_path="bulk_results.json"
            ... )
        """
        job = self.create(terms=terms, service=service, format=format, **kwargs)
        self.wait_for_completion(job.data.id, timeout=timeout)
        return self.download(job.data.id, output_path)
