"""xenv backup command."""

import shutil
import subprocess

import typer

from xenv_cli.utils.console import console, print_error, print_success
from xenv_cli.utils.paths import get_conf_home


def backup_cmd(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show Plakar output.",
    ),
) -> None:
    """Trigger Plakar backup of the xenv configuration.

    Backs up all env files and configuration to Plakar for secure storage.
    """
    # Check if plakar is installed
    if not shutil.which("plakar"):
        print_error("Plakar not installed")
        console.print("\nInstall Plakar to enable encrypted backups:")
        console.print("  https://github.com/PlakarKorp/plakar")
        raise typer.Exit(code=1)

    conf_home = get_conf_home()

    if not conf_home.exists():
        print_error("No xenv configuration to backup")
        console.print("\nRun `xenv init` in a git repository first.")
        raise typer.Exit(code=1)

    # Count files
    file_count = 0
    total_size = 0
    for path in conf_home.rglob("*"):
        if path.is_file():
            file_count += 1
            total_size += path.stat().st_size

    # Run plakar backup
    cmd = ["plakar", "push", str(conf_home)]

    if verbose:
        result = subprocess.run(cmd)
    else:
        result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print_error("Backup failed")
        if not verbose and result.stderr:
            console.print(f"[dim]{result.stderr}[/dim]")
        raise typer.Exit(code=1)

    # Output
    size_kb = total_size / 1024
    print_success("Backup complete")
    console.print(f"  {file_count} files, {size_kb:.1f} KB")

    if verbose and result.stdout:
        console.print(f"\n[dim]{result.stdout}[/dim]")
