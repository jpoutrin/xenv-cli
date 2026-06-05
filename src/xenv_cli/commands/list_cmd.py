"""xenv list command."""

import json
from typing import Optional

import typer

from xenv_cli.models.env_file import SyncStatus
from xenv_cli.models.project import Project
from xenv_cli.services.config import config_manager
from xenv_cli.services.env_file import env_file_manager
from xenv_cli.services.git import GitError, git_service
from xenv_cli.utils.console import console, print_error, print_project_header
from xenv_cli.utils.paths import get_origin_store_path


def list_cmd(
    all_projects: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="List all tracked projects.",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        "-j",
        help="Output as JSON.",
    ),
) -> None:
    """Show env files for current project or all projects.

    Lists env files with their sync status.
    """
    if all_projects:
        _list_all_projects(json_output)
    else:
        _list_current_project(json_output)


def _list_current_project(json_output: bool) -> None:
    """List env files for the current project."""
    try:
        # Get project info
        origin, origin_slug, git_root = env_file_manager.get_project_info()
        relative_path = git_service.get_relative_path()

        # Get env file status
        env_files = env_file_manager.get_env_files_status(
            git_root, origin_slug, relative_path
        )

        if json_output:
            data = {
                "origin": origin,
                "origin_slug": origin_slug,
                "git_root": str(git_root),
                "relative_path": relative_path,
                "env_files": [
                    {
                        "name": ef.name,
                        "relative_path": ef.relative_path,
                        "status": ef.status.value,
                        "local_path": str(ef.local_path) if ef.local_path else None,
                        "store_path": str(ef.store_path) if ef.store_path else None,
                    }
                    for ef in env_files
                ],
            }
            console.print_json(json.dumps(data))
        else:
            project = Project(origin=origin)
            print_project_header(project.display_name, project.host_and_path)

            if not env_files:
                console.print("  [dim]No env files found[/dim]")
                return

            for env_file in env_files:
                status_color = {
                    SyncStatus.SYNCED: "green",
                    SyncStatus.LOCAL_NEWER: "yellow",
                    SyncStatus.STORE_NEWER: "cyan",
                    SyncStatus.MISSING_LOCAL: "red",
                    SyncStatus.MISSING_STORE: "blue",
                }.get(env_file.status, "white")

                symbol = env_file.get_status_symbol()
                status_text = env_file.get_status_text()

                console.print(
                    f"  {env_file.name:30} [{status_color}]{symbol}[/{status_color}] {status_text}"
                )

    except GitError as e:
        print_error(str(e))
        raise typer.Exit(code=2)


def _list_all_projects(json_output: bool) -> None:
    """List all tracked projects."""
    projects = config_manager.load_projects()

    if not projects:
        console.print("[dim]No projects tracked yet.[/dim]")
        console.print("Run `xenv init` in a git repository to start tracking.")
        return

    if json_output:
        data = {
            "projects": [
                {
                    "origin": p.origin,
                    "paths": p.paths,
                    "env_files": p.env_files,
                }
                for p in projects
            ]
        }
        console.print_json(json.dumps(data))
    else:
        for project_entry in projects:
            project = Project(origin=project_entry.origin)
            console.print(f"\n[bold]\U0001f4c1 {project.host_and_path}[/bold]")

            # Try to get status for stored env files
            origin_slug = project.origin_slug
            store_path = get_origin_store_path(origin_slug)

            if store_path.exists():
                settings = config_manager.load_settings()
                for pattern in settings.env_patterns:
                    env_path = store_path / pattern
                    if env_path.exists():
                        console.print(f"  {pattern:30} [green]\u2713[/green] stored")

                # Check subdirectories for monorepo
                for subdir in store_path.iterdir():
                    if subdir.is_dir():
                        for pattern in settings.env_patterns:
                            env_path = subdir / pattern
                            if env_path.exists():
                                rel = subdir.relative_to(store_path)
                                console.print(
                                    f"  {rel}/{pattern}".ljust(30)
                                    + " [green]\u2713[/green] stored"
                                )
            else:
                console.print("  [dim]No env files stored[/dim]")
