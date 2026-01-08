"""Search commands for CLI."""

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


def save_to_file(data, output_path: str, file_format: str = "json") -> None:
    """Save data to file."""
    if hasattr(data, "model_dump"):
        data = data.model_dump()

    with open(output_path, "w") as f:
        if file_format == "csv" and isinstance(data, dict) and "data" in data:
            # Convert to CSV for results
            results = data.get("data", {}).get("results", [])
            if results:
                import csv
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                for row in results:
                    writer.writerow(row)
            return
        json.dump(data, f, indent=2, default=str)


@click.group()
def search() -> None:
    """Search breach and stealer databases."""
    pass


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


@search.command("breach")
@click.option("-q", "--query", required=True, help="Search query")
@click.option("--cursor", help="Pagination cursor")
@click.option("--dbnames", help="Filter by database names (comma-separated)")
@click.option("-o", "--output", help="Save results to file")
@click.option("--csv", "file_format", flag_value="csv", help="Save as CSV")
@click.pass_context
def breach(
    ctx: click.Context,
    query: str,
    cursor: str | None,
    dbnames: str | None,
    output: str | None,
    file_format: str | None,
) -> None:
    """Search breach database.

    Dynamically displays ALL fields in results since breach data varies by source.

    Example:
        oathnet search breach -q "winterfox"
        oathnet search breach -q "user@example.com" --dbnames linkedin
        oathnet search breach -q "winterfox" -o results.json
        oathnet search breach -q "winterfox" -o results.csv --csv
    """
    client = get_client(ctx)
    format = ctx.obj.get("format", "table")

    try:
        result = client.search.breach(q=query, cursor=cursor, dbnames=dbnames)

        # Save to file if requested
        if output:
            save_to_file(result, output, file_format or "json")
            print_success(f"Saved results to {output}")

        if format == "table":
            if result.data and result.data.results:
                console.print(f"\n[bold]Found {result.data.results_found} results[/bold] (showing {result.data.results_shown})\n")

                for i, r in enumerate(result.data.results, 1):
                    console.print(f"[cyan]━━━ Result {i} ━━━[/cyan]")

                    # Convert to dict for dynamic access
                    if hasattr(r, "model_dump"):
                        data = r.model_dump(exclude_none=True, exclude_unset=True)
                    else:
                        data = dict(r) if hasattr(r, "__iter__") else vars(r)

                    # Remove internal fields
                    data = {k: v for k, v in data.items() if not k.startswith("_") and v is not None}

                    # Prioritize important fields first
                    priority_fields = ["id", "dbname", "email", "username", "password", "password_hash",
                                      "phone_number", "ip", "domain", "country", "city", "full_name",
                                      "first_name", "last_name", "date"]

                    # Print priority fields first
                    for field in priority_fields:
                        if field in data:
                            val = data.pop(field)
                            if val is not None and val != "" and val != []:
                                console.print(f"  [bold]{field}:[/bold] {format_value(val)}")

                    # Print remaining fields
                    for key, val in sorted(data.items()):
                        if val is not None and val != "" and val != []:
                            console.print(f"  {key}: {format_value(val)}")

                    console.print()

                if result.data.cursor:
                    console.print(f"\n[yellow]Next cursor:[/yellow] {result.data.cursor}")
                    console.print("[dim]Use --cursor to fetch next page[/dim]")
            else:
                console.print("[yellow]No results found[/yellow]")
        else:
            output_result(result, format)

    except OathNetError as e:
        print_error(str(e))
        raise click.Abort()


@search.command("stealer")
@click.option("-q", "--query", required=True, help="Search query")
@click.option("--cursor", help="Pagination cursor")
@click.option("--dbnames", help="Filter by database names")
@click.option("-o", "--output", help="Save results to file")
@click.pass_context
def stealer_cmd(
    ctx: click.Context,
    query: str,
    cursor: str | None,
    dbnames: str | None,
    output: str | None,
) -> None:
    """Search stealer database (legacy).

    Example:
        oathnet search stealer -q "diddy"
        oathnet search stealer -q "diddy" -o stealer_results.json
    """
    client = get_client(ctx)
    format = ctx.obj.get("format", "table")

    try:
        result = client.search.stealer(q=query, cursor=cursor, dbnames=dbnames)

        # Save to file if requested
        if output:
            save_to_file(result, output)
            print_success(f"Saved results to {output}")

        if format == "table":
            if result.data and result.data.results:
                console.print(f"\n[bold]Found {result.data.results_found} results[/bold] (showing {result.data.results_shown})\n")
                for i, r in enumerate(result.data.results, 1):
                    console.print(f"[cyan]Result {i}:[/cyan]")
                    console.print(f"  LOG: {r.LOG or 'N/A'}")
                    if r.domain:
                        console.print(f"  Domain: {', '.join(r.domain)}")
                    if r.email:
                        console.print(f"  Email: {', '.join(r.email)}")
                    console.print()

                if result.data.cursor:
                    console.print(f"[dim]Next cursor: {result.data.cursor}[/dim]")
            else:
                console.print("[yellow]No results found[/yellow]")
        else:
            output_result(result, format)

    except OathNetError as e:
        print_error(str(e))
        raise click.Abort()


@search.command("init")
@click.option("-q", "--query", required=True, help="Search query")
@click.pass_context
def init_session(ctx: click.Context, query: str) -> None:
    """Initialize a search session.

    Example:
        oathnet search init -q "user@example.com"
    """
    client = get_client(ctx)
    format = ctx.obj.get("format", "table")

    try:
        result = client.search.init_session(query)

        if format == "table":
            if result.data:
                console.print(f"\n[bold green]Session initialized[/bold green]")
                console.print(f"Session ID: [cyan]{result.data.session.id}[/cyan]")
                console.print(f"Query: {result.data.session.query}")
                console.print(f"Search Type: {result.data.session.search_type}")
                console.print(f"Expires: {result.data.session.expires_at}")
                if result.data.user:
                    console.print(f"Plan: {result.data.user.plan}")
                    if result.data.user.daily_lookups:
                        console.print(f"Lookups remaining: {result.data.user.daily_lookups.remaining}")
        else:
            output_result(result, format)

    except OathNetError as e:
        print_error(str(e))
        raise click.Abort()
