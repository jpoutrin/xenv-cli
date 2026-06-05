"""xenv delete command."""

from pathlib import Path

import typer

from xenv_cli.services.config import config_manager
from xenv_cli.services.env_file import env_file_manager
from xenv_cli.services.git import GitError, git_service
from xenv_cli.utils.console import console, print_error, print_success
from xenv_cli.utils.paths import get_origin_store_path


def delete_cmd(
    filename: str = typer.Argument(
        ...,
        help="Env file to delete (e.g., '.env.local').",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation prompt.",
    ),
) -> None:
    """Remove env file from project (keeps backup in store).

    Deletes the local env file but preserves the backup in the store.
    Use this to clean up local files while keeping them safe.
    """
    try:
        # Get project info
        origin, origin_slug, git_root = env_file_manager.get_project_info()
        relative_path = git_service.get_relative_path()

        # Build local path
        local_dir = git_root
        if relative_path and relative_path != ".":
            local_dir = git_root / relative_path

        local_path = local_dir / filename

        if not local_path.exists():
            print_error(f"{filename} not found in project")
            raise typer.Exit(code=4)

        # Ensure backup exists in store
        store_dir = env_file_manager.get_store_path(origin_slug, relative_path)
        store_path = store_dir / filename

        if not store_path.exists():
            # Create backup first
            env_file_manager.copy_to_store(local_path, origin_slug, relative_path)
            console.print(f"[dim]Created backup before deletion[/dim]")

        # Confirm deletion
        if not force:
            confirm = typer.confirm(
                f"Delete {filename} from project? (backup preserved in store)"
            )
            if not confirm:
                console.print("[dim]Cancelled[/dim]")
                raise typer.Exit(code=0)

        # Delete local file
        env_file_manager.delete_local(local_path)

        # Output
        print_success(f"Removed {filename} from {git_root.name}")
        console.print(f"[dim]Backup preserved: {store_path}[/dim]")

    except GitError as e:
        print_error(str(e))
        raise typer.Exit(code=2)
