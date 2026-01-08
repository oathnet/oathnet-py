#!/usr/bin/env python3
"""Export example - async export to JSONL or CSV.

This example demonstrates:
- Creating export jobs
- Export formats (JSONL, CSV)
- Export types (docs, victims)
- Waiting for completion and downloading
"""

import os
import tempfile
from pathlib import Path

from oathnet import OathNetClient


def main():
    api_key = os.environ.get("OATHNET_API_KEY")
    if not api_key:
        print("Error: Set OATHNET_API_KEY environment variable")
        return

    with OathNetClient(api_key) as client:
        # Method 1: All-in-one export
        print("=== Simple Export (JSONL) ===")
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
            output_path = f.name

        try:
            path = client.exports.export(
                export_type="docs",
                output_path=output_path,
                format="jsonl",
                limit=100,
                timeout=120.0,
                search={"query": "gmail.com"},
            )
            size = path.stat().st_size
            print(f"Exported to: {path}")
            print(f"File size: {size} bytes")

            # Preview first few lines
            with open(path, "r") as f:
                lines = f.readlines()[:3]
                print(f"Preview ({len(lines)} lines):")
                for line in lines:
                    print(f"  {line[:100]}...")
        except Exception as e:
            print(f"Export failed: {e}")
        finally:
            Path(output_path).unlink(missing_ok=True)

        # Method 2: Manual job management
        print("\n=== Manual Export Management ===")

        # Create CSV export job
        job = client.exports.create(
            export_type="docs",
            format="csv",
            limit=50,
            fields=["email", "password", "domain", "url"],
            search={"query": "gmail.com"},
        )
        print(f"Created job: {job.data.job_id}")
        print(f"Initial status: {job.data.status}")

        # Wait for completion
        print("Waiting for completion...")
        result = client.exports.wait_for_completion(
            job.data.job_id,
            poll_interval=2.0,
            timeout=120.0,
        )
        print(f"Final status: {result.data.status}")

        if result.data.status == "completed":
            # Download as bytes
            data = client.exports.download(job.data.job_id)
            print(f"Downloaded {len(data)} bytes")

            # Preview CSV content
            preview = data[:500].decode("utf-8", errors="replace")
            print(f"CSV Preview:\n{preview}")

            # Or download to file
            with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
                temp_path = f.name

            try:
                path = client.exports.download(job.data.job_id, temp_path)
                print(f"\nSaved to: {path}")
            finally:
                Path(temp_path).unlink(missing_ok=True)
        else:
            print(f"Export did not complete: {result.data.status}")

        # Export victims data
        print("\n=== Export Victims Data ===")
        job = client.exports.create(
            export_type="victims",
            format="jsonl",
            limit=50,
            search={"query": "gmail"},
        )
        print(f"Created victims export job: {job.data.job_id}")

        result = client.exports.wait_for_completion(
            job.data.job_id,
            timeout=120.0,
        )
        print(f"Status: {result.data.status}")

        if result.data.status == "completed":
            data = client.exports.download(job.data.job_id)
            print(f"Downloaded {len(data)} bytes of victim data")

        # Export with domain filter
        print("\n=== Export with Domain Filter ===")
        job = client.exports.create(
            export_type="docs",
            format="jsonl",
            limit=50,
            search={"domains": ["github.com"]},
        )
        print(f"Created domain-filtered export: {job.data.job_id}")

        result = client.exports.wait_for_completion(job.data.job_id, timeout=120.0)
        print(f"Status: {result.data.status}")


if __name__ == "__main__":
    main()
