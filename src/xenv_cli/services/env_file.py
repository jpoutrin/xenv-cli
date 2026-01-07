"""Environment file operations service."""

import hashlib
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from xenv_cli.models.env_file import EnvFile, SyncStatus
from xenv_cli.services.config import config_manager
from xenv_cli.services.git import GitService, git_service
from xenv_cli.utils.paths import get_origin_store_path
from xenv_cli.utils.permissions import ensure_secure_dir, ensure_secure_file


class EnvFileManager:
    """Manages environment file operations."""

    def __init__(self, git: Optional[GitService] = None) -> None:
        self.git = git or git_service

    def get_project_info(self, path: Optional[Path] = None) -> Tuple[str, str, Path]:
        """Get project information for current directory.

        Args:
            path: Optional path. Uses cwd if not provided.

        Returns:
            Tuple of (origin, origin_slug, git_root).

        Raises:
            GitError: If not in a git repo or no origin.
        """
        git_root = self.git.get_root(path)
        origin = self.git.get_origin(path)
        origin_slug = self.git.slugify_origin(origin)
        return origin, origin_slug, git_root

    def get_store_path(self, origin_slug: str, relative_path: str = ".") -> Path:
        """Get the store path for env files.

        Args:
            origin_slug: Slugified origin URL.
            relative_path: Path relative to git root.

        Returns:
            Path to store directory.
        """
        store_path = get_origin_store_path(origin_slug)
        if relative_path and relative_path != ".":
            store_path = store_path / relative_path
        return store_path

    def find_local_env_files(
        self,
        git_root: Path,
        relative_path: str = ".",
        patterns: Optional[List[str]] = None,
    ) -> List[Path]:
        """Find env files in the local project directory.

        Args:
            git_root: Git repository root.
            relative_path: Path relative to git root.
            patterns: Env file patterns to search for.

        Returns:
            List of found env file paths.
        """
        if patterns is None:
            settings = config_manager.load_settings()
            patterns = settings.env_patterns

        search_dir = git_root
        if relative_path and relative_path != ".":
            search_dir = git_root / relative_path

        found = []
        for pattern in patterns:
            env_path = search_dir / pattern
            if env_path.exists() and env_path.is_file():
                found.append(env_path)

        return found

    def find_stored_env_files(
        self,
        origin_slug: str,
        relative_path: str = ".",
        patterns: Optional[List[str]] = None,
    ) -> List[Path]:
        """Find env files in the store.

        Args:
            origin_slug: Slugified origin URL.
            relative_path: Path relative to git root.
            patterns: Env file patterns to search for.

        Returns:
            List of found env file paths.
        """
        if patterns is None:
            settings = config_manager.load_settings()
            patterns = settings.env_patterns

        store_dir = self.get_store_path(origin_slug, relative_path)
        if not store_dir.exists():
            return []

        found = []
        for pattern in patterns:
            env_path = store_dir / pattern
            if env_path.exists() and env_path.is_file():
                found.append(env_path)

        return found

    def get_file_mtime(self, path: Path) -> Optional[datetime]:
        """Get file modification time.

        Args:
            path: File path.

        Returns:
            Modification datetime or None if file doesn't exist.
        """
        if not path.exists():
            return None
        return datetime.fromtimestamp(path.stat().st_mtime)

    def get_file_hash(self, path: Path) -> Optional[str]:
        """Get file content hash.

        Args:
            path: File path.

        Returns:
            SHA256 hash or None if file doesn't exist.
        """
        if not path.exists():
            return None
        content = path.read_bytes()
        return hashlib.sha256(content).hexdigest()

    def compare_files(self, local_path: Path, store_path: Path) -> SyncStatus:
        """Compare local and stored env files.

        Args:
            local_path: Path to local file.
            store_path: Path to stored file.

        Returns:
            SyncStatus indicating the comparison result.
        """
        local_exists = local_path.exists()
        store_exists = store_path.exists()

        if not local_exists and not store_exists:
            return SyncStatus.SYNCED

        if local_exists and not store_exists:
            return SyncStatus.MISSING_STORE

        if not local_exists and store_exists:
            return SyncStatus.MISSING_LOCAL

        # Both exist - compare content
        local_hash = self.get_file_hash(local_path)
        store_hash = self.get_file_hash(store_path)

        if local_hash == store_hash:
            return SyncStatus.SYNCED

        # Files differ - check which is newer by mtime
        local_mtime = self.get_file_mtime(local_path)
        store_mtime = self.get_file_mtime(store_path)

        if local_mtime and store_mtime:
            if local_mtime > store_mtime:
                return SyncStatus.LOCAL_NEWER
            else:
                return SyncStatus.STORE_NEWER

        # Fallback: if we can't determine, assume local is newer
        return SyncStatus.LOCAL_NEWER

    def get_env_files_status(
        self,
        git_root: Path,
        origin_slug: str,
        relative_path: str = ".",
        patterns: Optional[List[str]] = None,
    ) -> List[EnvFile]:
        """Get status of all env files for the current project.

        Args:
            git_root: Git repository root.
            origin_slug: Slugified origin URL.
            relative_path: Path relative to git root.
            patterns: Env file patterns to search for.

        Returns:
            List of EnvFile objects with status.
        """
        if patterns is None:
            settings = config_manager.load_settings()
            patterns = settings.env_patterns

        local_dir = git_root
        if relative_path and relative_path != ".":
            local_dir = git_root / relative_path

        store_dir = self.get_store_path(origin_slug, relative_path)

        env_files = []
        seen_names = set()

        # Check all patterns
        for pattern in patterns:
            local_path = local_dir / pattern
            store_path = store_dir / pattern

            # Skip if neither exists
            if not local_path.exists() and not store_path.exists():
                continue

            status = self.compare_files(local_path, store_path)

            env_file = EnvFile(
                name=pattern,
                relative_path=relative_path,
                local_path=local_path if local_path.exists() else None,
                store_path=store_path if store_path.exists() else None,
                status=status,
                local_mtime=self.get_file_mtime(local_path),
                store_mtime=self.get_file_mtime(store_path),
            )

            env_files.append(env_file)
            seen_names.add(pattern)

        return env_files

    def copy_to_store(
        self,
        local_path: Path,
        origin_slug: str,
        relative_path: str = ".",
    ) -> Path:
        """Copy env file from project to store.

        Args:
            local_path: Source file path.
            origin_slug: Slugified origin URL.
            relative_path: Path relative to git root.

        Returns:
            Path to the stored file.
        """
        store_dir = self.get_store_path(origin_slug, relative_path)
        ensure_secure_dir(store_dir)

        store_path = store_dir / local_path.name
        shutil.copy2(local_path, store_path)
        ensure_secure_file(store_path)

        return store_path

    def copy_to_project(
        self,
        store_path: Path,
        git_root: Path,
        relative_path: str = ".",
    ) -> Path:
        """Copy env file from store to project.

        Args:
            store_path: Source file path in store.
            git_root: Git repository root.
            relative_path: Path relative to git root.

        Returns:
            Path to the local file.
        """
        local_dir = git_root
        if relative_path and relative_path != ".":
            local_dir = git_root / relative_path
            local_dir.mkdir(parents=True, exist_ok=True)

        local_path = local_dir / store_path.name
        shutil.copy2(store_path, local_path)
        ensure_secure_file(local_path)

        return local_path

    def delete_local(self, local_path: Path) -> bool:
        """Delete local env file.

        Args:
            local_path: Path to local file.

        Returns:
            True if deleted, False if didn't exist.
        """
        if local_path.exists():
            local_path.unlink()
            return True
        return False


# Global instance
env_file_manager = EnvFileManager()
