#!/usr/bin/env python3
"""Pagination example - cursor-based pagination patterns.

This example demonstrates:
- Page-based pagination (breach search)
- Cursor-based pagination (V2 APIs)
- Efficient iteration patterns
- Collecting all results
"""

import os

from oathnet import OathNetClient


def main():
    api_key = os.environ.get("OATHNET_API_KEY")
    if not api_key:
        print("Error: Set OATHNET_API_KEY environment variable")
        return

    with OathNetClient(api_key) as client:
        # Page-based pagination (breach search)
        print("=== Page-Based Pagination (Breach) ===")
        page = 1
        limit = 25
        total_fetched = 0
        max_pages = 3  # Limit for demo

        while page <= max_pages:
            result = client.search.breach("gmail.com", page=page, limit=limit)
            count = len(result.data.results)
            total_fetched += count

            print(f"Page {page}: {count} results (Total: {result.data.results_found})")

            if count < limit:
                print("Reached end of results")
                break

            page += 1

        print(f"Fetched {total_fetched} records across {page} pages\n")

        # Cursor-based pagination (V2 Stealer)
        print("=== Cursor-Based Pagination (V2 Stealer) ===")
        cursor = None
        page_size = 25
        total_fetched = 0
        pages = 0
        max_pages = 3  # Limit for demo

        while pages < max_pages:
            result = client.stealer.search(
                q="gmail.com",
                page_size=page_size,
                cursor=cursor,
            )
            count = len(result.data.results)
            total_fetched += count
            pages += 1

            print(f"Page {pages}: {count} results (Total: {result.data.total_results})")

            # Get next cursor
            cursor = result.data.next_cursor
            if not cursor:
                print("No more pages")
                break

        print(f"Fetched {total_fetched} stealer records across {pages} pages\n")

        # Cursor-based pagination (V2 Victims)
        print("=== Cursor-Based Pagination (V2 Victims) ===")
        cursor = None
        page_size = 10
        total_fetched = 0
        pages = 0
        max_pages = 3

        while pages < max_pages:
            result = client.victims.search(
                q="gmail",
                page_size=page_size,
                cursor=cursor,
            )
            count = len(result.data.results)
            total_fetched += count
            pages += 1

            print(f"Page {pages}: {count} victims (Total: {result.data.total_results})")

            cursor = result.data.next_cursor
            if not cursor:
                print("No more pages")
                break

        print(f"Fetched {total_fetched} victim profiles across {pages} pages\n")

        # Collect all results helper pattern
        print("=== Collect All Results Pattern ===")

        def collect_all_stealer_results(client, query, max_results=100):
            """Collect stealer results up to max_results."""
            results = []
            cursor = None

            while len(results) < max_results:
                remaining = max_results - len(results)
                page_size = min(25, remaining)

                response = client.stealer.search(
                    q=query,
                    page_size=page_size,
                    cursor=cursor,
                )

                results.extend(response.data.results)
                cursor = response.data.next_cursor

                if not cursor or not response.data.results:
                    break

            return results[:max_results]

        all_results = collect_all_stealer_results(client, "gmail.com", max_results=50)
        print(f"Collected {len(all_results)} total results")

        # Show unique domains from collected results
        domains = set()
        for r in all_results:
            if hasattr(r, "domain") and r.domain:
                domains.add(r.domain)
        print(f"Unique domains: {len(domains)}")

        # Generator pattern for memory-efficient iteration
        print("\n=== Generator Pattern ===")

        def iter_stealer_results(client, query, max_pages=10):
            """Generator that yields stealer results page by page."""
            cursor = None
            pages = 0

            while pages < max_pages:
                response = client.stealer.search(
                    q=query,
                    page_size=25,
                    cursor=cursor,
                )

                for result in response.data.results:
                    yield result

                cursor = response.data.next_cursor
                pages += 1

                if not cursor:
                    break

        # Process results one at a time (memory efficient)
        count = 0
        for result in iter_stealer_results(client, "gmail.com", max_pages=2):
            count += 1
            if count <= 3:
                url = getattr(result, "url", "N/A")
                print(f"  Result {count}: {url[:50]}...")

        print(f"Processed {count} results using generator")


if __name__ == "__main__":
    main()
