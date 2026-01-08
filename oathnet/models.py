"""OathNet SDK Pydantic Models."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ============================================
# COMMON META MODELS
# ============================================


class UserMeta(BaseModel):
    """User plan information."""

    plan: str | None = None
    plan_type: str | None = None
    is_plan_active: bool | None = None


class LookupsMeta(BaseModel):
    """Lookup quota information."""

    used_today: int | None = None
    left_today: int | None = None
    daily_limit: int | None = None
    is_unlimited: bool | None = None


class ServiceMeta(BaseModel):
    """Service information."""

    name: str | None = None
    id: str | None = None
    category: str | None = None
    is_premium: bool | None = None
    is_available: bool | None = None
    session_quota: int | None = None


class PerformanceMeta(BaseModel):
    """Performance metrics."""

    duration_ms: float | None = None
    timestamp: str | None = None


class ResponseMeta(BaseModel):
    """Full response metadata."""

    user: UserMeta | None = None
    lookups: LookupsMeta | None = None
    service: ServiceMeta | None = None
    performance: PerformanceMeta | None = None


# ============================================
# SEARCH SESSION
# ============================================


class SessionInfo(BaseModel):
    """Search session information."""

    id: str
    query: str
    search_type: str | None = None
    status: str | None = None
    created_at: str | None = None
    expires_at: str | None = None
    duration_minutes: int | None = None


class DailyLookups(BaseModel):
    """Daily lookup information."""

    used: int | None = None
    remaining: int | None = None
    limit: int | None = None
    is_unlimited: bool | None = None


class SessionUser(BaseModel):
    """User info in session response."""

    plan: str | None = None
    plan_type: str | None = None
    daily_lookups: DailyLookups | None = None


class ServiceInfo(BaseModel):
    """Service availability info."""

    name: str | None = None
    service_id: str | None = None
    category: str | None = None
    is_available: bool | None = None
    is_premium: bool | None = None
    session_quota: int | None = None
    today_usage: int | None = None
    recommended_quota: int | None = None


class SessionSummary(BaseModel):
    """Session summary."""

    total_services: int | None = None
    available_services: int | None = None
    session_expires_in_minutes: int | None = None


class SearchSessionData(BaseModel):
    """Search session response data."""

    session: SessionInfo
    user: SessionUser | None = None
    services: dict[str, ServiceInfo] | None = None
    summary: SessionSummary | None = None


class SearchSessionResponse(BaseModel):
    """Full search session response."""

    success: bool
    message: str | None = None
    data: SearchSessionData


# ============================================
# BREACH SEARCH
# ============================================


class BreachResult(BaseModel):
    """Single breach result - fields vary by source."""

    model_config = {"extra": "allow"}

    dbname: str | None = None
    email: str | None = None
    username: str | list[str] | None = None
    password: str | None = None
    ip: str | None = None
    domain: str | None = None
    date: str | None = None
    country: str | list[str] | None = None
    id: str | None = None


class BreachSearchData(BaseModel):
    """Breach search response data."""

    results: list[BreachResult] = []
    results_found: int = 0
    results_shown: int = 0
    nextCursorMark: str | None = Field(None, alias="nextCursorMark")
    next_cursor_mark: str | None = None
    _meta: ResponseMeta | None = None

    @property
    def cursor(self) -> str | None:
        """Get pagination cursor."""
        return self.nextCursorMark or self.next_cursor_mark


class BreachSearchResponse(BaseModel):
    """Full breach search response."""

    success: bool
    message: str | None = None
    data: BreachSearchData | None = None


# ============================================
# LEGACY STEALER SEARCH
# ============================================


class StealerResult(BaseModel):
    """Single legacy stealer result."""

    model_config = {"extra": "allow"}

    id: str | None = None
    LOG: str | None = None
    domain: list[str] | None = None
    subdomain: list[str] | None = None
    path: list[str] | None = None
    email: list[str] | None = None


class StealerSearchData(BaseModel):
    """Stealer search response data."""

    results: list[StealerResult] = []
    results_found: int = 0
    results_shown: int = 0
    nextCursorMark: str | None = None
    _meta: ResponseMeta | None = None

    @property
    def cursor(self) -> str | None:
        return self.nextCursorMark


class StealerSearchResponse(BaseModel):
    """Full stealer search response."""

    success: bool
    message: str | None = None
    data: StealerSearchData | None = None


# ============================================
# V2 STEALER SEARCH
# ============================================


class V2StealerItem(BaseModel):
    """V2 stealer search item."""

    model_config = {"extra": "allow"}

    id: str | None = None
    log_id: str | None = None
    url: str | None = None
    domain: list[str] | None = None
    subdomain: list[str] | None = None
    path: list[str] | None = None
    username: str | None = None
    password: str | None = None
    email: list[str] | None = None
    log: str | None = None
    pwned_at: str | None = None
    indexed_at: str | None = None


class V2SearchMeta(BaseModel):
    """V2 search metadata."""

    count: int | None = None
    total: int | None = None
    took_ms: int | None = None
    has_more: bool | None = None
    total_pages: int | None = None
    max_score: float | None = None


class V2StealerData(BaseModel):
    """V2 stealer search response data."""

    items: list[V2StealerItem] = []
    meta: V2SearchMeta | None = None
    next_cursor: str | None = None
    _meta: ResponseMeta | None = None


class V2StealerResponse(BaseModel):
    """Full V2 stealer response."""

    success: bool
    message: str | None = None
    data: V2StealerData | None = None


# ============================================
# V2 SUBDOMAIN
# ============================================


class SubdomainData(BaseModel):
    """Subdomain extraction data."""

    domain: str | None = None
    subdomains: list[str] = []
    count: int = 0
    _meta: ResponseMeta | None = None


class SubdomainResponse(BaseModel):
    """Full subdomain response."""

    success: bool
    message: str | None = None
    data: SubdomainData | None = None


# ============================================
# V2 VICTIMS
# ============================================


class V2VictimItem(BaseModel):
    """V2 victim search item."""

    model_config = {"extra": "allow"}

    log_id: str | None = None
    device_users: list[str] | None = None
    hwids: list[str] | None = None
    device_ips: list[str] | None = None
    device_emails: list[str] | None = None
    discord_ids: list[str] | None = None
    total_docs: int | None = None
    pwned_at: str | None = None
    indexed_at: str | None = None


class V2VictimsData(BaseModel):
    """V2 victims search response data."""

    items: list[V2VictimItem] = []
    meta: V2SearchMeta | None = None
    next_cursor: str | None = None
    _meta: ResponseMeta | None = None


class V2VictimsResponse(BaseModel):
    """Full V2 victims response."""

    success: bool
    message: str | None = None
    data: V2VictimsData | None = None


# ============================================
# V2 VICTIM MANIFEST
# ============================================


class ManifestNode(BaseModel):
    """File tree node."""

    id: str | None = None
    name: str | None = None
    type: str | None = None  # "file" or "directory"
    size_bytes: int | None = None
    children: list["ManifestNode"] | None = None


class ManifestData(BaseModel):
    """Victim manifest data."""

    log_id: str | None = None
    log_name: str | None = None
    victim_tree: ManifestNode | None = None
    _meta: ResponseMeta | None = None


class ManifestResponse(BaseModel):
    """Full manifest response."""

    success: bool
    message: str | None = None
    data: ManifestData | None = None


# ============================================
# V2 FILE CONTENT
# ============================================


class FileContentData(BaseModel):
    """File content data."""

    content: str | None = None
    size: int | None = None
    lines: int | None = None
    _meta: ResponseMeta | None = None


class FileContentResponse(BaseModel):
    """Full file content response."""

    success: bool
    message: str | None = None
    data: FileContentData | None = None


# ============================================
# V2 FILE SEARCH JOB
# ============================================


class FileSearchLimits(BaseModel):
    """File search job limits."""

    byte_budget_bytes: int | None = None
    job_ttl_seconds: int | None = None
    max_context_lines: int | None = None
    max_expression_length: int | None = None
    max_file_size_bytes: int | None = None
    max_log_ids: int | None = None
    max_matches: int | None = None


class FileSearchSummary(BaseModel):
    """File search summary."""

    files_scanned: int | None = None
    files_total: int | None = None
    files_matched: int | None = None
    matches: int | None = None
    bytes_scanned: int | None = None
    duration_ms: int | None = None
    budget_exceeded: bool | None = None
    truncated: bool | None = None
    timeouts: int | None = None


class FileSearchMatch(BaseModel):
    """Single file search match."""

    log_id: str | None = None
    file_id: str | None = None
    file_name: str | None = None
    relative_path: str | None = None
    size_bytes: int | None = None
    match_text: str | None = None
    line_number: int | None = None


class FileSearchJobData(BaseModel):
    """File search job data."""

    job_id: str | None = None
    status: str | None = None  # queued, running, completed, canceled
    created_at: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    expires_at: str | None = None
    next_poll_after_ms: int | None = None
    limits: FileSearchLimits | None = None
    summary: FileSearchSummary | None = None
    matches: list[FileSearchMatch] | None = None
    progress: dict[str, Any] | None = None
    _meta: ResponseMeta | None = None


class FileSearchJobResponse(BaseModel):
    """Full file search job response."""

    success: bool
    message: str | None = None
    data: FileSearchJobData | None = None


# ============================================
# V2 EXPORT JOB
# ============================================


class ExportProgress(BaseModel):
    """Export job progress."""

    records_done: int | None = None
    records_total: int | None = None
    bytes_done: int | None = None
    percent: float | None = None
    updated_at: str | None = None


class ExportResult(BaseModel):
    """Export job result."""

    ready_at: str | None = None
    expires_at: str | None = None
    file_name: str | None = None
    file_path: str | None = None
    file_size: int | None = None
    format: str | None = None
    records: int | None = None


class ExportJobData(BaseModel):
    """Export job data."""

    job_id: str | None = None
    status: str | None = None  # queued, running, completed, canceled
    progress: ExportProgress | None = None
    result: ExportResult | None = None
    metadata: dict[str, Any] | None = None
    created_at: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    expires_at: str | None = None
    next_poll_after_ms: int | None = None
    _meta: ResponseMeta | None = None


class ExportJobResponse(BaseModel):
    """Full export job response."""

    success: bool
    message: str | None = None
    data: ExportJobData | None = None


# ============================================
# OSINT - IP INFO
# ============================================


class IPInfoData(BaseModel):
    """IP info data."""

    model_config = {"extra": "allow"}

    status: str | None = None
    query: str | None = None
    continent: str | None = None
    continentCode: str | None = None
    country: str | None = None
    countryCode: str | None = None
    region: str | None = None
    regionName: str | None = None
    city: str | None = None
    district: str | None = None
    zip: str | None = None
    lat: float | None = None
    lon: float | None = None
    timezone: str | None = None
    offset: int | None = None
    currency: str | None = None
    isp: str | None = None
    org: str | None = None
    asname: str | None = Field(None, alias="as")
    mobile: bool | None = None
    proxy: bool | None = None
    hosting: bool | None = None
    reverse: str | None = None
    _meta: ResponseMeta | None = None


class IPInfoResponse(BaseModel):
    """Full IP info response."""

    success: bool
    message: str | None = None
    data: IPInfoData | None = None


# ============================================
# OSINT - STEAM
# ============================================


class SteamRawData(BaseModel):
    """Raw Steam API data."""

    model_config = {"extra": "allow"}

    steamid: str | None = None
    personaname: str | None = None
    profileurl: str | None = None
    avatar: str | None = None
    avatarmedium: str | None = None
    avatarfull: str | None = None
    personastate: int | None = None
    timecreated: int | None = None


class SteamMeta(BaseModel):
    """Steam meta data."""

    username: str | None = None
    id: str | None = None
    avatar: str | None = None
    raw_data: SteamRawData | None = None
    source: str | None = None


class SteamData(BaseModel):
    """Steam profile data."""

    username: str | None = None
    id: str | None = None
    avatar: str | None = None
    meta: SteamMeta | None = None
    _meta: ResponseMeta | None = None


class SteamResponse(BaseModel):
    """Full Steam response."""

    success: bool
    message: str | None = None
    data: SteamData | None = None


# ============================================
# OSINT - XBOX
# ============================================


class XboxMetaInfo(BaseModel):
    """Xbox meta information."""

    model_config = {"extra": "allow"}

    gamerscore: str | None = None
    accounttier: str | None = None
    xboxonerep: str | None = None
    realname: str | None = None
    bio: str | None = None
    location: str | None = None


class XboxScraperData(BaseModel):
    """Xbox scraper data."""

    background_picture_url: str | None = None
    gamerscore: int | None = None
    games_played: int | None = None
    game_history: list[dict[str, Any]] | None = None


class XboxMeta(BaseModel):
    """Xbox meta data."""

    id: str | None = None
    username: str | None = None
    avatar: str | None = None
    meta: XboxMetaInfo | None = None
    cached_at: int | None = None
    scraper_data: XboxScraperData | None = None


class XboxData(BaseModel):
    """Xbox profile data."""

    username: str | None = None
    id: str | None = None
    avatar: str | None = None
    meta: XboxMeta | None = None
    _meta: ResponseMeta | None = None


class XboxResponse(BaseModel):
    """Full Xbox response."""

    success: bool
    message: str | None = None
    data: XboxData | None = None


# ============================================
# OSINT - DISCORD USER INFO
# ============================================


class DiscordUserData(BaseModel):
    """Discord user data."""

    id: str | None = None
    username: str | None = None
    global_name: str | None = None
    avatar_url: str | None = None
    banner_url: str | None = None
    creation_date: str | None = None
    badges: list[str] | None = None
    _meta: ResponseMeta | None = None


class DiscordUserResponse(BaseModel):
    """Full Discord user response."""

    success: bool
    message: str | None = None
    data: DiscordUserData | None = None


# ============================================
# OSINT - DISCORD USERNAME HISTORY
# ============================================


class UsernameHistoryEntry(BaseModel):
    """Single username history entry."""

    name: list[str] | None = None
    time: list[str] | None = None


class UsernameHistoryData(BaseModel):
    """Username history data."""

    success: bool | None = None
    message: str | None = None
    history: list[UsernameHistoryEntry] | None = None
    lookups_left: int | None = None
    _meta: ResponseMeta | None = None


class UsernameHistoryResponse(BaseModel):
    """Full username history response."""

    success: bool
    message: str | None = None
    data: UsernameHistoryData | None = None


# ============================================
# OSINT - DISCORD TO ROBLOX
# ============================================


class DiscordToRobloxData(BaseModel):
    """Discord to Roblox mapping data."""

    roblox_id: str | None = None
    name: str | None = None
    displayName: str | None = None
    created: str | None = None
    description: str | None = None
    avatar: str | None = None
    badges: list[str] | None = None
    groupCount: int | None = None
    _meta: ResponseMeta | None = None


class DiscordToRobloxResponse(BaseModel):
    """Full Discord to Roblox response."""

    success: bool
    message: str | None = None
    data: DiscordToRobloxData | None = None


# ============================================
# OSINT - ROBLOX USER INFO
# ============================================


class RobloxUserData(BaseModel):
    """Roblox user data."""

    model_config = {"extra": "allow"}

    username: str | None = None
    user_id: str | None = None
    Discord: str | None = None
    _meta: ResponseMeta | None = None

    # Alternative field names from API
    current_username: str | None = Field(None, alias="Current Username")
    old_usernames: str | None = Field(None, alias="Old Usernames")
    display_name: str | None = Field(None, alias="Display Name")
    user_id_alt: str | None = Field(None, alias="User ID")
    join_date: str | None = Field(None, alias="Join Date")
    avatar_url: str | None = Field(None, alias="Avatar URL")


class RobloxUserResponse(BaseModel):
    """Full Roblox user response."""

    success: bool
    message: str | None = None
    data: RobloxUserData | None = None


# ============================================
# OSINT - HOLEHE
# ============================================


class HoleleData(BaseModel):
    """Holehe data."""

    domains: list[str] = []
    _meta: ResponseMeta | None = None


class HoleleResponse(BaseModel):
    """Full Holehe response."""

    success: bool
    message: str | None = None
    data: HoleleData | None = None


# ============================================
# OSINT - GHUNT
# ============================================


class GHuntProfile(BaseModel):
    """GHunt profile data."""

    model_config = {"extra": "allow"}

    Name: str | None = None


class GHuntData(BaseModel):
    """GHunt data."""

    model_config = {"extra": "allow"}

    status: str | None = None
    data: dict[str, Any] | None = None
    _meta: ResponseMeta | None = None


class GHuntResponse(BaseModel):
    """Full GHunt response."""

    success: bool
    message: str | None = None
    data: GHuntData | None = None
    errors: dict[str, Any] | None = None


# ============================================
# OSINT - MINECRAFT HISTORY
# ============================================


class MinecraftHistoryEntry(BaseModel):
    """Minecraft username history entry."""

    username: str | None = None
    changed_at: str | None = None


class MinecraftHistoryData(BaseModel):
    """Minecraft history data."""

    uuid: str | None = None
    username: str | None = None
    history: list[MinecraftHistoryEntry] | None = None
    _meta: ResponseMeta | None = None


class MinecraftHistoryResponse(BaseModel):
    """Full Minecraft history response."""

    success: bool
    message: str | None = None
    data: MinecraftHistoryData | None = None


# ============================================
# BULK SEARCH
# ============================================


class BulkSearchJob(BaseModel):
    """Bulk search job."""

    id: str | None = None
    user: str | None = None
    status: str | None = None  # PENDING, IN_PROGRESS, COMPLETED, FAILED
    created_at: str | None = None
    updated_at: str | None = None
    search_service: str | None = None
    output_format: str | None = None
    results_expired: bool | None = None
    query: str | None = None
    results_count: int | None = None
    lookups_deducted: int | None = None


class BulkSearchCreateData(BaseModel):
    """Bulk search create response data."""

    id: str | None = None
    user: str | None = None
    status: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    search_service: str | None = None
    output_format: str | None = None
    results_expired: bool | None = None
    query: str | None = None
    results_count: int | None = None
    lookups_deducted: int | None = None


class BulkSearchCreateResponse(BaseModel):
    """Full bulk search create response."""

    success: bool
    message: str | None = None
    data: BulkSearchCreateData | None = None


class BulkSearchStatusResponse(BaseModel):
    """Full bulk search status response."""

    success: bool
    message: str | None = None
    data: BulkSearchJob | None = None


class BulkSearchListData(BaseModel):
    """Bulk search list data."""

    count: int = 0
    next: str | None = None
    previous: str | None = None
    results: list[BulkSearchJob] = []


class BulkSearchListResponse(BaseModel):
    """Full bulk search list response."""

    # Note: List endpoint returns data directly, not wrapped
    count: int = 0
    next: str | None = None
    previous: str | None = None
    results: list[BulkSearchJob] = []


# ============================================
# UTILITY - DBNAME AUTOCOMPLETE
# ============================================

# Note: dbname-autocomplete endpoint returns a plain list[str], not a wrapped response.
# The UtilityService handles this directly without a model.
