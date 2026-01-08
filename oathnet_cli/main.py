"""OathNet CLI - Main entry point."""

import click

from oathnet import OathNetClient

from .commands import bulk, exports, file_search, osint, search, stealer, utility, victims
from .utils import error_console


@click.group()
@click.option(
    "--api-key",
    "-k",
    envvar="OATHNET_API_KEY",
    help="OathNet API key (or set OATHNET_API_KEY env var)",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["table", "json", "raw"]),
    default="table",
    help="Output format",
)
@click.version_option(version="1.0.0", prog_name="oathnet")
@click.pass_context
def cli(ctx: click.Context, api_key: str | None, format: str) -> None:
    """OathNet CLI - Command-line interface for OathNet API.

    Search breach databases, stealer logs, and perform OSINT lookups.

    Example:

        oathnet search breach -q "user@example.com"

        oathnet osint discord user 300760994454437890

        oathnet osint ip 174.235.65.156
    """
    ctx.ensure_object(dict)
    ctx.obj["api_key"] = api_key
    ctx.obj["format"] = format


def get_client(ctx: click.Context) -> OathNetClient:
    """Get OathNet client from context."""
    api_key = ctx.obj.get("api_key")
    if not api_key:
        error_console.print("[red]Error:[/red] API key is required")
        error_console.print("Use --api-key or set OATHNET_API_KEY environment variable")
        raise click.Abort()
    return OathNetClient(api_key)


# Register command groups
cli.add_command(search.search)
cli.add_command(stealer.stealer)
cli.add_command(victims.victims)
cli.add_command(file_search.file_search)
cli.add_command(exports.export)
cli.add_command(osint.osint)
cli.add_command(bulk.bulk)
cli.add_command(utility.util)


def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
