"""OSINT commands for CLI."""

import click

from oathnet import OathNetClient
from oathnet.exceptions import OathNetError

from ..utils import console, error_console, output_result, print_error


def get_client(ctx: click.Context) -> OathNetClient:
    """Get client from context."""
    api_key = ctx.obj.get("api_key")
    if not api_key:
        error_console.print("[red]Error:[/red] API key is required")
        raise click.Abort()
    return OathNetClient(api_key)


@click.group()
def osint() -> None:
    """OSINT lookups (Discord, Steam, Xbox, etc.)."""
    pass


@osint.command("ip")
@click.argument("ip_address")
@click.pass_context
def ip_info(ctx: click.Context, ip_address: str) -> None:
    """Get IP address information.

    Example:
        oathnet osint ip 174.235.65.156
    """
    client = get_client(ctx)
    format = ctx.obj.get("format", "table")

    try:
        result = client.osint.ip_info(ip_address)

        if format == "table":
            if result.data:
                console.print(f"\n[bold]IP Information: {ip_address}[/bold]\n")
                console.print(f"  Country: {result.data.country} ({result.data.countryCode})")
                console.print(f"  Region: {result.data.regionName} ({result.data.region})")
                console.print(f"  City: {result.data.city}")
                console.print(f"  ZIP: {result.data.zip}")
                console.print(f"  Timezone: {result.data.timezone}")
                console.print(f"  ISP: {result.data.isp}")
                console.print(f"  Org: {result.data.org}")
                console.print(f"  Mobile: {result.data.mobile}")
                console.print(f"  Proxy: {result.data.proxy}")
                console.print(f"  Hosting: {result.data.hosting}")
                if result.data.reverse:
                    console.print(f"  Reverse DNS: {result.data.reverse}")
        else:
            output_result(result, format)

    except OathNetError as e:
        print_error(str(e))
        raise click.Abort()


@osint.command("steam")
@click.argument("steam_id")
@click.pass_context
def steam(ctx: click.Context, steam_id: str) -> None:
    """Get Steam profile.

    Example:
        oathnet osint steam 1100001586a2b38
    """
    client = get_client(ctx)
    format = ctx.obj.get("format", "table")

    try:
        result = client.osint.steam(steam_id)

        if format == "table":
            if result.data:
                console.print(f"\n[bold]Steam Profile[/bold]\n")
                console.print(f"  Username: {result.data.username}")
                console.print(f"  ID: {result.data.id}")
                if result.data.avatar:
                    console.print(f"  Avatar: {result.data.avatar}")
                if result.data.meta and result.data.meta.raw_data:
                    raw = result.data.meta.raw_data
                    if raw.profileurl:
                        console.print(f"  Profile URL: {raw.profileurl}")
        else:
            output_result(result, format)

    except OathNetError as e:
        print_error(str(e))
        raise click.Abort()


@osint.command("xbox")
@click.argument("gamertag")
@click.pass_context
def xbox(ctx: click.Context, gamertag: str) -> None:
    """Get Xbox Live profile.

    Example:
        oathnet osint xbox ethan
    """
    client = get_client(ctx)
    format = ctx.obj.get("format", "table")

    try:
        result = client.osint.xbox(gamertag)

        if format == "table":
            if result.data:
                console.print(f"\n[bold]Xbox Profile[/bold]\n")
                console.print(f"  Username: {result.data.username}")
                if result.data.meta:
                    console.print(f"  XUID: {result.data.meta.id}")
                    if result.data.meta.meta:
                        meta = result.data.meta.meta
                        console.print(f"  Gamerscore: {meta.gamerscore}")
                        console.print(f"  Account Tier: {meta.accounttier}")
                        console.print(f"  Reputation: {meta.xboxonerep}")
        else:
            output_result(result, format)

    except OathNetError as e:
        print_error(str(e))
        raise click.Abort()


@osint.group("discord")
def discord() -> None:
    """Discord lookups."""
    pass


@discord.command("user")
@click.argument("discord_id")
@click.pass_context
def discord_user(ctx: click.Context, discord_id: str) -> None:
    """Get Discord user info.

    Example:
        oathnet osint discord user 300760994454437890
    """
    client = get_client(ctx)
    format = ctx.obj.get("format", "table")

    try:
        result = client.osint.discord_userinfo(discord_id)

        if format == "table":
            if result.data:
                console.print(f"\n[bold]Discord User[/bold]\n")
                console.print(f"  ID: {result.data.id}")
                console.print(f"  Username: {result.data.username}")
                console.print(f"  Display Name: {result.data.global_name}")
                console.print(f"  Created: {result.data.creation_date}")
                if result.data.badges:
                    console.print(f"  Badges: {', '.join(result.data.badges)}")
                if result.data.avatar_url:
                    console.print(f"  Avatar: {result.data.avatar_url}")
        else:
            output_result(result, format)

    except OathNetError as e:
        print_error(str(e))
        raise click.Abort()


@discord.command("history")
@click.argument("discord_id")
@click.pass_context
def discord_history(ctx: click.Context, discord_id: str) -> None:
    """Get Discord username history.

    Example:
        oathnet osint discord history 1375046349392974005
    """
    client = get_client(ctx)
    format = ctx.obj.get("format", "table")

    try:
        result = client.osint.discord_username_history(discord_id)

        if format == "table":
            if result.data and result.data.history:
                console.print(f"\n[bold]Username History[/bold]\n")
                for entry in result.data.history:
                    name = entry.name[0] if entry.name else "N/A"
                    time = entry.time[0] if entry.time else "N/A"
                    console.print(f"  {name} - {time}")
            else:
                console.print("[yellow]No history found[/yellow]")
        else:
            output_result(result, format)

    except OathNetError as e:
        print_error(str(e))
        raise click.Abort()


