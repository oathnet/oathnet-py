"""Stealer V2 commands for CLI."""

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
def stealer() -> None:
    """V2 Stealer search commands."""
    pass


@stealer.command("search")
@click.option("-q", "--query", help="Search query")
@click.option("--cursor", help="Pagination cursor")
@click.option("--page-size", default=25, help="Results per page")
@click.option("--domain", multiple=True, help="Filter by domain (can repeat)")
@click.option("--wildcard", is_flag=True, help="Enable wildcard matching")
@click.option("--has-log-id", is_flag=True, help="Only results with log ID")
@click.option("--file-search", "-fs", help="Auto file-search pattern in results")
@click.option("--file-search-mode", type=click.Choice(["literal", "regex", "wildcard"]), default="literal")
@click.option("-o", "--output", help="Save results to JSON file")
@click.pass_context
def search(
    ctx: click.Context,
    query: str | None,
    cursor: str | None,
    page_size: int,
    domain: tuple[str, ...],
    wildcard: bool,
    has_log_id: bool,
    file_search: str | None,
    file_search_mode: str,
    output: str | None,
) -> None:
    """Search V2 stealer database.

    Shows ALL fields dynamically and always dumps log_ids for use with file-search.

    Example:
        oathnet stealer search -q "gmail.com"
        oathnet stealer search -q "diddy" --has-log-id
        oathnet stealer search -q "diddy" --file-search "password" # Auto search files
        oathnet stealer search -q "diddy" -o results.json
    """
    client = get_client(ctx)
    format_out = ctx.obj.get("format", "table")

    try:
        result = client.stealer.search(
            q=query,
            cursor=cursor,
            page_size=page_size,
            domain=list(domain) if domain else None,
            wildcard=wildcard,
            has_log_id=has_log_id if has_log_id else None,
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
                console.print(f"\n[bold]Found {total} results[/bold] (showing {len(result.data.items)})\n")

                # Collect log_ids for file search
                log_ids = []

                for i, item in enumerate(result.data.items, 1):
                    console.print(f"[cyan]━━━ Result {i} ━━━[/cyan]")

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
                    priority = ["id", "log_id", "url", "username", "password", "email", "domain",
                               "subdomain", "path", "log", "pwned_at", "indexed_at"]

                    for field in priority:
                        if field in data:
                            val = data.pop(field)
                            if val is not None and val != "" and val != []:
                                if field == "log_id":
                                    console.print(f"  [bold yellow]log_id:[/bold yellow] [green]{val}[/green]")
                                elif field == "id":
                                    console.print(f"  [bold]id:[/bold] [green]{val}[/green]")
                                else:
                                    console.print(f"  [bold]{field}:[/bold] {format_value(val)}")

                    # Remaining fields
                    for key, val in sorted(data.items()):
                        if val is not None and val != "" and val != []:
                            console.print(f"  {key}: {format_value(val)}")

                    console.print()

                # Show all collected log_ids
                if log_ids:
                    console.print("\n[bold yellow]═══ LOG IDs (use with file-search/victims) ═══[/bold yellow]")
                    for lid in log_ids:
                        console.print(f"  [green]{lid}[/green]")
                    console.print()

                if result.data.next_cursor:
                    console.print(f"[yellow]Next cursor:[/yellow] {result.data.next_cursor}")

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
                console.print("[yellow]No results found[/yellow]")
        else:
            output_result(result, format_out)

    except OathNetError as e:
        print_error(str(e))
        raise click.Abort()


@stealer.command("subdomain")
@click.option("-d", "--domain", required=True, help="Domain to search")
@click.option("-q", "--query", help="Additional query filter")
@click.pass_context
def subdomain(ctx: click.Context, domain: str, query: str | None) -> None:
    """Extract subdomains from stealer data.

    Example:
        oathnet stealer subdomain -d google.com
    """
    client = get_client(ctx)
    format = ctx.obj.get("format", "table")

    try:
        result = client.stealer.subdomain(domain=domain, q=query)

        if format == "table":
            if result.data and result.data.subdomains:
                console.print(f"\n[bold]Found {result.data.count} subdomains for {domain}:[/bold]\n")
                for sub in result.data.subdomains[:50]:
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
