"""Export V2 commands for CLI."""

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


@click.group("export")
def export() -> None:
    """V2 Export commands (export search results to files)."""
    pass


@export.command("create")
@click.option(
    "--type",
    "export_type",
    type=click.Choice(["docs", "victims"]),
    required=True,
    help="Export type (docs=credentials, victims=profiles)",
)
@click.option(
    "--format",
    "file_format",
    type=click.Choice(["jsonl", "csv"]),
    default="jsonl",
    help="Output format",
)
@click.option("--query", "-q", help="Search query for export")
@click.option("--limit", type=int, help="Maximum records to export")
@click.pass_context
def create(
    ctx: click.Context,
    export_type: str,
    file_format: str,
    query: str | None,
    limit: int | None,
) -> None:
    """Create an export job.

    Example:
        oathnet export create --type docs --format csv
        oathnet export create --type docs -q "gmail.com" --limit 1000
        oathnet export create --type victims --format jsonl
    """
    client = get_client(ctx)
    format = ctx.obj.get("format", "table")

    try:
        # Build search params
        search = {"query": query} if query else None

        result = client.exports.create(
            export_type=export_type,
            format=file_format,
            limit=limit,
            search=search,
        )

        if format == "table":
            if result.data:
                console.print(f"\n[bold green]Export job created[/bold green]\n")
                console.print(f"  Job ID: [cyan]{result.data.job_id}[/cyan]")
                console.print(f"  Status: {result.data.status}")
                console.print(f"  Created: {result.data.created_at}")
                if result.data.expires_at:
                    console.print(f"  Expires: {result.data.expires_at}")
                console.print(f"\nUse [cyan]oathnet export status {result.data.job_id}[/cyan] to check progress")
                console.print(f"Or [cyan]oathnet export download {result.data.job_id} -o output.{file_format}[/cyan] to download when ready")
        else:
            output_result(result, format)

    except OathNetError as e:
        print_error(str(e))
        raise click.Abort()


@export.command("status")
@click.argument("job_id")
@click.pass_context
def status(ctx: click.Context, job_id: str) -> None:
    """Get export job status.

    Example:
        oathnet export status abc123
    """
    client = get_client(ctx)
    format = ctx.obj.get("format", "table")

    try:
        result = client.exports.get_status(job_id)

        if format == "table":
            if result.data:
                console.print(f"\n[bold]Export Job Status[/bold]\n")
                console.print(f"  Job ID: {result.data.job_id}")
                console.print(f"  Status: {result.data.status}")

                if result.data.progress:
                    p = result.data.progress
                    console.print(f"\n[bold]Progress:[/bold]")
                    if p.percent is not None:
                        console.print(f"  Progress: {p.percent:.1f}%")
                    if p.records_done is not None:
                        console.print(f"  Records: {p.records_done}/{p.records_total or '?'}")
                    if p.bytes_done is not None:
                        console.print(f"  Bytes: {p.bytes_done:,}")

                if result.data.result and result.data.status == "completed":
                    r = result.data.result
                    console.print(f"\n[bold]Result:[/bold]")
                    console.print(f"  File: {r.file_name}")
                    console.print(f"  Size: {r.file_size:,} bytes" if r.file_size else "  Size: N/A")
                    console.print(f"  Records: {r.records:,}" if r.records else "  Records: N/A")
                    console.print(f"  Format: {r.format}")
                    console.print(f"  Expires: {r.expires_at}")
                    console.print(f"\nDownload with: [cyan]oathnet export download {job_id} -o {r.file_name}[/cyan]")
        else:
            output_result(result, format)

    except OathNetError as e:
        print_error(str(e))
        raise click.Abort()


@export.command("download")
@click.argument("job_id")
@click.option("-o", "--output", required=True, help="Output file path")
@click.pass_context
def download(ctx: click.Context, job_id: str, output: str) -> None:
    """Download completed export.

    Example:
        oathnet export download abc123 -o export.csv
        oathnet export download abc123 -o data.jsonl
    """
    client = get_client(ctx)

    try:
        console.print(f"Downloading export {job_id}...")
        client.exports.download(job_id, output)
        print_success(f"Downloaded to {output}")

    except OathNetError as e:
        print_error(str(e))
        raise click.Abort()


@export.command("wait")
@click.argument("job_id")
@click.option("-o", "--output", help="Download to file after completion")
@click.option("--timeout", default=600, help="Timeout in seconds")
@click.pass_context
def wait(ctx: click.Context, job_id: str, output: str | None, timeout: int) -> None:
    """Wait for export job to complete.

    Example:
        oathnet export wait abc123
        oathnet export wait abc123 -o export.csv
    """
    client = get_client(ctx)

    try:
        console.print(f"Waiting for export {job_id}...")
        result = client.exports.wait_for_completion(job_id, timeout=timeout)

        if result.data:
            console.print(f"\n[green]Export completed with status: {result.data.status}[/green]")

            if result.data.result:
                r = result.data.result
                console.print(f"  File: {r.file_name}")
                console.print(f"  Records: {r.records:,}" if r.records else "")

            if output:
                client.exports.download(job_id, output)
                print_success(f"Downloaded to {output}")

    except TimeoutError:
        print_error(f"Export did not complete within {timeout} seconds")
        raise click.Abort()
    except OathNetError as e:
        print_error(str(e))
        raise click.Abort()


@export.command("run")
@click.option(
    "--type",
    "export_type",
    type=click.Choice(["docs", "victims"]),
    required=True,
    help="Export type",
)
@click.option(
    "--format",
    "file_format",
    type=click.Choice(["jsonl", "csv"]),
    default="jsonl",
    help="Output format",
)
@click.option("-o", "--output", required=True, help="Output file path")
@click.option("--query", "-q", help="Search query for export")
@click.option("--limit", type=int, help="Maximum records")
@click.option("--timeout", default=600, help="Timeout in seconds")
@click.pass_context
def run(
    ctx: click.Context,
    export_type: str,
    file_format: str,
    output: str,
    query: str | None,
    limit: int | None,
    timeout: int,
) -> None:
    """Create export, wait, and download (convenience command).

    Example:
        oathnet export run --type docs --format csv -o results.csv
        oathnet export run --type docs -q "gmail.com" -o gmail_results.csv
    """
    client = get_client(ctx)

    try:
        console.print(f"Creating {export_type} export...")
        search = {"query": query} if query else None

        path = client.exports.export(
            export_type=export_type,
            output_path=output,
            format=file_format,
            limit=limit,
            search=search,
            timeout=timeout,
        )
        print_success(f"Export saved to {path}")

    except TimeoutError:
        print_error(f"Export did not complete within {timeout} seconds")
        raise click.Abort()
    except OathNetError as e:
        print_error(str(e))
        raise click.Abort()
