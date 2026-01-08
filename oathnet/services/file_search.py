"""File Search Service - V2 async file search within victim files."""

import time
from typing import TYPE_CHECKING, Literal

from ..models import FileSearchJobData, FileSearchJobResponse

if TYPE_CHECKING:
    from ..client import OathNetClient


class FileSearchService:
    """Service for V2 file search operations.

    Search within victim files using regex, literal, or wildcard patterns.
    File search is asynchronous - create a job, then poll for results.
    """

    def __init__(self, client: "OathNetClient"):
        self._client = client

    def create(
        self,
        expression: str,
        search_mode: Literal["literal", "regex", "wildcard"] = "literal",
        log_ids: list[str] | None = None,
        include_matches: bool = True,
        case_sensitive: bool = False,
        context_lines: int = 2,
        file_pattern: str | None = None,
        max_matches: int = 100,
    ) -> FileSearchJobResponse:
        """Create a file search job.

        Creates an asynchronous job to search within victim files.

        Args:
            expression: Search expression
            search_mode: Search mode (literal, regex, wildcard)
            log_ids: Victim log IDs to search (optional, defaults to all)
            include_matches: Include match text in results
            case_sensitive: Enable case-sensitive matching
            context_lines: Lines of context around matches (0-5)
            file_pattern: Glob pattern for file filtering
            max_matches: Maximum matches to return

        Returns:
            FileSearchJobResponse with job ID and initial status

        Example:
            >>> job = client.file_search.create("password", search_mode="literal")
            >>> print(f"Job ID: {job.data.job_id}")
        """
        body = {
            "expression": expression,
            "search_mode": search_mode,
            "include_matches": include_matches,
            "case_sensitive": case_sensitive,
            "context_lines": context_lines,
            "max_matches": max_matches,
        }

        if log_ids:
            body["log_ids"] = log_ids
        if file_pattern:
            body["file_pattern"] = file_pattern

        data = self._client.post("/service/v2/file-search", json=body)
        # API may return wrapped or unwrapped response
        if "success" in data:
            return FileSearchJobResponse.model_validate(data)
        return FileSearchJobResponse(success=True, data=FileSearchJobData.model_validate(data))

    def get_status(self, job_id: str) -> FileSearchJobResponse:
        """Get file search job status.

        Poll this endpoint to check job status and retrieve results.

        Args:
            job_id: Job ID from create()

        Returns:
            FileSearchJobResponse with status and results if completed

        Example:
            >>> status = client.file_search.get_status("job_abc")
            >>> print(f"Status: {status.data.status}")
        """
        data = self._client.get(f"/service/v2/file-search/{job_id}")
        # API may return wrapped or unwrapped response
        if "success" in data:
            return FileSearchJobResponse.model_validate(data)
        return FileSearchJobResponse(success=True, data=FileSearchJobData.model_validate(data))

    def wait_for_completion(
        self,
        job_id: str,
        poll_interval: float = 2.0,
        timeout: float = 300.0,
    ) -> FileSearchJobResponse:
        """Wait for file search job to complete.

        Polls the job status until completed, canceled, or timeout.

        Args:
            job_id: Job ID from create()
            poll_interval: Seconds between status checks
            timeout: Maximum seconds to wait

        Returns:
            FileSearchJobResponse with final status and results

        Raises:
            TimeoutError: If job doesn't complete within timeout

        Example:
            >>> job = client.file_search.create("api_key")
            >>> result = client.file_search.wait_for_completion(job.data.job_id)
            >>> for match in result.data.matches:
            ...     print(f"{match.file_name}: {match.match_text}")
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
                    f"File search job {job_id} did not complete within {timeout}s"
                )

            # Use server-suggested poll interval if available
            suggested_poll = (
                response.data.next_poll_after_ms / 1000
                if response.data and response.data.next_poll_after_ms
                else poll_interval
            )
            time.sleep(min(suggested_poll, poll_interval))

    def search(
        self,
        expression: str,
        search_mode: Literal["literal", "regex", "wildcard"] = "literal",
        log_ids: list[str] | None = None,
        timeout: float = 300.0,
        **kwargs,
    ) -> FileSearchJobResponse:
        """Create a file search job and wait for results.

        Convenience method that creates a job and waits for completion.

        Args:
            expression: Search expression
            search_mode: Search mode (literal, regex, wildcard)
            log_ids: Victim log IDs to search
            timeout: Maximum seconds to wait for completion
            **kwargs: Additional create() parameters

        Returns:
            FileSearchJobResponse with completed results

        Example:
            >>> result = client.file_search.search("password", search_mode="regex")
            >>> print(f"Found {len(result.data.matches)} matches")
        """
        job = self.create(
            expression=expression,
            search_mode=search_mode,
            log_ids=log_ids,
            **kwargs,
        )
        return self.wait_for_completion(job.data.job_id, timeout=timeout)
