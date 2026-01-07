"""xenv save command."""

from pathlib import Path
from typing import Optional

import typer

from xenv_cli.models.env_file import SyncStatus
from xenv_cli.services.config import config_manager
from xenv_cli.services.env_file import env_file_manager
from xenv_cli.services.git import GitError, git_service
from xenv_cli.utils.console import console, print_error, print_project_header, print_success


def save_cmd(
    filename: Optional[str] = typer.Argument(
        None,
        help="Specific env file to save (e.g., '.env.local').",
    ),
    all_files: bool = typer.Option(
        True,
        "--all",
        "-a",
        help="Save all env files (default behavior).",
    ),
) -> None:
    """Persist local changes back to the store.

    Copies local env files to the centralized store for safekeeping.
    Only saves files that have changed or are new.
    """
    try:
        # Get project info
        origin, origin_slug, git_root = env_file_manager.get_project_info()
        relative_path = git_service.get_relative_path()

        # Determine patterns to check
        settings = config_manager.load_settings()
        if filename:
            patterns = [filename]
        else:
            patterns = settings.env_patterns

        # Get env file status
        env_files = env_file_manager.get_env_files_status(
            git_root, origin_slug, relative_path, patterns
        )

        # Track actions
        saved = []
        unchanged = []
        protected = []

        for env_file in env_files:
            if env_file.local_path and env_file.local_path.exists():
                if env_file.status in (SyncStatus.LOCAL_NEWER, SyncStatus.MISSING_STORE):
                    env_file_manager.copy_to_store(
                        env_file.local_path, origin_slug, relative_path
                    )
                    saved.append(env_file.name)
                elif env_file.status == SyncStatus.STORE_NEWER:
                    # Don't overwrite - store has newer version
                    protected.append(env_file.name)
                elif env_file.status == SyncStatus.SYNCED:
                    unchanged.append(env_file.name)

        # Update project registry
        tracked_files = [ef.full_relative_path for ef in env_files if ef.local_path]
        config_manager.update_project(
            origin=origin,
            path=str(Path.cwd()),
            env_files=tracked_files,
        )

        # Output
        from xenv_cli.models.project import Project

        project = Project(origin=origin)
        print_project_header(project.display_name, project.host_and_path)

        for name in saved:
            print_success(f"Saved {name}")

        for name in protected:
            console.print(f"  [yellow]\u26a0[/yellow] {name} (store is newer - not overwritten)")

        for name in unchanged:
            console.print(f"  [dim]\u00b7[/dim] {name} (no changes)")

        if not saved and not unchanged and not protected:
            if filename:
                print_error(f"File {filename} not found")
                raise typer.Exit(code=4)
            console.print("  [dim]No env files found[/dim]")

    except GitError as e:
        print_error(str(e))
        raise typer.Exit(code=2)
