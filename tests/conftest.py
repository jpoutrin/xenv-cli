"""Pytest fixtures for xenv tests."""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def git_repo(temp_dir: Path) -> Path:
    """Create a temporary git repository with a remote origin."""
    repo_dir = temp_dir / "repo"
    repo_dir.mkdir()

    # Initialize git repo
    subprocess.run(["git", "init"], cwd=repo_dir, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=repo_dir,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_dir,
        capture_output=True,
    )

    # Add remote origin
    subprocess.run(
        ["git", "remote", "add", "origin", "git@github.com:test/repo.git"],
        cwd=repo_dir,
        capture_output=True,
    )

    return repo_dir


@pytest.fixture
def conf_home(temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a temporary xenv config home."""
    config_dir = temp_dir / "config" / "xenv"
    config_dir.mkdir(parents=True)

    # Set XDG_CONFIG_HOME to use our temp dir
    monkeypatch.setenv("XDG_CONFIG_HOME", str(temp_dir / "config"))

    return config_dir
