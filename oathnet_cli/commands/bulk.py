"""Bulk search commands for CLI."""

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


@click.group()
def bulk() -> None:
    """Bulk search commands."""
    pass


@bulk.command("create")
@click.option("-t", "--term", multiple=True, required=True, help="Search term (can repeat)")
@click.option("--service", type=click.Choice(["breach", "stealer"]), required=True, help="Search service")
@click.option("--format", type=click.Choice(["json", "csv"]), default="json", help="Output format")
@click.pass_context
def create(ctx: click.Context, term: tuple[str, ...], service: str, format: str) -> None:
    """Create a bulk search job.

    Example:
        oathnet bulk create -t user1@example.com -t user2@example.com --service breach
    """
    client = get_client(ctx)
    output_format = ctx.obj.get("format", "table")

    try:
        result = client.bulk.create(terms=list(term), service=service, format=format)

        if output_format == "table":
            if result.data:
                console.print(f"\n[bold green]Bulk search job created[/bold green]\n")
                console.print(f"  Job ID: [cyan]{result.data.id}[/cyan]")
                console.print(f"  Status: {result.data.status}")
                console.print(f"  Service: {result.data.search_service}")
                console.print(f"  Terms: {len(term)}")
                console.print(f"\nUse [cyan]oathnet bulk status {result.data.id}[/cyan] to check progress")
        else:
            output_result(result, output_format)

    except OathNetError as e:
        print_error(str(e))
        raise click.Abort()


@bulk.command("status")
@click.argument("job_id")
@click.pass_context
def status(ctx: click.Context, job_id: str) -> None:
    """Get bulk search job status.

    Example:
        oathnet bulk status abc123
    """
    client = get_client(ctx)
    format = ctx.obj.get("format", "table")

    try:
        result = client.bulk.get_status(job_id)

        if format == "table":
            if result.data:
                console.print(f"\n[bold]Bulk Search Job Status[/bold]\n")
                console.print(f"  Job ID: {result.data.id}")
                console.print(f"  Status: {result.data.status}")
                console.print(f"  Service: {result.data.search_service}")
                console.print(f"  Format: {result.data.output_format}")
                if result.data.results_count is not None:
                    console.print(f"  Results: {result.data.results_count}")
                if result.data.lookups_deducted is not None:
                    console.print(f"  Lookups used: {result.data.lookups_deducted}")
                console.print(f"  Created: {result.data.created_at}")
                console.print(f"  Updated: {result.data.updated_at}")
        else:
            output_result(result, format)

    except OathNetError as e:
        print_error(str(e))
        raise click.Abort()


@bulk.command("list")
@click.option("--page", default=1, help="Page number")
@click.option("--page-size", default=10, help="Results per page")
@click.pass_context
def list_jobs(ctx: click.Context, page: int, page_size: int) -> None:
    """List bulk search jobs.

    Example:
        oathnet bulk list
        oathnet bulk list --page 2
    """
    client = get_client(ctx)
    format = ctx.obj.get("format", "table")

    try:
        result = client.bulk.list_jobs(page=page, page_size=page_size)

        if format == "table":
            if result.results:
                console.print(f"\n[bold]Bulk Search Jobs[/bold] (Total: {result.count})\n")
                for job in result.results:
                    status_color = "green" if job.status == "COMPLETED" else "yellow"
                    console.print(f"  [{status_color}]{job.status}[/{status_color}] {job.id}")
                    console.print(f"     Service: {job.search_service} | Created: {job.created_at}")
            else:
                console.print("[yellow]No jobs found[/yellow]")
        else:
            output_result(result, format)

    except OathNetError as e:
        print_error(str(e))
        raise click.Abort()


@bulk.command("download")
@click.argument("job_id")
@click.option("-o", "--output", help="Output file path")
@click.pass_context
def download(ctx: click.Context, job_id: str, output: str | None) -> None:
    """Download bulk search results.

    Example:
        oathnet bulk download abc123
        oathnet bulk download abc123 -o results.json
    """
    client = get_client(ctx)

    try:
        output_path = output or f"bulk_{job_id}.json"
        client.bulk.download(job_id, output_path)
        print_success(f"Downloaded results to {output_path}")

    except OathNetError as e:
        print_error(str(e))
        raise click.Abort()


@bulk.command("wait")
@click.argument("job_id")
@click.option("-o", "--output", help="Output file path after completion")
@click.option("--timeout", default=600, help="Timeout in seconds")
@click.pass_context
def wait(ctx: click.Context, job_id: str, output: str | None, timeout: int) -> None:
    """Wait for bulk search job to complete and optionally download.

    Example:
        oathnet bulk wait abc123
        oathnet bulk wait abc123 -o results.json
    """
    client = get_client(ctx)

    try:
        console.print(f"Waiting for job {job_id}...")
        result = client.bulk.wait_for_completion(job_id, timeout=timeout)

        if result.data:
            console.print(f"[green]Job completed with status: {result.data.status}[/green]")

            if output:
                client.bulk.download(job_id, output)
                print_success(f"Downloaded results to {output}")

    except TimeoutError:
        print_error(f"Job did not complete within {timeout} seconds")
        raise click.Abort()
    except OathNetError as e:
        print_error(str(e))
        raise click.Abort()
