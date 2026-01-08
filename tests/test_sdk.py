"""Comprehensive tests for OathNet SDK.

These tests use the real API with known working queries.
"""

import pytest

from oathnet import OathNetClient
from oathnet.exceptions import AuthenticationError, NotFoundError, ValidationError


class TestClientInitialization:
    """Test client initialization."""

    def test_client_requires_api_key(self):
        """Client should require API key."""
        with pytest.raises(ValueError):
            OathNetClient("")

    def test_client_with_api_key(self, api_key):
        """Client should initialize with API key."""
        client = OathNetClient(api_key)
        assert client.api_key == api_key

    def test_client_context_manager(self, api_key):
        """Client should work as context manager."""
        with OathNetClient(api_key) as client:
            assert client.api_key == api_key


class TestSearchService:
    """Test search service endpoints."""

    def test_breach_search(self, client: OathNetClient):
        """Test breach search with known query."""
        result = client.search.breach("winterfox")
        assert result.success is True
        assert result.data is not None
        assert result.data.results_found >= 0

    def test_breach_search_with_results(self, client: OathNetClient):
        """Test breach search returns results."""
        result = client.search.breach("winterfox")
        if result.data.results:
            first = result.data.results[0]
            # Should have some common fields
            assert hasattr(first, "dbname") or hasattr(first, "email")

    def test_stealer_search(self, client: OathNetClient):
        """Test stealer search with known query."""
        result = client.search.stealer("diddy")
        assert result.success is True
        assert result.data is not None
        assert result.data.results_found >= 0

    def test_stealer_search_has_log_field(self, client: OathNetClient):
        """Test stealer results have LOG field."""
        result = client.search.stealer("diddy")
        if result.data.results:
            first = result.data.results[0]
            assert hasattr(first, "LOG")

    def test_init_session(self, client: OathNetClient):
        """Test search session initialization."""
        result = client.search.init_session("test@example.com")
        assert result.success is True
        assert result.data is not None
        assert result.data.session.id is not None


class TestOSINTService:
    """Test OSINT service endpoints."""

    def test_discord_userinfo(self, client: OathNetClient):
        """Test Discord user lookup."""
        result = client.osint.discord_userinfo("300760994454437890")
        assert result.success is True
        assert result.data is not None
        assert result.data.username is not None

    def test_discord_username_history(self, client: OathNetClient):
        """Test Discord username history."""
        result = client.osint.discord_username_history("1375046349392974005")
        assert result.success is True
        assert result.data is not None
        # History may or may not exist

    def test_discord_to_roblox(self, client: OathNetClient):
        """Test Discord to Roblox mapping."""
        result = client.osint.discord_to_roblox("1205957884584656927")
        assert result.success is True
        assert result.data is not None
        assert result.data.roblox_id is not None

    def test_steam_profile(self, client: OathNetClient):
        """Test Steam profile lookup."""
        result = client.osint.steam("1100001586a2b38")
        assert result.success is True
        assert result.data is not None
        assert result.data.username is not None

    def test_xbox_profile(self, client: OathNetClient):
        """Test Xbox profile lookup."""
        result = client.osint.xbox("ethan")
        assert result.success is True
        assert result.data is not None
        assert result.data.username is not None

    def test_roblox_userinfo_by_username(self, client: OathNetClient):
        """Test Roblox user lookup by username."""
        result = client.osint.roblox_userinfo(username="chris")
        assert result.success is True
        assert result.data is not None
        assert result.data.user_id is not None

    def test_holehe(self, client: OathNetClient):
        """Test Holehe email check."""
        result = client.osint.holehe("ethan_lewis_196@hotmail.co.uk")
        assert result.success is True
        assert result.data is not None
        # domains may be empty or have entries

    def test_ip_info(self, client: OathNetClient):
        """Test IP info lookup."""
        result = client.osint.ip_info("174.235.65.156")
        assert result.success is True
        assert result.data is not None
        assert result.data.country is not None
        assert result.data.city is not None

    def test_extract_subdomain(self, client: OathNetClient):
        """Test subdomain extraction."""
        result = client.osint.extract_subdomain("limabean.co.za")
        assert result.success is True
        assert result.data is not None
        # count should be >= 0


class TestUtilityService:
    """Test utility service endpoints."""

    def test_dbname_autocomplete(self, client: OathNetClient):
        """Test database name autocomplete."""
        result = client.utility.dbname_autocomplete("linkedin")
        assert isinstance(result, list)
        # Should have some results (may or may not include linkedin depending on API)
        # Just verify the response is a list


class TestErrorHandling:
    """Test error handling."""

    def test_invalid_api_key(self):
        """Test invalid API key raises AuthenticationError."""
        client = OathNetClient("invalid_key")
        with pytest.raises((AuthenticationError, ValidationError)):
            # API may return different errors for invalid keys
            client.search.breach("test")

    def test_invalid_discord_id_format(self, client: OathNetClient):
        """Test invalid Discord ID raises error."""
        with pytest.raises((ValidationError, NotFoundError)):
            client.osint.discord_userinfo("123")  # Too short

    def test_no_results_search(self, client: OathNetClient):
        """Test search with no results."""
        # Note: API may return ValidationError with "No results found"
        # or return success with empty results depending on query
        try:
            result = client.search.breach("xyznonexistent123456789abcdef")
            # If we get here, check the response
            assert result.data.results_found == 0 or len(result.data.results) == 0
        except ValidationError as e:
            # API returns "No results found" as error for some queries
            assert "no results" in str(e).lower()


class TestStealerV2Service:
    """Test V2 stealer service."""

    def test_v2_stealer_search(self, client: OathNetClient):
        """Test V2 stealer search."""
        result = client.stealer.search(q="gmail.com", page_size=5)
        assert result.success is True
        assert result.data is not None

    def test_v2_stealer_subdomain(self, client: OathNetClient):
        """Test V2 stealer subdomain extraction."""
        result = client.stealer.subdomain(domain="google.com")
        assert result.success is True
        assert result.data is not None


class TestVictimsService:
    """Test V2 victims service."""

    def test_victims_search(self, client: OathNetClient):
        """Test victims search."""
        result = client.victims.search(q="gmail", page_size=5)
        assert result.success is True
        assert result.data is not None


class TestBulkService:
    """Test bulk search service."""

    def test_bulk_list_jobs(self, client: OathNetClient):
        """Test listing bulk jobs."""
        try:
            result = client.bulk.list_jobs()
            # Should return list structure
            assert hasattr(result, "results")
        except (ValidationError, AuthenticationError):
            # Bulk search may require special permissions or different auth
            pytest.skip("Bulk search not available with current API key")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
