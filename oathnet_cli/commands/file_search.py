"""File Search V2 commands for CLI."""

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


@click.group("file-search")
def file_search() -> None:
    """V2 File search commands (search within victim files)."""
    pass


@file_search.command("create")
@click.option("-e", "--expression", required=True, help="Search expression")
@click.option(
    "--mode",
    type=click.Choice(["literal", "regex", "wildcard"]),
    default="literal",
    help="Search mode",
)
@click.option("--log-id", multiple=True, help="Limit to specific log IDs")
@click.option("--case-sensitive", is_flag=True, help="Case-sensitive search")
@click.option("--context-lines", default=2, help="Lines of context (0-5)")
@click.option("--file-pattern", help="Glob pattern for file filtering")
@click.option("--max-matches", default=100, help="Maximum matches to return")
@click.pass_context
def create(
    ctx: click.Context,
    expression: str,
    mode: str,
    log_id: tuple[str, ...],
    case_sensitive: bool,
    context_lines: int,
    file_pattern: str | None,
    max_matches: int,
) -> None:
    """Create a file search job.

    Example:
        oathnet file-search create -e "password"
        oathnet file-search create -e "api[_-]?key" --mode regex
        oathnet file-search create -e "*.txt" --mode wildcard --file-pattern "*.txt"
    """
    client = get_client(ctx)
    format = ctx.obj.get("format", "table")

    try:
        result = client.file_search.create(
            expression=expression,
            search_mode=mode,
            log_ids=list(log_id) if log_id else None,
            case_sensitive=case_sensitive,
            context_lines=context_lines,
            file_pattern=file_pattern,
            max_matches=max_matches,
        )

        if format == "table":
            if result.data:
                console.print(f"\n[bold green]File search job created[/bold green]\n")
                console.print(f"  Job ID: [cyan]{result.data.job_id}[/cyan]")
                console.print(f"  Status: {result.data.status}")
                console.print(f"  Created: {result.data.created_at}")
                if result.data.expires_at:
                    console.print(f"  Expires: {result.data.expires_at}")
                console.print(f"\nUse [cyan]oathnet file-search status {result.data.job_id}[/cyan] to check progress")
                console.print(f"Or [cyan]oathnet file-search wait {result.data.job_id}[/cyan] to wait for completion")
        else:
            output_result(result, format)

    except OathNetError as e:
        print_error(str(e))
        raise click.Abort()


@file_search.command("status")
@click.argument("job_id")
@click.pass_context
def status(ctx: click.Context, job_id: str) -> None:
    """Get file search job status.

    Example:
        oathnet file-search status abc123
    """
    client = get_client(ctx)
    format = ctx.obj.get("format", "table")

    try:
        result = client.file_search.get_status(job_id)

        if format == "table":
            if result.data:
                console.print(f"\n[bold]File Search Job Status[/bold]\n")
                console.print(f"  Job ID: {result.data.job_id}")
                console.print(f"  Status: {result.data.status}")

                if result.data.summary:
                    s = result.data.summary
                    console.print(f"\n[bold]Summary:[/bold]")
                    console.print(f"  Files scanned: {s.files_scanned}/{s.files_total}")
                    console.print(f"  Files matched: {s.files_matched}")
                    console.print(f"  Total matches: {s.matches}")
                    console.print(f"  Bytes scanned: {s.bytes_scanned}")
                    if s.duration_ms:
                        console.print(f"  Duration: {s.duration_ms}ms")

                if result.data.matches and result.data.status == "completed":
                    console.print(f"\n[bold]Matches ({len(result.data.matches)}):[/bold]\n")
                    for i, match in enumerate(result.data.matches[:20], 1):
                        console.print(f"  [cyan]{i}.[/cyan] {match.file_name}")
                        console.print(f"     Log: {match.log_id}")
                        console.print(f"     Path: {match.relative_path}")
                        if match.match_text:
                            # Truncate long matches
                            text = match.match_text[:100] + "..." if len(match.match_text) > 100 else match.match_text
                            console.print(f"     Match: {text}")
                        console.print()

                    if len(result.data.matches) > 20:
                        console.print(f"  [dim]... and {len(result.data.matches) - 20} more matches[/dim]")
        else:
            output_result(result, format)

    except OathNetError as e:
        print_error(str(e))
        raise click.Abort()


