#!/usr/bin/env python3
"""Breach search example with advanced filters and pagination.

This example demonstrates:
- Breach search with filters
- Database filtering by name
- Pagination using cursor
- Sorting options
"""

import os

from oathnet import OathNetClient


def main():
    api_key = os.environ.get("OATHNET_API_KEY")
    if not api_key:
        print("Error: Set OATHNET_API_KEY environment variable")
        return

    with OathNetClient(api_key) as client:
        # Basic breach search
        print("=== Basic Breach Search ===")
        result = client.search.breach("winterfox", page=1, limit=10)
        print(f"Total found: {result.data.results_found}")
        print(f"Results: {len(result.data.results)}")

        # Search with database filter
        print("\n=== Search with Database Filter ===")
        result = client.search.breach(
            "gmail.com",
            dbname="linkedin",
            page=1,
            limit=10
        )
        print(f"LinkedIn results: {result.data.results_found}")

        # Iterate through all fields dynamically
        print("\n=== Dynamic Field Display ===")
        result = client.search.breach("winterfox", page=1, limit=3)
        for i, record in enumerate(result.data.results[:3]):
            print(f"\n--- Record {i + 1} ---")
            # Convert to dict and print all fields
            record_dict = record.model_dump(exclude_none=True)
            for key, value in record_dict.items():
                if value and key != "model_extra":
                    print(f"  {key}: {value}")

        # Pagination example
        print("\n=== Pagination Example ===")
        page = 1
        total_fetched = 0
        max_pages = 3

        while page <= max_pages:
            result = client.search.breach("gmail.com", page=page, limit=10)
            count = len(result.data.results)
            total_fetched += count
            print(f"Page {page}: {count} results")

            if count == 0:
                break
            page += 1

        print(f"Total fetched across {page - 1} pages: {total_fetched}")


if __name__ == "__main__":
    main()