@discord.command("roblox")
@click.argument("discord_id")
@click.pass_context
def discord_roblox(ctx: click.Context, discord_id: str) -> None:
    """Get linked Roblox account from Discord ID.

    Example:
        oathnet osint discord roblox 1205957884584656927
    """
    client = get_client(ctx)
    format = ctx.obj.get("format", "table")

    try:
        result = client.osint.discord_to_roblox(discord_id)

        if format == "table":
            if result.data:
                console.print(f"\n[bold]Linked Roblox Account[/bold]\n")
                console.print(f"  Roblox ID: {result.data.roblox_id}")
                console.print(f"  Name: {result.data.name}")
                console.print(f"  Display Name: {result.data.displayName}")
                if result.data.avatar:
                    console.print(f"  Avatar: {result.data.avatar}")
        else:
            output_result(result, format)

    except OathNetError as e:
        print_error(str(e))
        raise click.Abort()


@osint.command("roblox")
@click.option("--user-id", help="Roblox user ID")
@click.option("--username", help="Roblox username")
@click.pass_context
def roblox(ctx: click.Context, user_id: str | None, username: str | None) -> None:
    """Get Roblox user info.

    Example:
        oathnet osint roblox --username chris
        oathnet osint roblox --user-id 65
    """
    if not user_id and not username:
        error_console.print("[red]Error:[/red] Either --user-id or --username is required")
        raise click.Abort()

    client = get_client(ctx)
    format = ctx.obj.get("format", "table")

    try:
        result = client.osint.roblox_userinfo(user_id=user_id, username=username)

        if format == "table":
            if result.data:
                console.print(f"\n[bold]Roblox User[/bold]\n")
                console.print(f"  Username: {result.data.username}")
                console.print(f"  User ID: {result.data.user_id}")
                if result.data.display_name:
                    console.print(f"  Display Name: {result.data.display_name}")
                if result.data.join_date:
                    console.print(f"  Join Date: {result.data.join_date}")
        else:
            output_result(result, format)

    except OathNetError as e:
        print_error(str(e))
        raise click.Abort()


@osint.command("holehe")
@click.argument("email")
@click.pass_context
def holehe(ctx: click.Context, email: str) -> None:
    """Check email account existence.

    Example:
        oathnet osint holehe user@example.com
    """
    client = get_client(ctx)
    format = ctx.obj.get("format", "table")

    try:
        result = client.osint.holehe(email)

        if format == "table":
            if result.data and result.data.domains:
                console.print(f"\n[bold]Account found on {len(result.data.domains)} services:[/bold]\n")
                for domain in result.data.domains:
                    console.print(f"  • {domain}")
            else:
                console.print("[yellow]No accounts found[/yellow]")
        else:
            output_result(result, format)

    except OathNetError as e:
        print_error(str(e))
        raise click.Abort()


@osint.command("ghunt")
@click.argument("email")
@click.pass_context
def ghunt(ctx: click.Context, email: str) -> None:
    """Get Google account info.

    Example:
        oathnet osint ghunt user@gmail.com
    """
    client = get_client(ctx)
    format = ctx.obj.get("format", "table")

    try:
        result = client.osint.ghunt(email)

        if format == "table":
            if result.success and result.data:
                console.print(f"\n[bold]Google Account Info[/bold]\n")
                console.print(f"  Status: {result.data.status}")
                if result.data.data:
                    console.print(f"  Data: {result.data.data}")
            else:
                console.print(f"[yellow]{result.message}[/yellow]")
                if result.errors:
                    console.print(f"[dim]{result.errors}[/dim]")
        else:
            output_result(result, format)

    except OathNetError as e:
        print_error(str(e))
        raise click.Abort()


@osint.command("subdomain")
@click.argument("domain")
@click.option("--alive", is_flag=True, help="Only return alive subdomains")
@click.pass_context
def subdomain(ctx: click.Context, domain: str, alive: bool) -> None:
    """Extract subdomains for a domain.

    Example:
        oathnet osint subdomain example.com
        oathnet osint subdomain example.com --alive
    """
    client = get_client(ctx)
    format = ctx.obj.get("format", "table")

    try:
        result = client.osint.extract_subdomain(domain, is_alive=alive)

        if format == "table":
            if result.data and result.data.subdomains:
                console.print(f"\n[bold]Found {result.data.count} subdomains for {domain}:[/bold]\n")
                for sub in result.data.subdomains[:50]:  # Limit display
                    console.print(f"  • {sub}")
                if result.data.count > 50:
                    console.print(f"\n[dim]... and {result.data.count - 50} more[/dim]")
            else:
                console.print("[yellow]No subdomains found[/yellow]")
        else:
            output_result(result, format)

    except OathNetError as e:
        print_error(str(e))
        raise click.Abort()


@osint.command("minecraft")
@click.argument("username")
@click.pass_context
def minecraft(ctx: click.Context, username: str) -> None:
    """Get Minecraft username history.

    Example:
        oathnet osint minecraft Notch
    """
    client = get_client(ctx)
    format = ctx.obj.get("format", "table")

    try:
        result = client.osint.minecraft_history(username)

        if format == "table":
            if result.data:
                console.print(f"\n[bold]Minecraft Account[/bold]\n")
                console.print(f"  UUID: {result.data.uuid}")
                console.print(f"  Username: {result.data.username}")
                if result.data.history:
                    console.print(f"\n  Username History:")
                    for entry in result.data.history:
                        console.print(f"    • {entry.username} ({entry.changed_at})")
        else:
            output_result(result, format)

    except OathNetError as e:
        print_error(str(e))
        raise click.Abort()
