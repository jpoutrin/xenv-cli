"""Path utilities for xenv."""

import os
from pathlib import Path


def get_conf_home() -> Path:
    """Get the xenv configuration home directory.

    Uses XDG_CONFIG_HOME if set, otherwise ~/.config/xenv/

    Returns:
        Path to the xenv configuration directory.
    """
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config:
        return Path(xdg_config) / "xenv"
    return Path.home() / ".config" / "xenv"


def get_origins_dir() -> Path:
    """Get the origins directory within CONF_HOME.

    Returns:
        Path to the origins directory.
    """
    return get_conf_home() / "origins"


def get_origin_store_path(origin_slug: str) -> Path:
    """Get the store path for a specific origin.

    Args:
        origin_slug: Slugified origin URL.

    Returns:
        Path to the origin's storage directory.
    """
    return get_origins_dir() / origin_slug


def get_config_file() -> Path:
    """Get the global config file path.

    Returns:
        Path to config.toml.
    """
    return get_conf_home() / "config.toml"


def get_projects_file() -> Path:
    """Get the projects registry file path.

    Returns:
        Path to projects.toml.
    """
    return get_conf_home() / "projects.toml"
