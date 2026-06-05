"""xenv sync command."""

from pathlib import Path

import typer

from xenv_cli.models.env_file import SyncStatus
from xenv_cli.services.config import config_manager
from xenv_cli.services.env_file import env_file_manager
from xenv_cli.services.git import GitError, git_service
from xenv_cli.utils.console import console


def sync_cmd(
    silent: bool = typer.Option(
        False,
        "--silent",
        "-s",
        help="No output at all.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed operations including 'in sync' status.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        help="Show what would happen without doing it.",
    ),
) -> None:
    """Combined init + save in one command.

    This is the workhorse behind the shell hook. It:
    - Restores missing .env files from the store
    - Saves modified .env files to the store
    - Skips files that are already in sync
    """
    try:
        # Get project info
        origin, origin_slug, git_root = env_file_manager.get_project_info()
        relative_path = git_service.get_relative_path()

        # Get env file status
        env_files = env_file_manager.get_env_files_status(
            git_root, origin_slug, relative_path
        )

        # Track actions
        saved = []
        restored = []
        synced = []

        for env_file in env_files:
            if env_file.status == SyncStatus.MISSING_LOCAL:
                # Restore from store
                if env_file.store_path:
                    if not dry_run:
                        env_file_manager.copy_to_project(
                            env_file.store_path, git_root, relative_path
                        )
                    restored.append(env_file.name)

            elif env_file.status == SyncStatus.MISSING_STORE:
                # Save to store (new file)
                if env_file.local_path:
                    if not dry_run:
                        env_file_manager.copy_to_store(
                            env_file.local_path, origin_slug, relative_path
                        )
                    saved.append(env_file.name)

            elif env_file.status == SyncStatus.LOCAL_NEWER:
                # Save to store (local is newer)
                if env_file.local_path:
                    if not dry_run:
                        env_file_manager.copy_to_store(
                            env_file.local_path, origin_slug, relative_path
                        )
                    saved.append(env_file.name)

            elif env_file.status == SyncStatus.STORE_NEWER:
                # Restore from store (store has newer version)
                if env_file.store_path:
                    if not dry_run:
                        env_file_manager.copy_to_project(
                            env_file.store_path, git_root, relative_path
                        )
                    restored.append(env_file.name)

            elif env_file.status == SyncStatus.SYNCED:
                synced.append(env_file.name)

        # Update project registry
        if not dry_run:
            tracked_files = [ef.full_relative_path for ef in env_files]
            config_manager.update_project(
                origin=origin,
                path=str(Path.cwd()),
                env_files=tracked_files,
            )

        # Output
        if silent:
            return

        if dry_run:
            # Show what would happen
            for name in saved:
                console.print(f"xenv: would save {name}")
            for name in restored:
                console.print(f"xenv: would restore {name}")
            if verbose:
                for name in synced:
                    console.print(f"{name}: in sync")
        elif verbose:
            # Show detailed info
            for name in saved:
                console.print(f"{name}: saved")
            for name in restored:
                console.print(f"{name}: restored")
            for name in synced:
                console.print(f"{name}: in sync \u2713")
        else:
            # Default output - only show actions
            if saved or restored:
                actions = []
                if saved:
                    actions.append(f"saved {', '.join(saved)}")
                if restored:
                    actions.append(f"restored {', '.join(restored)}")
                console.print(f"xenv: {', '.join(actions)}")

    except GitError:
        # Silent fail for hook usage - not in a git repo
        if verbose:
            console.print("[dim]Not in a git repository[/dim]")