@file_search.command("wait")
@click.argument("job_id")
@click.option("--timeout", default=300, help="Timeout in seconds")
@click.pass_context
def wait(ctx: click.Context, job_id: str, timeout: int) -> None:
    """Wait for file search job to complete.

    Example:
        oathnet file-search wait abc123
        oathnet file-search wait abc123 --timeout 600
    """
    client = get_client(ctx)
    format = ctx.obj.get("format", "table")

    try:
        console.print(f"Waiting for job {job_id}...")
        result = client.file_search.wait_for_completion(job_id, timeout=timeout)

        if format == "table":
            if result.data:
                console.print(f"\n[green]Job completed with status: {result.data.status}[/green]")

                if result.data.summary:
                    s = result.data.summary
                    console.print(f"\n[bold]Summary:[/bold]")
                    console.print(f"  Files matched: {s.files_matched}")
                    console.print(f"  Total matches: {s.matches}")

                if result.data.matches:
                    console.print(f"\n[bold]Matches ({len(result.data.matches)}):[/bold]\n")
                    for i, match in enumerate(result.data.matches[:20], 1):
                        console.print(f"  [cyan]{i}.[/cyan] {match.file_name} (log: {match.log_id})")
                        if match.match_text:
                            text = match.match_text[:80] + "..." if len(match.match_text) > 80 else match.match_text
                            console.print(f"     {text}")
                    if len(result.data.matches) > 20:
                        console.print(f"\n  [dim]... and {len(result.data.matches) - 20} more[/dim]")
        else:
            output_result(result, format)

    except TimeoutError:
        print_error(f"Job did not complete within {timeout} seconds")
        raise click.Abort()
    except OathNetError as e:
        print_error(str(e))
        raise click.Abort()


@file_search.command("search")
@click.option("-e", "--expression", required=True, help="Search expression")
@click.option(
    "--mode",
    type=click.Choice(["literal", "regex", "wildcard"]),
    default="literal",
    help="Search mode",
)
@click.option("--timeout", default=300, help="Timeout in seconds")
@click.option("-o", "--output", help="Save results to file")
@click.pass_context
def search(
    ctx: click.Context,
    expression: str,
    mode: str,
    timeout: int,
    output: str | None,
) -> None:
    """Create file search and wait for results (convenience command).

    Example:
        oathnet file-search search -e "password"
        oathnet file-search search -e "api_key" --mode regex -o results.json
    """
    client = get_client(ctx)
    format = ctx.obj.get("format", "table")

    try:
        console.print(f"Creating file search for: {expression}")
        result = client.file_search.search(expression=expression, search_mode=mode, timeout=timeout)

        if output and result.data:
            import json
            with open(output, "w") as f:
                json.dump(result.model_dump(), f, indent=2, default=str)
            print_success(f"Saved results to {output}")

        if format == "table":
            if result.data:
                console.print(f"\n[green]Search completed[/green]")

                if result.data.summary:
                    console.print(f"  Matches: {result.data.summary.matches}")

                if result.data.matches:
                    console.print(f"\n[bold]Results:[/bold]\n")
                    for i, match in enumerate(result.data.matches[:20], 1):
                        console.print(f"  [cyan]{i}.[/cyan] {match.file_name}")
                        console.print(f"     Log ID: {match.log_id}")
                        if match.match_text:
                            text = match.match_text[:80] + "..." if len(match.match_text) > 80 else match.match_text
                            console.print(f"     Match: {text}")
                        console.print()
        else:
            output_result(result, format)

    except TimeoutError:
        print_error(f"Search did not complete within {timeout} seconds")
        raise click.Abort()
    except OathNetError as e:
        print_error(str(e))
        raise click.Abort()
