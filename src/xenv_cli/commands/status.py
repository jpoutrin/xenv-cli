"""xenv status command."""

import typer

from xenv_cli.models.env_file import SyncStatus
from xenv_cli.services.env_file import env_file_manager
from xenv_cli.services.git import GitError, git_service
from xenv_cli.utils.console import console, print_error


def status_cmd(
    porcelain: bool = typer.Option(
        False,
        "--porcelain",
        "-p",
        help="Machine-readable output for scripts.",
    ),
) -> None:
    """Show sync status without making changes.

    Displays the status of each env file:
    - synced: identical in local and store
    - local changes: local file is newer/different
    - missing locally: exists in store but not local
    - new: exists locally but not in store
    """
    try:
        # Get project info
        origin, origin_slug, git_root = env_file_manager.get_project_info()
        relative_path = git_service.get_relative_path()

        # Get env file status
        env_files = env_file_manager.get_env_files_status(
            git_root, origin_slug, relative_path
        )

        if not env_files:
            if not porcelain:
                console.print("[dim]No env files found[/dim]")
            return

        if porcelain:
            # Machine-readable format
            for env_file in env_files:
                code = _get_porcelain_code(env_file.status)
                console.print(f"{code} {env_file.name}")
        else:
            # Human-readable format
            for env_file in env_files:
                symbol = _get_status_symbol(env_file.status)
                hint = _get_status_hint(env_file.status)
                console.print(f"{env_file.name:30} {symbol} {hint}")

    except GitError as e:
        print_error(str(e))
        raise typer.Exit(code=2)


def _get_porcelain_code(status: SyncStatus) -> str:
    """Get porcelain status code."""
    codes = {
        SyncStatus.SYNCED: "=",
        SyncStatus.LOCAL_NEWER: "M",
        SyncStatus.STORE_NEWER: "S",
        SyncStatus.MISSING_LOCAL: "R",
        SyncStatus.MISSING_STORE: "A",
    }
    return codes.get(status, "?")


def _get_status_symbol(status: SyncStatus) -> str:
    """Get human-readable status symbol."""
    symbols = {
        SyncStatus.SYNCED: "[green]\u2713[/green]",
        SyncStatus.LOCAL_NEWER: "[yellow]\u2191[/yellow]",
        SyncStatus.STORE_NEWER: "[cyan]\u2193[/cyan]",
        SyncStatus.MISSING_LOCAL: "[red]\u2193[/red]",
        SyncStatus.MISSING_STORE: "[blue]+[/blue]",
    }
    return symbols.get(status, "?")


def _get_status_hint(status: SyncStatus) -> str:
    """Get status hint text."""
    hints = {
        SyncStatus.SYNCED: "synced",
        SyncStatus.LOCAL_NEWER: "local newer (will save)",
        SyncStatus.STORE_NEWER: "store newer (will restore)",
        SyncStatus.MISSING_LOCAL: "missing locally (will restore)",
        SyncStatus.MISSING_STORE: "new (will save)",
    }
    return hints.get(status, "unknown")
