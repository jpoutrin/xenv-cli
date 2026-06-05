"""Configuration management service."""

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

import tomli_w

from xenv_cli.utils.paths import get_config_file, get_conf_home, get_projects_file
from xenv_cli.utils.permissions import ensure_secure_dir, ensure_secure_file


@dataclass
class Settings:
    """Global xenv settings."""

    conf_home: str = ".config/xenv"
    env_patterns: List[str] = field(
        default_factory=lambda: [
            ".env.local",
            ".env.development",
            ".env.development.local",
            ".env.test",
            ".env.test.local",
        ]
    )
    backup_tool: str = "plakar"
    auto_backup: bool = False
    verbosity: str = "normal"

    # Hook settings
    hook_enabled: bool = True
    hook_cache_ttl: int = 2
    hook_output: str = "default"
    hook_auto_save: bool = True
    hook_auto_restore: bool = True


@dataclass
class ProjectEntry:
    """Project entry in the registry."""

    origin: str
    paths: List[str] = field(default_factory=list)
    env_files: List[str] = field(default_factory=list)


class ConfigManager:
    """Manages xenv configuration files."""

    def __init__(self) -> None:
        self._settings: Optional[Settings] = None
        self._projects: Optional[List[ProjectEntry]] = None

    def ensure_conf_home(self) -> Path:
        """Ensure CONF_HOME directory exists with proper permissions.

        Returns:
            Path to CONF_HOME.
        """
        conf_home = get_conf_home()
        ensure_secure_dir(conf_home)
        ensure_secure_dir(conf_home / "origins")
        return conf_home

    def load_settings(self) -> Settings:
        """Load global settings from config.toml.

        Returns:
            Settings object with loaded or default values.
        """
        if self._settings is not None:
            return self._settings

        config_file = get_config_file()
        if config_file.exists():
            with open(config_file, "rb") as f:
                data = tomllib.load(f)

            settings_data = data.get("settings", {})
            backup_data = data.get("backup", {})
            display_data = data.get("display", {})
            hook_data = data.get("hook", {})

            self._settings = Settings(
                conf_home=settings_data.get("conf_home", ".config/xenv"),
                env_patterns=settings_data.get(
                    "env_patterns",
                    [
                        ".env.local",
                        ".env.development",
                        ".env.development.local",
                        ".env.test",
                        ".env.test.local",
                    ],
                ),
                backup_tool=backup_data.get("tool", "plakar"),
                auto_backup=backup_data.get("auto_backup", False),
                verbosity=display_data.get("verbosity", "normal"),
                hook_enabled=hook_data.get("enabled", True),
                hook_cache_ttl=hook_data.get("cache_ttl", 2),
                hook_output=hook_data.get("output", "default"),
                hook_auto_save=hook_data.get("auto_save", True),
                hook_auto_restore=hook_data.get("auto_restore", True),
            )
        else:
            self._settings = Settings()

        return self._settings

    def save_settings(self, settings: Settings) -> None:
        """Save settings to config.toml.

        Args:
            settings: Settings to save.
        """
        self.ensure_conf_home()
        config_file = get_config_file()

        data: Dict[str, Any] = {
            "settings": {
                "conf_home": settings.conf_home,
                "env_patterns": settings.env_patterns,
            },
            "backup": {
                "tool": settings.backup_tool,
                "auto_backup": settings.auto_backup,
            },
            "display": {
                "verbosity": settings.verbosity,
            },
            "hook": {
                "enabled": settings.hook_enabled,
                "cache_ttl": settings.hook_cache_ttl,
                "output": settings.hook_output,
                "auto_save": settings.hook_auto_save,
                "auto_restore": settings.hook_auto_restore,
            },
        }

        with open(config_file, "wb") as f:
            tomli_w.dump(data, f)

        ensure_secure_file(config_file)
        self._settings = settings

    def load_projects(self) -> List[ProjectEntry]:
        """Load project registry from projects.toml.

        Returns:
            List of project entries.
        """
        if self._projects is not None:
            return self._projects

        projects_file = get_projects_file()
        if projects_file.exists():
            with open(projects_file, "rb") as f:
                data = tomllib.load(f)

            self._projects = []
            for proj in data.get("projects", []):
                self._projects.append(
                    ProjectEntry(
                        origin=proj.get("origin", ""),
                        paths=proj.get("paths", []),
                        env_files=proj.get("env_files", []),
                    )
                )
        else:
            self._projects = []

        return self._projects

    def save_projects(self, projects: List[ProjectEntry]) -> None:
        """Save project registry to projects.toml.

        Args:
            projects: List of project entries to save.
        """
        self.ensure_conf_home()
        projects_file = get_projects_file()

        data: Dict[str, Any] = {
            "projects": [
                {
                    "origin": p.origin,
                    "paths": p.paths,
                    "env_files": p.env_files,
                }
                for p in projects
            ]
        }

        with open(projects_file, "wb") as f:
            tomli_w.dump(data, f)

        ensure_secure_file(projects_file)
        self._projects = projects

    def get_project(self, origin: str) -> Optional[ProjectEntry]:
        """Get a project by origin.

        Args:
            origin: Git remote origin URL.

        Returns:
            ProjectEntry if found, None otherwise.
        """
        projects = self.load_projects()
        for project in projects:
            if project.origin == origin:
                return project
        return None

    def update_project(
        self,
        origin: str,
        path: Optional[str] = None,
        env_files: Optional[List[str]] = None,
    ) -> ProjectEntry:
        """Update or create a project entry.

        Args:
            origin: Git remote origin URL.
            path: Optional path to add to the project.
            env_files: Optional list of env files to add.

        Returns:
            Updated or created ProjectEntry.
        """
        projects = self.load_projects()

        # Find existing project
        project = None
        for p in projects:
            if p.origin == origin:
                project = p
                break

        if project is None:
            # Create new project
            project = ProjectEntry(origin=origin)
            projects.append(project)

        # Update path
        if path and path not in project.paths:
            project.paths.append(path)

        # Update env files
        if env_files:
            for ef in env_files:
                if ef not in project.env_files:
                    project.env_files.append(ef)

        self.save_projects(projects)
        return project

    def invalidate_cache(self) -> None:
        """Clear cached settings and projects."""
        self._settings = None
        self._projects = None


# Global instance
config_manager = ConfigManager()
