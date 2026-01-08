#!/usr/bin/env python3
"""Error handling example - exception patterns and best practices.

This example demonstrates:
- Different exception types
- Proper error handling patterns
- Retry logic for transient errors
- Validation error handling
"""

import os
import time

from oathnet import OathNetClient
from oathnet.exceptions import (
    AuthenticationError,
    NotFoundError,
    OathNetError,
    RateLimitError,
    ServerError,
    ValidationError,
)


def main():
    api_key = os.environ.get("OATHNET_API_KEY")
    if not api_key:
        print("Error: Set OATHNET_API_KEY environment variable")
        return

    # Example 1: Basic error handling
    print("=== Basic Error Handling ===")
    with OathNetClient(api_key) as client:
        try:
            result = client.search.breach("example.com")
            print(f"Search successful: {result.data.results_found} results")
        except AuthenticationError as e:
            print(f"Authentication failed - check your API key: {e}")
        except ValidationError as e:
            print(f"Invalid input: {e}")
        except NotFoundError as e:
            print(f"Resource not found: {e}")
        except RateLimitError as e:
            print(f"Rate limited - slow down requests: {e}")
        except ServerError as e:
            print(f"Server error - try again later: {e}")
        except OathNetError as e:
            print(f"API error: {e}")

    # Example 2: Invalid API key handling
    print("\n=== Invalid API Key ===")
    try:
        bad_client = OathNetClient("invalid_api_key")
        bad_client.search.breach("test")
    except (AuthenticationError, ValidationError) as e:
        print(f"Expected error: {e}")

    # Example 3: Validation errors
    print("\n=== Validation Errors ===")
    with OathNetClient(api_key) as client:
        try:
            # Invalid Discord ID (too short)
            client.osint.discord_userinfo("123")
        except ValidationError as e:
            print(f"Validation error: {e}")
        except NotFoundError as e:
            print(f"Not found: {e}")

    # Example 4: No results handling
    print("\n=== No Results Handling ===")
    with OathNetClient(api_key) as client:
        try:
            result = client.search.breach("xyznonexistent123456789abcdef")
            if result.data.results_found == 0:
                print("No results found (API returned success with empty results)")
        except ValidationError as e:
            if "no results" in str(e).lower():
                print("No results found (API returned validation error)")
            else:
                raise

    # Example 5: Retry logic for transient errors
    print("\n=== Retry Logic ===")

    def search_with_retry(client, query, max_retries=3, backoff=1.0):
        """Search with exponential backoff retry."""
        for attempt in range(max_retries):
            try:
                return client.search.breach(query)
            except RateLimitError:
                if attempt < max_retries - 1:
                    wait_time = backoff * (2 ** attempt)
                    print(f"Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise
            except ServerError:
                if attempt < max_retries - 1:
                    wait_time = backoff * (2 ** attempt)
                    print(f"Server error, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise
        return None

    with OathNetClient(api_key) as client:
        result = search_with_retry(client, "gmail.com")
        if result:
            print(f"Search succeeded: {result.data.results_found} results")

    # Example 6: Context manager error handling
    print("\n=== Context Manager Cleanup ===")
    try:
        with OathNetClient(api_key) as client:
            result = client.search.breach("example.com")
            print(f"Results: {result.data.results_found}")
            # Client is automatically cleaned up on exit
    except OathNetError as e:
        print(f"Error occurred, but client was still cleaned up: {e}")

    # Example 7: Checking specific error codes
    print("\n=== Error Code Handling ===")
    with OathNetClient(api_key) as client:
        try:
            client.osint.discord_userinfo("invalid")
        except OathNetError as e:
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {e}")

    print("\nError handling examples complete!")


if __name__ == "__main__":
    main()
