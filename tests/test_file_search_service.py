"""Tests for FileSearchService - async file search within victim logs."""

import pytest

from oathnet import OathNetClient
from oathnet.exceptions import ValidationError


def get_log_ids(client: OathNetClient, count: int = 3) -> list[str]:
    """Helper to get log_ids from stealer search (with has_log_id filter)."""
    result = client.stealer.search(q="gmail.com", page_size=10, has_log_id=True)
    if not result.data or not result.data.items:
        return []
    log_ids = [v.log_id for v in result.data.items if v.log_id]
    # Return unique log_ids
    return list(set(log_ids))[:count]


class TestFileSearchService:
    """Test file search service endpoints."""

    def test_create_file_search_job(self, client: OathNetClient):
        """Test creating a file search job."""
        log_ids = get_log_ids(client)
        if not log_ids:
            pytest.skip("No log IDs available from stealer search")

        result = client.file_search.create(
            expression="password",
            search_mode="literal",
            log_ids=log_ids,
            max_matches=5,
        )
        assert result.success is True
        assert result.data is not None
        assert result.data.job_id is not None
        assert result.data.status in ("pending", "processing", "queued", "running", "completed")

    def test_create_file_search_with_regex(self, client: OathNetClient):
        """Test file search with regex mode."""
        log_ids = get_log_ids(client)
        if not log_ids:
            pytest.skip("No log IDs available from stealer search")

        result = client.file_search.create(
            expression=r"pass(word|wd)",
            search_mode="regex",
            log_ids=log_ids,
            max_matches=5,
        )
        assert result.success is True
        assert result.data is not None
        assert result.data.job_id is not None

    def test_create_file_search_with_wildcard(self, client: OathNetClient):
        """Test file search with wildcard mode."""
        log_ids = get_log_ids(client)
        if not log_ids:
            pytest.skip("No log IDs available from stealer search")

        result = client.file_search.create(
            expression="*@gmail.com",
            search_mode="wildcard",
            log_ids=log_ids,
            max_matches=5,
        )
        assert result.success is True
        assert result.data is not None
        assert result.data.job_id is not None

    def test_create_file_search_with_log_ids(self, client: OathNetClient):
        """Test file search with specific log IDs."""
        log_ids = get_log_ids(client, count=2)
        if not log_ids:
            pytest.skip("No log IDs available")

        result = client.file_search.create(
            expression="password",
            search_mode="literal",
            log_ids=log_ids,
            max_matches=5,
        )
        assert result.success is True
        assert result.data is not None
        assert result.data.job_id is not None

    def test_get_file_search_status(self, client: OathNetClient):
        """Test getting file search job status."""
        log_ids = get_log_ids(client)
        if not log_ids:
            pytest.skip("No log IDs available from stealer search")

        # Create a job first
        job = client.file_search.create(
            expression="test",
            search_mode="literal",
            log_ids=log_ids,
            max_matches=5,
        )
        assert job.data.job_id is not None

        # Get status
        status = client.file_search.get_status(job.data.job_id)
        assert status.success is True
        assert status.data is not None
        assert status.data.status in ("pending", "processing", "queued", "running", "completed", "canceled")

    def test_wait_for_completion(self, client: OathNetClient):
        """Test waiting for file search completion."""
        log_ids = get_log_ids(client)
        if not log_ids:
            pytest.skip("No log IDs available from stealer search")

        # Create a small job
        job = client.file_search.create(
            expression="password",
            search_mode="literal",
            log_ids=log_ids,
            max_matches=3,
        )
        assert job.data.job_id is not None

        # Wait for completion (with short timeout for tests)
        result = client.file_search.wait_for_completion(
            job.data.job_id,
            poll_interval=1.0,
            timeout=60.0,
        )
        assert result.success is True
        assert result.data is not None
        assert result.data.status in ("completed", "canceled")

    def test_search_convenience_method(self, client: OathNetClient):
        """Test the all-in-one search method."""
        log_ids = get_log_ids(client)
        if not log_ids:
            pytest.skip("No log IDs available from stealer search")

        result = client.file_search.search(
            expression="password",
            search_mode="literal",
            log_ids=log_ids,
            max_matches=3,
            timeout=60.0,
        )
        assert result.success is True
        assert result.data is not None
        assert result.data.status in ("completed", "canceled")

    def test_file_search_with_file_pattern(self, client: OathNetClient):
        """Test file search with file pattern filter."""
        log_ids = get_log_ids(client)
        if not log_ids:
            pytest.skip("No log IDs available from stealer search")

        result = client.file_search.create(
            expression="password",
            search_mode="literal",
            log_ids=log_ids,
            file_pattern="*.txt",
            max_matches=5,
        )
        assert result.success is True
        assert result.data is not None

    def test_file_search_with_context_lines(self, client: OathNetClient):
        """Test file search with context lines."""
        log_ids = get_log_ids(client)
        if not log_ids:
            pytest.skip("No log IDs available from stealer search")

        result = client.file_search.create(
            expression="password",
            search_mode="literal",
            log_ids=log_ids,
            context_lines=3,
            max_matches=5,
        )
        assert result.success is True
        assert result.data is not None

    def test_file_search_case_sensitive(self, client: OathNetClient):
        """Test case-sensitive file search."""
        log_ids = get_log_ids(client)
        if not log_ids:
            pytest.skip("No log IDs available from stealer search")

        result = client.file_search.create(
            expression="Password",
            search_mode="literal",
            log_ids=log_ids,
            case_sensitive=True,
            max_matches=5,
        )
        assert result.success is True
        assert result.data is not None


class TestFileSearchErrorHandling:
    """Test file search error handling."""

    def test_invalid_job_id(self, client: OathNetClient):
        """Test getting status for invalid job ID."""
        with pytest.raises((ValidationError, Exception)):
            client.file_search.get_status("invalid_job_id_12345")

    def test_empty_expression(self, client: OathNetClient):
        """Test creating job with empty expression."""
        with pytest.raises((ValidationError, Exception)):
            client.file_search.create(
                expression="",
                search_mode="literal",
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
