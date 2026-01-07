"""xenv CLI entry point."""

import typer

from xenv_cli import __version__
from xenv_cli.commands import backup, delete, hook, init, list_cmd, save, status, sync

app = typer.Typer(
    name="xenv",
    help="Never lose a .env.local ever.",
    no_args_is_help=True,
)


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        typer.echo(f"xenv version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """xenv - Never lose a .env.local ever.

    Centralized .env.local file management with git-aware, worktree-native,
    and direnv-integrated local environment variable file management.
    """
    pass


# Register commands
app.command(name="init")(init.init_cmd)
app.command(name="save")(save.save_cmd)
app.command(name="list")(list_cmd.list_cmd)
app.command(name="delete")(delete.delete_cmd)
app.command(name="backup")(backup.backup_cmd)
app.command(name="hook")(hook.hook_cmd)
app.command(name="sync")(sync.sync_cmd)
app.command(name="status")(status.status_cmd)


if __name__ == "__main__":
    app()
