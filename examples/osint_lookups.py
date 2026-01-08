#!/usr/bin/env python3
"""OSINT lookups example - all OSINT methods.

This example demonstrates:
- Discord user info and username history
- Discord to Roblox mapping
- Steam and Xbox profile lookups
- Roblox user info
- Email analysis with Holehe
- IP geolocation
- Subdomain extraction
"""

import os

from oathnet import OathNetClient
from oathnet.exceptions import NotFoundError, ValidationError


def main():
    api_key = os.environ.get("OATHNET_API_KEY")
    if not api_key:
        print("Error: Set OATHNET_API_KEY environment variable")
        return

    with OathNetClient(api_key) as client:
        # Discord User Info
        print("=== Discord User Info ===")
        try:
            result = client.osint.discord_userinfo("300760994454437890")
            if result.data:
                print(f"Username: {result.data.username}")
                print(f"Global Name: {result.data.global_name}")
                print(f"Avatar URL: {result.data.avatar_url}")
        except (NotFoundError, ValidationError) as e:
            print(f"Error: {e}")

        # Discord Username History
        print("\n=== Discord Username History ===")
        try:
            result = client.osint.discord_username_history("1375046349392974005")
            if result.data and result.data.history:
                print(f"Found {len(result.data.history)} username changes:")
                for entry in result.data.history[:5]:
                    print(f"  - {entry}")
            else:
                print("No username history found")
        except (NotFoundError, ValidationError) as e:
            print(f"Error: {e}")

        # Discord to Roblox
        print("\n=== Discord to Roblox ===")
        try:
            result = client.osint.discord_to_roblox("1205957884584656927")
            if result.data:
                print(f"Roblox ID: {result.data.roblox_id}")
                print(f"Roblox Name: {result.data.name}")
                print(f"Display Name: {result.data.displayName}")
        except (NotFoundError, ValidationError) as e:
            print(f"Error: {e}")

        # Steam Profile
        print("\n=== Steam Profile ===")
        try:
            result = client.osint.steam("1100001586a2b38")
            if result.data:
                print(f"Username: {result.data.username}")
                print(f"Profile URL: {getattr(result.data, 'profile_url', 'N/A')}")
                if hasattr(result.data, 'real_name') and result.data.real_name:
                    print(f"Real Name: {result.data.real_name}")
        except (NotFoundError, ValidationError) as e:
            print(f"Error: {e}")

        # Xbox Profile
        print("\n=== Xbox Profile ===")
        try:
            result = client.osint.xbox("ethan")
            if result.data:
                print(f"Gamertag: {result.data.username}")
                print(f"Gamerscore: {getattr(result.data, 'gamerscore', 'N/A')}")
        except (NotFoundError, ValidationError) as e:
            print(f"Error: {e}")

        # Roblox User Info (by username)
        print("\n=== Roblox User Info ===")
        try:
            result = client.osint.roblox_userinfo(username="chris")
            if result.data:
                print(f"User ID: {result.data.user_id}")
                print(f"Username: {result.data.username}")
        except (NotFoundError, ValidationError) as e:
            print(f"Error: {e}")

        # Holehe Email Check
        print("\n=== Holehe Email Check ===")
        try:
            result = client.osint.holehe("ethan_lewis_196@hotmail.co.uk")
            print(f"Email: ethan_lewis_196@hotmail.co.uk")
            if result.data and result.data.domains:
                print(f"Found on {len(result.data.domains)} services:")
                for domain in result.data.domains[:10]:
                    print(f"  - {domain}")
            else:
                print("No registered services found")
        except (NotFoundError, ValidationError) as e:
            print(f"Error: {e}")

        # IP Info
        print("\n=== IP Info ===")
        try:
            result = client.osint.ip_info("174.235.65.156")
            print(f"IP: 174.235.65.156")
            if result.data:
                print(f"Country: {result.data.country}")
                print(f"City: {result.data.city}")
                print(f"Region: {result.data.region}")
                print(f"ISP: {result.data.isp}")
                print(f"ASN: {getattr(result.data, 'asn', 'N/A')}")
        except (NotFoundError, ValidationError) as e:
            print(f"Error: {e}")

        # Subdomain Extraction
        print("\n=== Subdomain Extraction ===")
        try:
            result = client.osint.extract_subdomain("limabean.co.za")
            print(f"Domain: limabean.co.za")
            if result.data:
                print(f"Subdomain count: {result.data.count}")
                if result.data.subdomains:
                    print("Subdomains found:")
                    for sub in result.data.subdomains[:10]:
                        print(f"  - {sub}")
        except (NotFoundError, ValidationError) as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
