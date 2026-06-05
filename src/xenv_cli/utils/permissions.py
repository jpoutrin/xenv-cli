"""File permissions utilities for xenv."""

import os
import stat
from pathlib import Path
from typing import Optional

# Secure permission modes
DIR_MODE = 0o700  # rwx------
FILE_MODE = 0o600  # rw-------


class PermissionError(Exception):
    """File permission issue."""

    pass


def ensure_secure_dir(path: Path) -> None:
    """Create directory with secure permissions.

    Args:
        path: Directory path to create/secure.
    """
    path.mkdir(parents=True, exist_ok=True)
    os.chmod(path, DIR_MODE)


def ensure_secure_file(path: Path) -> None:
    """Set secure permissions on file.

    Args:
        path: File path to secure.
    """
    os.chmod(path, FILE_MODE)


def check_permissions(path: Path) -> Optional[str]:
    """Check if file/dir has secure permissions.

    Args:
        path: Path to check.

    Returns:
        None if secure, warning message if insecure.
    """
    if not path.exists():
        return None

    mode = os.stat(path).st_mode
    if path.is_dir():
        if mode & (stat.S_IRWXG | stat.S_IRWXO):
            return f"Insecure permissions on directory: {path} (should be 700)"
    else:
        if mode & (stat.S_IRWXG | stat.S_IRWXO):
            return f"Insecure permissions on file: {path} (should be 600)"
    return None


def warn_if_insecure(path: Path, console) -> None:
    """Print warning if permissions are insecure.

    Args:
        path: Path to check.
        console: Rich console for output.
    """
    warning = check_permissions(path)
    if warning:
        console.print(f"[yellow]\u26a0 {warning}[/yellow]")
