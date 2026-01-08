"""Exports Service - V2 async export to JSONL or CSV."""

import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from ..models import ExportJobData, ExportJobResponse

if TYPE_CHECKING:
    from ..client import OathNetClient


class ExportsService:
    """Service for V2 export operations.

    Export search results to JSONL or CSV format.
    Exports are asynchronous - create a job, poll for completion, then download.
    """

    def __init__(self, client: "OathNetClient"):
        self._client = client

    def create(
        self,
        export_type: Literal["docs", "victims"],
        format: Literal["jsonl", "csv"] = "jsonl",
        limit: int | None = None,
        fields: list[str] | None = None,
        search: dict[str, Any] | None = None,
    ) -> ExportJobResponse:
        """Create an export job.

        Creates an asynchronous export job.

        Args:
            export_type: Type of export ("docs" for credentials, "victims" for profiles)
            format: Output format ("jsonl" or "csv")
            limit: Maximum records to export
            fields: Specific fields to include
            search: Search criteria for export (query, domains, emails, etc.)

        Returns:
            ExportJobResponse with job ID and initial status

        Example:
            >>> job = client.exports.create(
            ...     export_type="docs",
            ...     format="csv",
            ...     search={"query": "gmail.com"}
            ... )
            >>> print(f"Job ID: {job.data.job_id}")
        """
        body: dict[str, Any] = {
            "type": export_type,
            "format": format,
        }

        if limit:
            body["limit"] = limit
        if fields:
            body["fields"] = fields
        if search:
            body["search"] = search

        data = self._client.post("/service/v2/exports", json=body)
        # API may return wrapped or unwrapped response
        if "success" in data:
            return ExportJobResponse.model_validate(data)
        # Wrap unwrapped response
        return ExportJobResponse(success=True, data=ExportJobData.model_validate(data))

    def get_status(self, job_id: str) -> ExportJobResponse:
        """Get export job status.

        Poll this endpoint to check job status.

        Args:
            job_id: Job ID from create()

        Returns:
            ExportJobResponse with status and progress

        Example:
            >>> status = client.exports.get_status("job_abc")
            >>> print(f"Progress: {status.data.progress.percent}%")
        """
        data = self._client.get(f"/service/v2/exports/{job_id}")
        # API may return wrapped or unwrapped response
        if "success" in data:
            return ExportJobResponse.model_validate(data)
        return ExportJobResponse(success=True, data=ExportJobData.model_validate(data))

    def download(
        self, job_id: str, output_path: str | Path | None = None
    ) -> bytes | Path:
        """Download export file.

        Downloads the completed export file.

        Args:
            job_id: Job ID of completed export
            output_path: Path to save the file (optional)

        Returns:
            bytes if no output_path, Path to saved file otherwise

        Example:
            >>> path = client.exports.download("job_abc", "export.csv")
        """
        raw_bytes = self._client.get_raw(f"/service/v2/exports/{job_id}/download")

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
    ) -> ExportJobResponse:
        """Wait for export job to complete.

        Polls the job status until completed, canceled, or timeout.

        Args:
            job_id: Job ID from create()
            poll_interval: Seconds between status checks
            timeout: Maximum seconds to wait

        Returns:
            ExportJobResponse with final status

        Raises:
            TimeoutError: If job doesn't complete within timeout
        """
        start_time = time.time()

        while True:
            response = self.get_status(job_id)
            status = response.data.status if response.data else None

            if status in ("completed", "canceled"):
                return response

            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(
                    f"Export job {job_id} did not complete within {timeout}s"
                )

            # Use server-suggested poll interval if available
            suggested_poll = (
                response.data.next_poll_after_ms / 1000
                if response.data and response.data.next_poll_after_ms
                else poll_interval
            )
            time.sleep(min(suggested_poll, poll_interval))

    def wait_and_download(
        self,
        job_id: str,
        output_path: str | Path,
        timeout: float = 600.0,
    ) -> Path:
        """Wait for export to complete and download.

        Convenience method that waits for completion and downloads the file.

        Args:
            job_id: Job ID from create()
            output_path: Path to save the export file
            timeout: Maximum seconds to wait

        Returns:
            Path to saved file

        Example:
            >>> job = client.exports.create("docs", format="csv")
            >>> path = client.exports.wait_and_download(job.data.job_id, "data.csv")
        """
        self.wait_for_completion(job_id, timeout=timeout)
        return self.download(job_id, output_path)

    def export(
        self,
        export_type: Literal["docs", "victims"],
        output_path: str | Path,
        format: Literal["jsonl", "csv"] = "jsonl",
        timeout: float = 600.0,
        **kwargs,
    ) -> Path:
        """Create export, wait for completion, and download.

        All-in-one convenience method for exporting data.

        Args:
            export_type: Type of export ("docs" or "victims")
            output_path: Path to save the export file
            format: Output format ("jsonl" or "csv")
            timeout: Maximum seconds to wait
            **kwargs: Additional create() parameters

        Returns:
            Path to saved file

        Example:
            >>> path = client.exports.export(
            ...     "docs",
            ...     "credentials.csv",
            ...     format="csv",
            ...     search={"query": "example.com"}
            ... )
        """
        job = self.create(export_type=export_type, format=format, **kwargs)
        return self.wait_and_download(job.data.job_id, output_path, timeout=timeout)
