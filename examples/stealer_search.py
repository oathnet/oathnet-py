#!/usr/bin/env python3
"""Stealer search example with V2 API.

This example demonstrates:
- V2 stealer search with various filters
- Domain and subdomain filtering
- Log ID access for victim profile linking
- Subdomain extraction
"""

import os

from oathnet import OathNetClient


def main():
    api_key = os.environ.get("OATHNET_API_KEY")
    if not api_key:
        print("Error: Set OATHNET_API_KEY environment variable")
        return

    with OathNetClient(api_key) as client:
        # Basic stealer search
        print("=== V2 Stealer Search ===")
        result = client.stealer.search(q="gmail.com", page_size=10)
        print(f"Success: {result.success}")
        if result.data:
            total = result.data.meta.total if result.data.meta else 0
            print(f"Total found: {total}")
            print(f"Results: {len(result.data.items)}")

            # Show results with log IDs for victim profile access
            print("\n=== Results with Log IDs ===")
            log_ids = []
            for i, record in enumerate(result.data.items[:5]):
                print(f"\n--- Record {i + 1} ---")
                if hasattr(record, "url") and record.url:
                    print(f"  URL: {record.url}")
                if hasattr(record, "username") and record.username:
                    print(f"  Username: {record.username}")
                if hasattr(record, "password") and record.password:
                    print(f"  Password: {'*' * 8}")
                if hasattr(record, "log_id") and record.log_id:
                    print(f"  Log ID: {record.log_id}")
                    log_ids.append(record.log_id)

            # Collect unique log IDs
            if log_ids:
                unique_log_ids = list(set(log_ids))
                print(f"\n=== Unique Log IDs (for victim profile access) ===")
                print(f"Found {len(unique_log_ids)} unique victim profiles:")
                for lid in unique_log_ids[:10]:
                    print(f"  - {lid}")

        # Search with domain filter
        print("\n=== Domain-Specific Search ===")
        result = client.stealer.search(
            domain=["google.com"],
            page_size=5,
            wildcard=True
        )
        if result.data:
            total = result.data.meta.total if result.data.meta else 0
            print(f"Google domain results: {total}")

        # Search with has_log_id filter
        print("\n=== Search with Log ID Filter ===")
        result = client.stealer.search(
            q="gmail.com",
            has_log_id=True,
            page_size=5
        )
        if result.data:
            total = result.data.meta.total if result.data.meta else 0
            print(f"Results with victim profiles: {total}")

        # Subdomain extraction
        print("\n=== Subdomain Extraction ===")
        subdomain_result = client.stealer.subdomain(domain="google.com")
        print(f"Success: {subdomain_result.success}")
        if subdomain_result.data and subdomain_result.data.subdomains:
            print(f"Found {len(subdomain_result.data.subdomains)} subdomains:")
            for sub in subdomain_result.data.subdomains[:10]:
                print(f"  - {sub}")


if __name__ == "__main__":
    main()
