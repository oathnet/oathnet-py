"""Tests for ExportsService - async export to JSONL or CSV."""

import tempfile
from pathlib import Path

import pytest

from oathnet import OathNetClient
from oathnet.exceptions import ValidationError


class TestExportsService:
    """Test exports service endpoints."""

    def test_create_export_job_docs(self, client: OathNetClient):
        """Test creating a docs export job."""
        result = client.exports.create(
            export_type="docs",
            format="jsonl",
            limit=100,
            search={"query": "gmail.com"},
        )
        assert result.success is True
        assert result.data is not None
        assert result.data.job_id is not None
        assert result.data.status in ("pending", "processing", "queued", "running", "completed")

    def test_create_export_job_victims(self, client: OathNetClient):
        """Test creating a victims export job."""
        result = client.exports.create(
            export_type="victims",
            format="jsonl",
            limit=100,
            search={"query": "gmail"},
        )
        assert result.success is True
        assert result.data is not None
        assert result.data.job_id is not None

    def test_create_export_csv_format(self, client: OathNetClient):
        """Test creating export with CSV format."""
        result = client.exports.create(
            export_type="docs",
            format="csv",
            limit=100,
            search={"query": "gmail.com"},
        )
        assert result.success is True
        assert result.data is not None
        assert result.data.job_id is not None

    def test_create_export_with_fields(self, client: OathNetClient):
        """Test creating export with specific fields."""
        result = client.exports.create(
            export_type="docs",
            format="jsonl",
            limit=100,
            fields=["email", "domain", "password"],
            search={"query": "gmail.com"},
        )
        assert result.success is True
        assert result.data is not None
        assert result.data.job_id is not None

    def test_get_export_status(self, client: OathNetClient):
        """Test getting export job status."""
        # Create a job first
        job = client.exports.create(
            export_type="docs",
            format="jsonl",
            limit=100,
            search={"query": "gmail.com"},
        )
        assert job.data.job_id is not None

        # Get status
        status = client.exports.get_status(job.data.job_id)
        assert status.success is True
        assert status.data is not None
        assert status.data.status in ("pending", "processing", "completed", "canceled")

    def test_wait_for_completion(self, client: OathNetClient):
        """Test waiting for export completion."""
        # Create a small export job
        job = client.exports.create(
            export_type="docs",
            format="jsonl",
            limit=100,
            search={"query": "gmail.com"},
        )
        assert job.data.job_id is not None

        # Wait for completion
        result = client.exports.wait_for_completion(
            job.data.job_id,
            poll_interval=1.0,
            timeout=120.0,
        )
        assert result.success is True
        assert result.data is not None
        assert result.data.status in ("completed", "canceled")

    @pytest.mark.skip(reason="Export download API returns 500 error - known API issue")
    def test_download_export(self, client: OathNetClient):
        """Test downloading completed export."""
        # Create and wait for export
        job = client.exports.create(
            export_type="docs",
            format="jsonl",
            limit=100,
            search={"query": "gmail.com"},
        )

        result = client.exports.wait_for_completion(
            job.data.job_id,
            timeout=120.0,
        )

        if result.data.status != "completed":
            pytest.skip("Export did not complete successfully")

        # Download as bytes
        data = client.exports.download(job.data.job_id)
        assert isinstance(data, bytes)
        assert len(data) > 0

    @pytest.mark.skip(reason="Export download API returns 500 error - known API issue")
    def test_download_export_to_file(self, client: OathNetClient):
        """Test downloading export to file."""
        # Create and wait for export
        job = client.exports.create(
            export_type="docs",
            format="jsonl",
            limit=100,
            search={"query": "gmail.com"},
        )

        result = client.exports.wait_for_completion(
            job.data.job_id,
            timeout=120.0,
        )

        if result.data.status != "completed":
            pytest.skip("Export did not complete successfully")

        # Download to temp file
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
            temp_path = f.name

        try:
            path = client.exports.download(job.data.job_id, temp_path)
            assert isinstance(path, Path)
            assert path.exists()
            assert path.stat().st_size > 0
        finally:
            Path(temp_path).unlink(missing_ok=True)

    @pytest.mark.skip(reason="Export download API returns 500 error - known API issue")
    def test_wait_and_download(self, client: OathNetClient):
        """Test wait_and_download convenience method."""
        # Create export
        job = client.exports.create(
            export_type="docs",
            format="jsonl",
            limit=100,
            search={"query": "gmail.com"},
        )

        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
            temp_path = f.name

        try:
            path = client.exports.wait_and_download(
                job.data.job_id,
                temp_path,
                timeout=120.0,
            )
            assert path.exists()
            assert path.stat().st_size > 0
        except Exception as e:
            # Export may not complete if job was canceled
            if "canceled" in str(e).lower():
                pytest.skip("Export was canceled")
            raise
        finally:
            Path(temp_path).unlink(missing_ok=True)

    @pytest.mark.skip(reason="Export download API returns 500 error - known API issue")
    def test_export_convenience_method(self, client: OathNetClient):
        """Test the all-in-one export method."""
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
            temp_path = f.name

        try:
            path = client.exports.export(
                export_type="docs",
                output_path=temp_path,
                format="jsonl",
                limit=100,
                timeout=120.0,
                search={"query": "gmail.com"},
            )
            assert path.exists()
            assert path.stat().st_size > 0
        except Exception as e:
            # Export may not complete if job was canceled
            if "canceled" in str(e).lower():
                pytest.skip("Export was canceled")
            raise
        finally:
            Path(temp_path).unlink(missing_ok=True)


class TestExportsWithSearchCriteria:
    """Test exports with various search criteria."""

    def test_export_with_domain_filter(self, client: OathNetClient):
        """Test export with domain filter."""
        result = client.exports.create(
            export_type="docs",
            format="jsonl",
            limit=100,
            search={"domains": ["gmail.com"]},
        )
        assert result.success is True
        assert result.data is not None

    def test_export_with_multiple_criteria(self, client: OathNetClient):
        """Test export with multiple search criteria."""
        result = client.exports.create(
            export_type="docs",
            format="jsonl",
            limit=100,
            search={
                "query": "gmail.com",
                "has_password": True,
            },
        )
        assert result.success is True
        assert result.data is not None


class TestExportsErrorHandling:
    """Test exports error handling."""

    def test_invalid_job_id(self, client: OathNetClient):
        """Test getting status for invalid job ID."""
        with pytest.raises((ValidationError, Exception)):
            client.exports.get_status("invalid_job_id_12345")

    def test_download_invalid_job(self, client: OathNetClient):
        """Test downloading from invalid job ID."""
        with pytest.raises((ValidationError, Exception)):
            client.exports.download("invalid_job_id_12345")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
