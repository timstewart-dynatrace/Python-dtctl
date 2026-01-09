"""Cache management commands for dtctl."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from dtctl.utils.cache import cache

app = typer.Typer(no_args_is_help=True)
console = Console()


def is_plain_mode() -> bool:
    """Check if plain mode is enabled."""
    from dtctl.cli import state

    return state.plain


@app.command("stats")
def cache_stats() -> None:
    """Show cache statistics.

    Displays hit rate, entry counts, and cache configuration.
    """
    stats = cache.stats()

    if is_plain_mode():
        console.print_json(data=stats)
        return

    table = Table(title="Cache Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Active Entries", str(stats["active_entries"]))
    table.add_row("Expired Entries", str(stats["expired_entries"]))
    table.add_row("Total Entries", str(stats["total_entries"]))
    table.add_row("Hits", str(stats["hits"]))
    table.add_row("Misses", str(stats["misses"]))
    table.add_row("Hit Rate", f"{stats['hit_rate']}%")
    table.add_row("Default TTL", f"{stats['default_ttl']}s")

    console.print(table)


@app.command("clear")
def cache_clear(
    prefix: str = typer.Option(
        None, "--prefix", "-p", help="Only clear entries matching this prefix"
    ),
    expired_only: bool = typer.Option(
        False, "--expired", "-e", help="Only clear expired entries"
    ),
) -> None:
    """Clear cache entries.

    By default, clears all entries. Use --prefix to clear specific resource types.
    Use --expired to only clear expired entries.
    """
    if expired_only:
        count = cache.clear_expired()
        console.print(f"[green]Cleared {count} expired cache entries.[/green]")
    elif prefix:
        count = cache.clear_prefix(prefix)
        console.print(f"[green]Cleared {count} cache entries with prefix '{prefix}'.[/green]")
    else:
        count = cache.clear()
        console.print(f"[green]Cleared {count} cache entries.[/green]")


@app.command("keys")
def cache_keys(
    prefix: str = typer.Option(
        None, "--prefix", "-p", help="Filter keys by prefix"
    ),
) -> None:
    """List cache keys.

    Shows all current cache keys, optionally filtered by prefix.
    """
    keys = cache.keys()

    if prefix:
        keys = [k for k in keys if k.startswith(prefix)]

    if not keys:
        console.print("[yellow]No cache entries found.[/yellow]")
        return

    if is_plain_mode():
        for key in keys:
            console.print(key)
        return

    table = Table(title=f"Cache Keys ({len(keys)} entries)")
    table.add_column("Key", style="cyan")

    for key in sorted(keys):
        table.add_row(key)

    console.print(table)


@app.command("reset-stats")
def cache_reset_stats() -> None:
    """Reset cache hit/miss statistics.

    Resets counters while keeping cached data intact.
    """
    cache.reset_stats()
    console.print("[green]Cache statistics reset.[/green]")


@app.command("set-ttl")
def cache_set_ttl(
    ttl: int = typer.Argument(..., help="New default TTL in seconds"),
) -> None:
    """Set default cache TTL.

    Sets the default time-to-live for new cache entries.
    """
    if ttl < 0:
        console.print("[red]Error:[/red] TTL must be non-negative.")
        raise typer.Exit(1)

    cache.default_ttl = ttl
    console.print(f"[green]Default cache TTL set to {ttl} seconds.[/green]")
