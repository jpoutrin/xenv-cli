"""Rich console utilities for xenv."""

from rich.console import Console

# Global console instance
console = Console()


def print_error(message: str) -> None:
    """Print an error message.

    Args:
        message: Error message to display.
    """
    console.print(f"[red]Error:[/red] {message}")


def print_warning(message: str) -> None:
    """Print a warning message.

    Args:
        message: Warning message to display.
    """
    console.print(f"[yellow]\u26a0[/yellow] {message}")


def print_success(message: str) -> None:
    """Print a success message.

    Args:
        message: Success message to display.
    """
    console.print(f"[green]\u2713[/green] {message}")


def print_info(message: str) -> None:
    """Print an info message.

    Args:
        message: Info message to display.
    """
    console.print(f"[blue]\u2022[/blue] {message}")


def print_project_header(name: str, origin: str) -> None:
    """Print a project header.

    Args:
        name: Project name.
        origin: Project origin (host/path).
    """
    console.print(f"\n[bold]\U0001f4c1 {name}[/bold] [dim]({origin})[/dim]")
    console.print()
