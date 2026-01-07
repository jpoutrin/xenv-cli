"""xenv init command."""

from pathlib import Path
from typing import Optional

import typer

from xenv_cli.models.env_file import SyncStatus
from xenv_cli.services.config import config_manager
from xenv_cli.services.env_file import env_file_manager
from xenv_cli.services.git import GitError, git_service
from xenv_cli.utils.console import console, print_error, print_project_header, print_success


def init_cmd(
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress output unless there's an action or warning.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite local files with stored versions.",
    ),
) -> None:
    """Create or restore env files for the current project.

    Restores env files from the store if they exist there but not locally.
    Saves env files to the store if they exist locally but not in the store.
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
        restored = []
        saved = []
        synced = []

        settings = config_manager.load_settings()

        for env_file in env_files:
            if env_file.status == SyncStatus.MISSING_LOCAL:
                # Restore from store
                if env_file.store_path:
                    env_file_manager.copy_to_project(
                        env_file.store_path, git_root, relative_path
                    )
                    restored.append(env_file.name)

            elif env_file.status == SyncStatus.MISSING_STORE:
                # Initial save to store
                if env_file.local_path:
                    env_file_manager.copy_to_store(
                        env_file.local_path, origin_slug, relative_path
                    )
                    saved.append(env_file.name)

            elif env_file.status in (SyncStatus.LOCAL_NEWER, SyncStatus.STORE_NEWER) and force:
                # Force restore from store
                if env_file.store_path:
                    env_file_manager.copy_to_project(
                        env_file.store_path, git_root, relative_path
                    )
                    restored.append(env_file.name)

            elif env_file.status == SyncStatus.SYNCED:
                synced.append(env_file.name)

        # Update project registry
        tracked_files = [ef.full_relative_path for ef in env_files]
        config_manager.update_project(
            origin=origin,
            path=str(Path.cwd()),
            env_files=tracked_files,
        )

        # Output
        if quiet:
            # Only show if there were actions
            if restored or saved:
                actions = []
                if restored:
                    actions.append(f"restored {len(restored)} env file(s)")
                if saved:
                    actions.append(f"saved {len(saved)} env file(s)")
                console.print(f"xenv: {', '.join(actions)} for {git_root.name}")
        else:
            # Get display info from project model
            from xenv_cli.models.project import Project

            project = Project(origin=origin)
            print_project_header(project.display_name, project.host_and_path)

            for name in restored:
                print_success(f"Restored {name}")

            for name in saved:
                print_success(f"Saved {name}")

            for name in synced:
                console.print(f"  [green]\u2713[/green] {name} (synced)")

            # Show local changes if not forcing
            for env_file in env_files:
                if env_file.status in (SyncStatus.LOCAL_NEWER, SyncStatus.STORE_NEWER) and not force:
                    console.print(
                        f"  [yellow]\u26a0[/yellow] {env_file.name} (local changes)"
                    )

            if not env_files:
                console.print("  [dim]No env files found[/dim]")

    except GitError as e:
        print_error(str(e))
        if "Not a git repository" in str(e):
            console.print("\nThis command must be run inside a git repository.")
            console.print("Run `git init` to initialize a new repository.")
        elif "No remote origin" in str(e):
            console.print("\nThis command requires a remote origin.")
            console.print("Run `git remote add origin <url>` to add one.")
        raise typer.Exit(code=2)
