"""Git repository operations."""

import subprocess
from pathlib import Path
from typing import Optional


class GitError(Exception):
    """Git operation failed."""

    pass


class GitService:
    """Git repository operations."""

    def get_root(self, path: Optional[Path] = None) -> Path:
        """Get git repository root directory.

        Args:
            path: Optional path to check. Uses cwd if not provided.

        Returns:
            Path to the git repository root.

        Raises:
            GitError: If not in a git repository.
        """
        cmd = ["git", "rev-parse", "--show-toplevel"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=path,
        )
        if result.returncode != 0:
            raise GitError("Not a git repository")
        return Path(result.stdout.strip())

    def get_origin(self, path: Optional[Path] = None) -> str:
        """Get remote origin URL.

        Args:
            path: Optional path to check. Uses cwd if not provided.

        Returns:
            The remote origin URL.

        Raises:
            GitError: If no remote origin is configured.
        """
        cmd = ["git", "remote", "get-url", "origin"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=path,
        )
        if result.returncode != 0:
            raise GitError("No remote origin configured")
        return result.stdout.strip()

    def is_git_repo(self, path: Optional[Path] = None) -> bool:
        """Check if we're in a git repository.

        Args:
            path: Optional path to check. Uses cwd if not provided.

        Returns:
            True if in a git repository.
        """
        cmd = ["git", "rev-parse", "--is-inside-work-tree"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=path,
        )
        return result.returncode == 0 and result.stdout.strip() == "true"

    def is_worktree(self, path: Optional[Path] = None) -> bool:
        """Check if current directory is a git worktree (not main repo).

        Args:
            path: Optional path to check. Uses cwd if not provided.

        Returns:
            True if in a worktree (not the main working tree).
        """
        cmd = ["git", "rev-parse", "--git-common-dir"]
        common_result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=path,
        )

        cmd = ["git", "rev-parse", "--git-dir"]
        dir_result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=path,
        )

        if common_result.returncode != 0 or dir_result.returncode != 0:
            return False

        # If git-dir != git-common-dir, we're in a worktree
        return common_result.stdout.strip() != dir_result.stdout.strip()

    def get_relative_path(self, path: Optional[Path] = None) -> str:
        """Get path relative to git root (for monorepo support).

        Args:
            path: Optional path to check. Uses cwd if not provided.

        Returns:
            Path relative to git root, or "." if at root.
        """
        root = self.get_root(path)
        current = Path.cwd() if path is None else path.resolve()
        try:
            rel = current.relative_to(root)
            return str(rel) if str(rel) else "."
        except ValueError:
            return "."

    @staticmethod
    def slugify_origin(origin: str) -> str:
        """Convert origin URL to filesystem-safe slug.

        Args:
            origin: Git remote origin URL.

        Returns:
            Filesystem-safe slug.

        Examples:
            git@github.com:user/repo.git -> github-com-user-repo
            https://github.com/user/repo.git -> github-com-user-repo
        """
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


# Global instance for convenience
git_service = GitService()
