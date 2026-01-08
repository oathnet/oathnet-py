"""CLI Utility functions for output formatting."""

import json
import os
import sys
from typing import Any

import click
from rich.console import Console
from rich.json import JSON
from rich.table import Table

console = Console()
error_console = Console(stderr=True)


def get_api_key(ctx: click.Context) -> str:
    """Get API key from context, environment, or prompt."""
    # Check context
    api_key = ctx.obj.get("api_key") if ctx.obj else None

    # Check environment
    if not api_key:
        api_key = os.environ.get("OATHNET_API_KEY")

    if not api_key:
        error_console.print("[red]Error:[/red] API key is required.")
        error_console.print("Set OATHNET_API_KEY environment variable or use --api-key flag")
        sys.exit(1)

    return api_key


def output_json(data: Any) -> None:
    """Output data as formatted JSON."""
    if hasattr(data, "model_dump"):
        data = data.model_dump()
    console.print(JSON(json.dumps(data, default=str, indent=2)))


def output_raw_json(data: Any) -> None:
    """Output data as raw JSON (for piping)."""
    if hasattr(data, "model_dump"):
        data = data.model_dump()
    click.echo(json.dumps(data, default=str))


def output_table(headers: list[str], rows: list[list[Any]], title: str | None = None) -> None:
    """Output data as a rich table."""
    table = Table(title=title, show_header=True, header_style="bold cyan")

    for header in headers:
        table.add_column(header)

    for row in rows:
        table.add_row(*[str(cell) if cell is not None else "" for cell in row])

    console.print(table)


def output_result(
    data: Any,
    format: str = "table",
    table_headers: list[str] | None = None,
    table_rows: list[list[Any]] | None = None,
    title: str | None = None,
) -> None:
    """Output result in specified format."""
    if format == "json":
        output_json(data)
    elif format == "raw":
        output_raw_json(data)
    elif format == "table" and table_headers and table_rows:
        output_table(table_headers, table_rows, title)
    else:
        # Default to JSON if no table data
        output_json(data)


def print_success(message: str) -> None:
    """Print success message."""
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str) -> None:
    """Print error message."""
    error_console.print(f"[red]✗[/red] {message}")


def print_warning(message: str) -> None:
    """Print warning message."""
    console.print(f"[yellow]![/yellow] {message}")


def print_info(message: str) -> None:
    """Print info message."""
    console.print(f"[blue]ℹ[/blue] {message}")


def format_meta(meta: Any) -> str:
    """Format metadata for display."""
    if not meta:
        return ""

    parts = []
    if hasattr(meta, "lookups") and meta.lookups:
        lookups = meta.lookups
        if lookups.left_today is not None:
            parts.append(f"Lookups left: {lookups.left_today}")
    if hasattr(meta, "performance") and meta.performance:
        perf = meta.performance
        if perf.duration_ms is not None:
            parts.append(f"Duration: {perf.duration_ms:.0f}ms")

    return " | ".join(parts)
