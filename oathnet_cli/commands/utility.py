"""Utility commands for CLI."""

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
def util() -> None:
    """Utility commands."""
    pass


@util.command("dbnames")
@click.option("-q", "--query", required=True, help="Partial database name")
@click.pass_context
def dbnames(ctx: click.Context, query: str) -> None:
    """Autocomplete database names.

    Example:
        oathnet util dbnames -q "linked"
        oathnet util dbnames -q "face"
    """
    client = get_client(ctx)
    format = ctx.obj.get("format", "table")

    try:
        result = client.utility.dbname_autocomplete(query)

        if format == "table":
            if result:
                console.print(f"\n[bold]Database names matching '{query}':[/bold]\n")
                for name in result:
                    console.print(f"  • {name}")
            else:
                console.print("[yellow]No matches found[/yellow]")
        else:
            output_result(result, format)

    except OathNetError as e:
        print_error(str(e))
        raise click.Abort()
