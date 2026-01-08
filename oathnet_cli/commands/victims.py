"""Victims V2 commands for CLI."""

import json

import click

from oathnet import OathNetClient
from oathnet.exceptions import OathNetError

from ..utils import console, error_console, output_result, print_error, print_success


def get_client(ctx: click.Context) -> OathNetClient:
    """Get client from context."""
    api_key = ctx.obj.get("api_key")
    if not api_key:
        error_console.print("[red]Error:[/red] API key is required")
        raise click.Abort()
    return OathNetClient(api_key)


def format_value(value) -> str:
    """Format any value for display."""
    if value is None:
        return "[dim]N/A[/dim]"
    if isinstance(value, list):
        if not value:
            return "[dim]N/A[/dim]"
        return ", ".join(str(v) for v in value[:5]) + (f" (+{len(value)-5} more)" if len(value) > 5 else "")
    if isinstance(value, dict):
        return json.dumps(value, default=str)
    return str(value)


@click.group()
def victims() -> None:
    """V2 Victims commands (profiles, files, archives)."""
    pass


@victims.command("search")
@click.option("-q", "--query", help="Search query")
@click.option("--cursor", help="Pagination cursor")
@click.option("--page-size", default=25, help="Results per page")
@click.option("--email", multiple=True, help="Filter by email (can repeat)")
@click.option("--ip", multiple=True, help="Filter by IP (can repeat)")
@click.option("--discord-id", multiple=True, help="Filter by Discord ID")
@click.option("--wildcard", is_flag=True, help="Enable wildcard matching")
@click.option("--file-search", "-fs", help="Auto file-search pattern in results")
@click.option("--file-search-mode", type=click.Choice(["literal", "regex", "wildcard"]), default="literal")
@click.option("-o", "--output", help="Save results to JSON file")
@click.pass_context
def search(
    ctx: click.Context,
    query: str | None,
    cursor: str | None,
    page_size: int,
    email: tuple[str, ...],
    ip: tuple[str, ...],
    discord_id: tuple[str, ...],
    wildcard: bool,
    file_search: str | None,
    file_search_mode: str,
    output: str | None,
) -> None:
    """Search victim profiles.

    Shows ALL fields dynamically and always dumps log_ids for use with file-search.

    Example:
        oathnet victims search -q "gmail"
        oathnet victims search --email user@gmail.com
        oathnet victims search -q "diddy" --file-search "api_key"  # Auto search files
        oathnet victims search -q "diddy" -o results.json
    """
    client = get_client(ctx)
    format_out = ctx.obj.get("format", "table")

    try:
        result = client.victims.search(
            q=query,
            cursor=cursor,
            page_size=page_size,
            email=list(email) if email else None,
            ip=list(ip) if ip else None,
            discord_id=list(discord_id) if discord_id else None,
            wildcard=wildcard,
        )

        # Save to file if requested
        if output:
            with open(output, "w") as f:
                if hasattr(result, "model_dump"):
                    json.dump(result.model_dump(), f, indent=2, default=str)
                else:
                    json.dump(result, f, indent=2, default=str)
            print_success(f"Saved results to {output}")

        if format_out == "table":
            if result.data and result.data.items:
                meta = result.data.meta
                total = meta.total if meta else "?"
                console.print(f"\n[bold]Found {total} victims[/bold] (showing {len(result.data.items)})\n")

                # Collect log_ids for file search
                log_ids = []

                for i, item in enumerate(result.data.items, 1):
                    console.print(f"[cyan]━━━ Victim {i} ━━━[/cyan]")

                    # Convert to dict for dynamic display
                    if hasattr(item, "model_dump"):
                        data = item.model_dump(exclude_none=True, exclude_unset=True)
                    else:
                        data = dict(item) if hasattr(item, "__iter__") else vars(item)

                    # Remove internal fields
                    data = {k: v for k, v in data.items() if not k.startswith("_") and v is not None}

                    # Collect log_id
                    if "log_id" in data and data["log_id"]:
                        log_ids.append(data["log_id"])

                    # Priority fields
                    priority = ["log_id", "device_users", "device_emails", "device_ips",
                               "discord_ids", "hwids", "total_docs", "pwned_at", "indexed_at"]

                    for field in priority:
                        if field in data:
                            val = data.pop(field)
                            if val is not None and val != "" and val != []:
                                if field == "log_id":
                                    console.print(f"  [bold yellow]log_id:[/bold yellow] [green]{val}[/green]")
                                else:
                                    console.print(f"  [bold]{field}:[/bold] {format_value(val)}")

                    # Remaining fields
                    for key, val in sorted(data.items()):
                        if val is not None and val != "" and val != []:
                            console.print(f"  {key}: {format_value(val)}")

                    console.print()

                # Show all collected log_ids
                if log_ids:
                    console.print("\n[bold yellow]═══ LOG IDs (use with file-search/manifest/archive) ═══[/bold yellow]")
                    for lid in log_ids:
                        console.print(f"  [green]{lid}[/green]")
                    console.print()
                    console.print("[dim]Usage: oathnet victims manifest <log_id>[/dim]")
                    console.print("[dim]       oathnet file-search create -e 'password' --log-id <log_id>[/dim]")

                if result.data.next_cursor:
                    console.print(f"\n[yellow]Next cursor:[/yellow] {result.data.next_cursor}")

                # Auto file-search if requested
                if file_search and log_ids:
                    console.print(f"\n[bold magenta]═══ Auto File Search: '{file_search}' ═══[/bold magenta]")
                    try:
                        fs_result = client.file_search.search(
                            expression=file_search,
                            search_mode=file_search_mode,
                            log_ids=log_ids[:10],  # Limit to first 10 logs
                            max_matches=50,
                        )
                        if fs_result.data and fs_result.data.matches:
                            console.print(f"[green]Found {len(fs_result.data.matches)} matches![/green]\n")
                            for match in fs_result.data.matches[:20]:
                                console.print(f"  [cyan]{match.file_name}[/cyan] (log: {match.log_id})")
                                if match.match_text:
                                    console.print(f"    → {match.match_text[:100]}")
                        else:
                            console.print("[yellow]No file matches found[/yellow]")
                    except Exception as e:
                        console.print(f"[red]File search error: {e}[/red]")
            else:
                console.print("[yellow]No victims found[/yellow]")
        else:
            output_result(result, format_out)

    except OathNetError as e:
        print_error(str(e))
        raise click.Abort()


