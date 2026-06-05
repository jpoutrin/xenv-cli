"""Tests for EnvFile service."""

import time
from pathlib import Path

import pytest

from xenv_cli.models.env_file import SyncStatus
from xenv_cli.services.env_file import EnvFileManager


class TestCompareFiles:
    """Tests for file comparison logic."""

    def test_both_missing_is_synced(self, temp_dir):
        """Two non-existent files are considered synced."""
        manager = EnvFileManager()
        local = temp_dir / "local" / ".env.local"
        store = temp_dir / "store" / ".env.local"

        status = manager.compare_files(local, store)
        assert status == SyncStatus.SYNCED

    def test_local_only_is_missing_store(self, temp_dir):
        """Local exists, store doesn't = MISSING_STORE."""
        manager = EnvFileManager()
        local = temp_dir / ".env.local"
        local.write_text("KEY=value")
        store = temp_dir / "store" / ".env.local"

        status = manager.compare_files(local, store)
        assert status == SyncStatus.MISSING_STORE

    def test_store_only_is_missing_local(self, temp_dir):
        """Store exists, local doesn't = MISSING_LOCAL."""
        manager = EnvFileManager()
        local = temp_dir / ".env.local"
        store_dir = temp_dir / "store"
        store_dir.mkdir()
        store = store_dir / ".env.local"
        store.write_text("KEY=value")

        status = manager.compare_files(local, store)
        assert status == SyncStatus.MISSING_LOCAL

    def test_identical_files_are_synced(self, temp_dir):
        """Identical files are synced."""
        manager = EnvFileManager()
        local = temp_dir / "local.env"
        store = temp_dir / "store.env"
        content = "KEY=value\nOTHER=123"
        local.write_text(content)
        store.write_text(content)

        status = manager.compare_files(local, store)
        assert status == SyncStatus.SYNCED

    def test_local_newer_detected(self, temp_dir):
        """Local file newer than store = LOCAL_NEWER."""
        manager = EnvFileManager()
        store = temp_dir / "store.env"
        store.write_text("OLD=content")

        # Wait a bit to ensure different mtime
        time.sleep(0.1)

        local = temp_dir / "local.env"
        local.write_text("NEW=content")

        status = manager.compare_files(local, store)
        assert status == SyncStatus.LOCAL_NEWER

    def test_store_newer_detected(self, temp_dir):
        """Store file newer than local = STORE_NEWER."""
        manager = EnvFileManager()
        local = temp_dir / "local.env"
        local.write_text("OLD=content")

        # Wait a bit to ensure different mtime
        time.sleep(0.1)

        store = temp_dir / "store.env"
        store.write_text("NEW=content")

        status = manager.compare_files(local, store)
        assert status == SyncStatus.STORE_NEWER


class TestCopyOperations:
    """Tests for file copy operations."""

    def test_copy_to_store(self, temp_dir, conf_home):
        """Files are correctly copied to store."""
        manager = EnvFileManager()

        # Create local file
        local_dir = temp_dir / "project"
        local_dir.mkdir()
        local_file = local_dir / ".env.local"
        local_file.write_text("SECRET=value123")

        # Copy to store
        store_path = manager.copy_to_store(local_file, "test-origin", ".")

        assert store_path.exists()
        assert store_path.read_text() == "SECRET=value123"
        # Check permissions (should be 600)
        assert (store_path.stat().st_mode & 0o777) == 0o600

    def test_copy_to_project(self, temp_dir, conf_home):
        """Files are correctly copied to project."""
        manager = EnvFileManager()

        # Create store file
        store_dir = conf_home / "origins" / "test-origin"
        store_dir.mkdir(parents=True)
        store_file = store_dir / ".env.local"
        store_file.write_text("SECRET=restored")

        # Create project dir
        project_dir = temp_dir / "project"
        project_dir.mkdir()

        # Copy to project
        local_path = manager.copy_to_project(store_file, project_dir, ".")

        assert local_path.exists()
        assert local_path.read_text() == "SECRET=restored"


class TestEnvFilesStatus:
    """Tests for getting env files status."""

    def test_finds_local_env_files(self, git_repo, conf_home):
        """Finds .env.local files in project."""
        manager = EnvFileManager()

        # Create env file
        env_file = git_repo / ".env.local"
        env_file.write_text("KEY=value")

        # Get origin info
        origin = "git@github.com:test/repo.git"
        origin_slug = "github.com-test-repo"

        env_files = manager.get_env_files_status(
            git_repo, origin_slug, ".", [".env.local"]
        )

        assert len(env_files) == 1
        assert env_files[0].name == ".env.local"
        assert env_files[0].status == SyncStatus.MISSING_STORE
