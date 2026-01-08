"""OSINT Service - Platform lookups (Discord, Steam, Xbox, etc.)."""

from typing import TYPE_CHECKING

from ..models import (
    DiscordToRobloxResponse,
    DiscordUserResponse,
    GHuntResponse,
    HoleleResponse,
    IPInfoResponse,
    MinecraftHistoryResponse,
    RobloxUserResponse,
    SteamResponse,
    SubdomainResponse,
    UsernameHistoryResponse,
    XboxResponse,
)

if TYPE_CHECKING:
    from ..client import OathNetClient


class OSINTService:
    """Service for OSINT lookups.

    Includes lookups for Discord, Steam, Xbox, Roblox, IP, email, and more.
    """

    def __init__(self, client: "OathNetClient"):
        self._client = client

    def ip_info(
        self, ip: str, search_id: str | None = None
    ) -> IPInfoResponse:
        """Get IP address information.

        Retrieves geolocation and network info for an IP address.

        Args:
            ip: IP address to lookup
            search_id: Optional search session ID

        Returns:
            IPInfoResponse with geolocation, ISP, and network details

        Example:
            >>> info = client.osint.ip_info("174.235.65.156")
            >>> print(f"{info.data.city}, {info.data.country}")
        """
        data = self._client.get(
            "/service/ip-info",
            params={"ip": ip, "search_id": search_id},
        )
        return IPInfoResponse.model_validate(data)

    def steam(
        self, steam_id: str, search_id: str | None = None
    ) -> SteamResponse:
        """Get Steam profile information.

        Args:
            steam_id: Steam64 ID or custom URL name
            search_id: Optional search session ID

        Returns:
            SteamResponse with profile details

        Example:
            >>> profile = client.osint.steam("1100001586a2b38")
            >>> print(profile.data.username)
        """
        data = self._client.get(
            "/service/steam",
            params={"steam_id": steam_id, "search_id": search_id},
        )
        return SteamResponse.model_validate(data)

    def xbox(
        self, xbl_id: str, search_id: str | None = None
    ) -> XboxResponse:
        """Get Xbox Live profile information.

        Args:
            xbl_id: Xbox Live gamertag or XUID
            search_id: Optional search session ID

        Returns:
            XboxResponse with profile details and gamerscore

        Example:
            >>> profile = client.osint.xbox("ethan")
            >>> print(f"Gamerscore: {profile.data.meta.meta.gamerscore}")
        """
        data = self._client.get(
            "/service/xbox",
            params={"xbl_id": xbl_id, "search_id": search_id},
        )
        return XboxResponse.model_validate(data)

    def discord_userinfo(
        self, discord_id: str, search_id: str | None = None
    ) -> DiscordUserResponse:
        """Get Discord user information.

        Args:
            discord_id: Discord user ID (snowflake, 14-19 digits)
            search_id: Optional search session ID

        Returns:
            DiscordUserResponse with username, avatar, creation date, badges

        Example:
            >>> user = client.osint.discord_userinfo("300760994454437890")
            >>> print(f"{user.data.username} created on {user.data.creation_date}")
        """
        data = self._client.get(
            "/service/discord-userinfo",
            params={"discord_id": discord_id, "search_id": search_id},
        )
        return DiscordUserResponse.model_validate(data)

    def discord_username_history(
        self, discord_id: str, search_id: str | None = None
    ) -> UsernameHistoryResponse:
        """Get Discord username history.

        Retrieves historical usernames for a Discord user.

        Args:
            discord_id: Discord user ID (snowflake, 14-19 digits)
            search_id: Optional search session ID

        Returns:
            UsernameHistoryResponse with history array

        Example:
            >>> history = client.osint.discord_username_history("1375046349392974005")
            >>> for entry in history.data.history:
            ...     print(f"{entry.name[0]} at {entry.time[0]}")
        """
        data = self._client.get(
            "/service/discord-username-history",
            params={"discord_id": discord_id, "search_id": search_id},
        )
        return UsernameHistoryResponse.model_validate(data)

    def discord_to_roblox(
        self, discord_id: str, search_id: str | None = None
    ) -> DiscordToRobloxResponse:
        """Get Roblox account linked to Discord.

        Finds Roblox account linked to Discord user ID.

        Args:
            discord_id: Discord user ID (snowflake, 14-19 digits)
            search_id: Optional search session ID

        Returns:
            DiscordToRobloxResponse with Roblox profile

        Example:
            >>> mapping = client.osint.discord_to_roblox("1205957884584656927")
            >>> print(f"Roblox ID: {mapping.data.roblox_id}")
        """
        data = self._client.get(
            "/service/discord-to-roblox",
            params={"discord_id": discord_id, "search_id": search_id},
        )
        return DiscordToRobloxResponse.model_validate(data)

    def roblox_userinfo(
        self,
        user_id: str | None = None,
        username: str | None = None,
        search_id: str | None = None,
    ) -> RobloxUserResponse:
        """Get Roblox user information.

        Provide either user_id OR username.

        Args:
            user_id: Roblox user ID
            username: Roblox username
            search_id: Optional search session ID

        Returns:
            RobloxUserResponse with profile details

        Example:
            >>> user = client.osint.roblox_userinfo(username="chris")
            >>> print(f"User ID: {user.data.user_id}")
        """
        params = {"search_id": search_id}
        if user_id:
            params["user_id"] = user_id
        if username:
            params["username"] = username

        data = self._client.get("/service/roblox-userinfo", params=params)
        return RobloxUserResponse.model_validate(data)

    def holehe(
        self, email: str, search_id: str | None = None
    ) -> HoleleResponse:
        """Check email account existence across services.

        Uses holehe to check which services have accounts for an email.

        Args:
            email: Email address to check
            search_id: Optional search session ID

        Returns:
            HoleleResponse with list of services (domains)

        Example:
            >>> result = client.osint.holehe("user@example.com")
            >>> print(f"Found accounts on: {result.data.domains}")
        """
        data = self._client.get(
            "/service/holehe",
            params={"email": email, "search_id": search_id},
        )
        return HoleleResponse.model_validate(data)

    def ghunt(
        self, email: str, search_id: str | None = None
    ) -> GHuntResponse:
        """Get Google account information.

        Retrieves public Google account info using GHunt.

        Note: May return error if OSID header not detected.

        Args:
            email: Gmail address
            search_id: Optional search session ID

        Returns:
            GHuntResponse with Google profile data

        Example:
            >>> result = client.osint.ghunt("user@gmail.com")
            >>> if result.success:
            ...     print(result.data.data)
        """
        data = self._client.get(
            "/service/ghunt",
            params={"email": email, "search_id": search_id},
        )
        return GHuntResponse.model_validate(data)

    def extract_subdomain(
        self,
        domain: str,
        is_alive: bool = False,
        search_id: str | None = None,
    ) -> SubdomainResponse:
        """Extract subdomains for a domain.

        Extracts known subdomains for a domain.

        Args:
            domain: Domain to search
            is_alive: Only return alive (HTTP responsive) subdomains
            search_id: Optional search session ID

        Returns:
            SubdomainResponse with list of subdomains

        Example:
            >>> result = client.osint.extract_subdomain("example.com")
            >>> print(f"Found {result.data.count} subdomains")
        """
        data = self._client.get(
            "/service/extract-subdomain",
            params={
                "domain": domain,
                "is_alive": is_alive if is_alive else None,
                "search_id": search_id,
            },
        )
        return SubdomainResponse.model_validate(data)

    def minecraft_history(
        self, username: str, search_id: str | None = None
    ) -> MinecraftHistoryResponse:
        """Get Minecraft username history.

        Retrieves username history for a Minecraft account.

        Note: This endpoint may be unavailable due to upstream API issues.

        Args:
            username: Minecraft username
            search_id: Optional search session ID

        Returns:
            MinecraftHistoryResponse with UUID and history

        Example:
            >>> result = client.osint.minecraft_history("Notch")
            >>> print(f"UUID: {result.data.uuid}")
        """
        data = self._client.get(
            "/service/mc-history",
            params={"username": username, "search_id": search_id},
        )
        return MinecraftHistoryResponse.model_validate(data)
