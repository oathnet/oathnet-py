#!/usr/bin/env python3
"""File search example - async search within victim files.

This example demonstrates:
- Creating file search jobs
- Different search modes (literal, regex, wildcard)
- Polling for job completion
- Processing search results
"""

import os

from oathnet import OathNetClient


def main():
    api_key = os.environ.get("OATHNET_API_KEY")
    if not api_key:
        print("Error: Set OATHNET_API_KEY environment variable")
        return

    with OathNetClient(api_key) as client:
        # Method 1: All-in-one search (create + wait)
        print("=== Simple File Search ===")
        result = client.file_search.search(
            expression="password",
            search_mode="literal",
            max_matches=10,
            timeout=60.0,
        )
        print(f"Status: {result.data.status}")
        if result.data.matches:
            print(f"Found {len(result.data.matches)} matches:")
            for match in result.data.matches[:5]:
                print(f"  - Log: {match.log_id}")
                print(f"    File: {match.file_name}")
                if match.match_text:
                    # Truncate long matches
                    preview = match.match_text[:100]
                    print(f"    Match: {preview}...")

        # Method 2: Manual job creation and polling
        print("\n=== Manual Job Management ===")

        # Create job
        job = client.file_search.create(
            expression=r"api[_-]?key",
            search_mode="regex",
            max_matches=5,
            include_matches=True,
            context_lines=2,
        )
        print(f"Created job: {job.data.job_id}")
        print(f"Initial status: {job.data.status}")

        # Poll for status
        print("\nPolling for completion...")
        result = client.file_search.wait_for_completion(
            job.data.job_id,
            poll_interval=2.0,
            timeout=60.0,
        )
        print(f"Final status: {result.data.status}")

        if result.data.matches:
            print(f"\nFound {len(result.data.matches)} regex matches")

        # Search with specific log IDs
        print("\n=== Search Within Specific Logs ===")

        # First get some log IDs
        victims = client.victims.search(q="gmail", page_size=3)
        log_ids = [
            v.log_id for v in victims.data.results
            if hasattr(v, "log_id") and v.log_id
        ][:3]

        if log_ids:
            print(f"Searching within {len(log_ids)} victim logs...")
            result = client.file_search.search(
                expression="*@gmail.com",
                search_mode="wildcard",
                log_ids=log_ids,
                max_matches=10,
                timeout=60.0,
            )
            print(f"Status: {result.data.status}")
            if result.data.matches:
                print(f"Found {len(result.data.matches)} matches in specified logs")
        else:
            print("No log IDs available for targeted search")

        # Search with file pattern filter
        print("\n=== Search with File Pattern Filter ===")
        result = client.file_search.search(
            expression="token",
            search_mode="literal",
            file_pattern="*.txt",
            max_matches=5,
            timeout=60.0,
        )
        print(f"Matches in .txt files: {len(result.data.matches or [])}")


if __name__ == "__main__":
    main()
