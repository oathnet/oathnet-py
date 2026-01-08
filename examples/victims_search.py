#!/usr/bin/env python3
"""Victims search example with manifest and file access.

This example demonstrates:
- Victim profile search
- Fetching victim manifest (file tree)
- Accessing individual files
- Downloading full archive
"""

import os
import tempfile

from oathnet import OathNetClient


def main():
    api_key = os.environ.get("OATHNET_API_KEY")
    if not api_key:
        print("Error: Set OATHNET_API_KEY environment variable")
        return

    with OathNetClient(api_key) as client:
        # Search for victim profiles
        print("=== Victims Search ===")
        result = client.victims.search(q="gmail", page_size=5)
        print(f"Success: {result.success}")
        print(f"Total found: {result.data.total_results}")

        if not result.data.results:
            print("No results found")
            return

        # Display victim profiles
        print("\n=== Victim Profiles ===")
        for i, victim in enumerate(result.data.results[:3]):
            print(f"\n--- Profile {i + 1} ---")
            if hasattr(victim, "log_id"):
                print(f"  Log ID: {victim.log_id}")
            if hasattr(victim, "computer_name"):
                print(f"  Computer: {victim.computer_name}")
            if hasattr(victim, "country"):
                print(f"  Country: {victim.country}")
            if hasattr(victim, "malware_family"):
                print(f"  Malware: {victim.malware_family}")
            if hasattr(victim, "date"):
                print(f"  Date: {victim.date}")

        # Get manifest for first victim with log_id
        log_id = None
        for victim in result.data.results:
            if hasattr(victim, "log_id") and victim.log_id:
                log_id = victim.log_id
                break

        if not log_id:
            print("\nNo log IDs available for manifest demo")
            return

        print(f"\n=== Manifest for {log_id} ===")
        try:
            manifest = client.victims.get_manifest(log_id)
            if manifest and manifest.files:
                print(f"Found {len(manifest.files)} files:")
                for f in manifest.files[:10]:
                    if hasattr(f, "path"):
                        print(f"  - {f.path}")
                    elif hasattr(f, "name"):
                        print(f"  - {f.name}")

                # Try to get content of first text file
                print("\n=== File Content Preview ===")
                text_file = None
                for f in manifest.files:
                    path = getattr(f, "path", "") or getattr(f, "name", "")
                    if path.endswith((".txt", ".log")):
                        text_file = f
                        break

                if text_file and hasattr(text_file, "file_id"):
                    file_id = text_file.file_id
                    print(f"Fetching: {getattr(text_file, 'path', text_file.file_id)}")
                    content = client.victims.get_file(log_id, file_id)
                    # Show first 500 bytes
                    preview = content[:500].decode("utf-8", errors="replace")
                    print(f"Content preview:\n{preview}...")
                else:
                    print("No suitable text file found for preview")

        except Exception as e:
            print(f"Could not fetch manifest: {e}")

        # Archive download example (commented out to avoid large downloads)
        # print("\n=== Archive Download ===")
        # with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as f:
        #     temp_path = f.name
        # client.victims.download_archive(log_id, temp_path)
        # print(f"Archive saved to: {temp_path}")


if __name__ == "__main__":
    main()
