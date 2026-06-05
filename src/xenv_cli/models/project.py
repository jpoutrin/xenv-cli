"""Project model."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class Project:
    """Represents a tracked git project."""

    origin: str  # Git remote origin URL
    paths: List[Path] = field(default_factory=list)  # Registered local paths (worktrees)
    env_files: List[str] = field(default_factory=list)  # Tracked env file names

    @property
    def origin_slug(self) -> str:
        """Slugified origin for filesystem storage.

        Examples:
            git@github.com:user/repo.git -> github-com-user-repo
            https://github.com/user/repo.git -> github-com-user-repo
        """
        return self._slugify_origin(self.origin)

    @staticmethod
    def _slugify_origin(origin: str) -> str:
        """Convert origin URL to filesystem-safe slug."""
        # Remove protocol
        slug = origin.replace("git@", "").replace("https://", "").replace("http://", "")
        # Remove .git suffix
        if slug.endswith(".git"):
            slug = slug[:-4]
        # Replace separators with dashes
        slug = slug.replace(":", "-").replace("/", "-")
        # Clean up multiple dashes
        while "--" in slug:
            slug = slug.replace("--", "-")
        return slug.strip("-")

    @property
    def display_name(self) -> str:
        """Get a human-readable display name."""
        # Extract repo name from origin
        slug = self.origin_slug
        parts = slug.split("-")
        if len(parts) >= 2:
            # Return last two parts (user/repo)
            return "/".join(parts[-2:])
        return slug

    @property
    def host_and_path(self) -> str:
        """Get host and path for display (e.g., github.com/user/repo)."""
        origin = self.origin
        # Remove protocol
        origin = origin.replace("git@", "").replace("https://", "").replace("http://", "")
        # Remove .git suffix
        if origin.endswith(".git"):
            origin = origin[:-4]
        # Replace : with /
        origin = origin.replace(":", "/")
        return origin