@victims.command("manifest")
@click.argument("log_id")
@click.pass_context
def manifest(ctx: click.Context, log_id: str) -> None:
    """Get victim file manifest (tree).

    Example:
        oathnet victims manifest vic_001_user
    """
    client = get_client(ctx)
    format = ctx.obj.get("format", "table")

    try:
        result = client.victims.get_manifest(log_id)

        if format == "table":
            if result.data:
                console.print(f"\n[bold]Manifest for {log_id}[/bold]\n")
                console.print(f"  Log Name: {result.data.log_name}")

                def print_tree(node, indent=0):
                    prefix = "  " * indent
                    icon = "📁" if node.type == "directory" else "📄"
                    size = f" ({node.size_bytes} bytes)" if node.size_bytes else ""
                    console.print(f"{prefix}{icon} {node.name}{size}")
                    if node.id and node.type == "file":
                        console.print(f"{prefix}   [dim]ID: {node.id}[/dim]")
                    if node.children:
                        for child in node.children:
                            print_tree(child, indent + 1)

                if result.data.victim_tree:
                    print_tree(result.data.victim_tree)
        else:
            output_result(result, format)

    except OathNetError as e:
        print_error(str(e))
        raise click.Abort()


@victims.command("file")
@click.argument("log_id")
@click.argument("file_id")
@click.option("-o", "--output", help="Save to file")
@click.pass_context
def file(ctx: click.Context, log_id: str, file_id: str, output: str | None) -> None:
    """Get victim file content.

    Example:
        oathnet victims file vic_001 file_abc
        oathnet victims file vic_001 file_abc -o passwords.txt
    """
    client = get_client(ctx)

    try:
        result = client.victims.get_file(log_id, file_id)

        if output and result.data and result.data.content:
            with open(output, "w") as f:
                f.write(result.data.content)
            print_success(f"Saved to {output}")
        elif result.data and result.data.content:
            console.print(result.data.content)
        else:
            console.print("[yellow]No content[/yellow]")

    except OathNetError as e:
        print_error(str(e))
        raise click.Abort()


@victims.command("archive")
@click.argument("log_id")
@click.option("-o", "--output", help="Output path (default: {log_id}.zip)")
@click.pass_context
def archive(ctx: click.Context, log_id: str, output: str | None) -> None:
    """Download victim archive as ZIP.

    Example:
        oathnet victims archive vic_001
        oathnet victims archive vic_001 -o victim.zip
    """
    client = get_client(ctx)

    try:
        output_path = output or f"{log_id}.zip"
        client.victims.download_archive(log_id, output_path)
        print_success(f"Downloaded archive to {output_path}")

    except OathNetError as e:
        print_error(str(e))
        raise click.Abort()
