# OathNet Python SDK

Official Python SDK and CLI for the OathNet API.

## Installation

```bash
pip install oathnet
```

Or install from source:

```bash
pip install -e .
```

## Quick Start

### SDK Usage

```python
from oathnet import OathNetClient

# Initialize client
client = OathNetClient("your-api-key")

# Search breach database
results = client.search.breach("user@example.com")
print(f"Found {results.data.results_found} results")

for result in results.data.results:
    print(f"  {result.email} from {result.dbname}")

# OSINT lookups
discord_user = client.osint.discord_userinfo("300760994454437890")
print(f"Discord user: {discord_user.data.username}")

ip_info = client.osint.ip_info("174.235.65.156")
print(f"IP location: {ip_info.data.city}, {ip_info.data.country}")
```

### CLI Usage

```bash
# Set API key
export OATHNET_API_KEY="your-api-key"

# Search breach database
oathnet search breach -q "user@example.com"

# OSINT lookups
oathnet osint discord user 300760994454437890
oathnet osint ip 174.235.65.156
oathnet osint steam 1100001586a2b38

# Output as JSON
oathnet --format json search breach -q "winterfox"
```

## Features

### Search Services
- **Breach Search**: Search leaked credentials across 50B+ records
- **Stealer Search**: Search stealer log databases
- **Search Sessions**: Optimize quota with grouped lookups

### V2 Services
- **V2 Stealer**: Enhanced stealer search with filtering
- **V2 Victims**: Search victim profiles with device info
- **V2 File Search**: Regex search within victim files
- **V2 Exports**: Export results to CSV/JSONL

### OSINT Lookups
- Discord (user info, username history, linked Roblox)
- Steam profiles
- Xbox Live profiles
- Roblox user info
- IP geolocation
- Email existence (Holehe)
- Google accounts (GHunt)
- Subdomain extraction
- Minecraft username history

## SDK Reference

### Client

```python
from oathnet import OathNetClient

client = OathNetClient(
    api_key="your-api-key",
    base_url="https://oathnet.org/api",  # Optional
    timeout=30.0  # Optional
)
```

### Services

#### Search

```python
# Initialize search session
session = client.search.init_session("query")

# Search breach database
results = client.search.breach("query", cursor=None, dbnames="linkedin")

# Search stealer database
results = client.search.stealer("query")

# Paginate through all results
for result in client.search.breach_paginate("query"):
    print(result)
```

#### OSINT

```python
# IP lookup
info = client.osint.ip_info("8.8.8.8")

# Steam profile
profile = client.osint.steam("steam_id")

# Xbox profile
profile = client.osint.xbox("gamertag")

# Discord user
user = client.osint.discord_userinfo("discord_id")

# Discord username history
history = client.osint.discord_username_history("discord_id")

# Discord to Roblox
mapping = client.osint.discord_to_roblox("discord_id")

# Roblox user
user = client.osint.roblox_userinfo(username="username")

# Holehe email check
result = client.osint.holehe("email@example.com")

# Subdomain extraction
result = client.osint.extract_subdomain("example.com")
```

#### V2 Stealer

```python
# Enhanced search with filters
results = client.stealer.search(
    q="query",
    domain=["facebook.com"],
    has_log_id=True
)

# Extract subdomains from stealer data
subs = client.stealer.subdomain("example.com")
```

#### V2 Victims

```python
# Search victim profiles
victims = client.victims.search(
    q="query",
    email=["user@gmail.com"]
)

# Get file manifest
manifest = client.victims.get_manifest("log_id")

# Download file
content = client.victims.get_file("log_id", "file_id")

# Download archive
client.victims.download_archive("log_id", "output.zip")
```

#### File Search (Async)

```python
# Create search job
job = client.file_search.create("password", search_mode="regex")

# Wait for results
result = client.file_search.wait_for_completion(job.data.job_id)

# Or use convenience method
result = client.file_search.search("api_key", search_mode="literal")
```

#### Exports (Async)

```python
# Create export
job = client.exports.create(
    export_type="docs",
    format="csv",
    search={"query": "example.com"}
)

# Wait and download
path = client.exports.wait_and_download(job.data.job_id, "export.csv")
```

### Error Handling

```python
from oathnet import OathNetClient
from oathnet.exceptions import (
    AuthenticationError,
    NotFoundError,
    QuotaExceededError,
    ValidationError
)

try:
    results = client.search.breach("query")
except AuthenticationError:
    print("Invalid API key")
except QuotaExceededError as e:
    print(f"Quota exceeded: {e.used_today}/{e.daily_limit}")
except NotFoundError:
    print("Resource not found")
except ValidationError as e:
    print(f"Invalid parameters: {e.errors}")
```

## CLI Reference

```bash
# Global options
oathnet --api-key KEY --format json|table|raw COMMAND

# Search commands
oathnet search breach -q "query" [--cursor] [--dbnames]
oathnet search stealer -q "query"
oathnet search init -q "query"

# Stealer V2
oathnet stealer search -q "query" [--domain] [--wildcard]
oathnet stealer subdomain -d "domain.com"

# Victims V2
oathnet victims search -q "query" [--email] [--ip]
oathnet victims manifest LOG_ID
oathnet victims file LOG_ID FILE_ID
oathnet victims archive LOG_ID

# OSINT
oathnet osint ip IP_ADDRESS
oathnet osint steam STEAM_ID
oathnet osint xbox GAMERTAG
oathnet osint discord user DISCORD_ID
oathnet osint discord history DISCORD_ID
oathnet osint discord roblox DISCORD_ID
oathnet osint roblox [--user-id ID | --username NAME]
oathnet osint holehe EMAIL
oathnet osint ghunt EMAIL
oathnet osint subdomain DOMAIN
oathnet osint minecraft USERNAME

# Utility
oathnet util dbnames -q "linked"
```

## Configuration

API key can be set via:

1. CLI flag: `--api-key KEY`
2. Environment variable: `OATHNET_API_KEY`

## Examples

The `examples/` directory contains comprehensive examples for common use cases:

| Example | Description |
|---------|-------------|
| `basic_usage.py` | Client initialization and simple search |
| `breach_search.py` | Breach search with filters and pagination |
| `stealer_search.py` | V2 stealer search with log ID access |
| `victims_search.py` | Victim profiles, manifests, and file access |
| `file_search.py` | Async file search within victim logs |
| `osint_lookups.py` | All 12 OSINT methods demonstrated |
| `exports.py` | Async export to CSV/JSONL |
| `error_handling.py` | Exception patterns and retry logic |
| `pagination.py` | Cursor-based pagination patterns |

Run an example:

```bash
export OATHNET_API_KEY="your-api-key"
python examples/basic_usage.py
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests (requires API key)
export OATHNET_API_KEY="your-api-key"
pytest tests/ -v

# Run specific test file
pytest tests/test_sdk.py -v

# Run specific test class
pytest tests/test_sdk.py::TestOSINTService -v

# Run with coverage
pytest tests/ -v --cov=oathnet --cov-report=html

# Run only fast tests (skip slow integration tests)
pytest tests/ -v -m "not slow"
```

### Test Structure

```
tests/
  conftest.py              # Fixtures (API key from env)
  test_sdk.py              # Core SDK tests
  test_file_search_service.py  # File search tests
  test_exports_service.py  # Export tests
```

## License

MIT License - See LICENSE file for details.

## Support

- Documentation: https://docs.oathnet.org
- Discord: https://discord.gg/DCjnk9TAMK
- Email: info@oathnet.org
