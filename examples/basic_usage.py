#!/usr/bin/env python3
"""Basic usage example for OathNet SDK.

This example demonstrates:
- Client initialization
- Simple breach search
- Basic error handling
"""

import os

from oathnet import OathNetClient
from oathnet.exceptions import AuthenticationError, OathNetError


def main():
    # Get API key from environment
    api_key = os.environ.get("OATHNET_API_KEY")
    if not api_key:
        print("Error: Set OATHNET_API_KEY environment variable")
        return

    # Initialize client
    client = OathNetClient(api_key)

    # Or use as context manager for automatic cleanup
    with OathNetClient(api_key) as client:
        try:
            # Simple breach search
            print("Searching for 'example.com' in breach database...")
            result = client.search.breach("example.com")

            if result.success:
                print(f"Found {result.data.results_found} results")
                print(f"Retrieved {len(result.data.results)} records")

                # Print first few results
                for i, record in enumerate(result.data.results[:5]):
                    print(f"\n--- Result {i + 1} ---")
                    if hasattr(record, "email"):
                        print(f"Email: {record.email}")
                    if hasattr(record, "dbname"):
                        print(f"Database: {record.dbname}")
                    if hasattr(record, "password"):
                        print(f"Password: {'*' * 8}")  # Don't print actual password

        except AuthenticationError as e:
            print(f"Authentication failed: {e}")
        except OathNetError as e:
            print(f"API error: {e}")


if __name__ == "__main__":
    main()
