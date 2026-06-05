# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

xenv is a CLI tool for centralized `.env.local` file management. It stores env files in `~/.config/xenv/` indexed by git remote origin, enabling automatic sync across git worktrees and re-clones.

## Development Commands

```bash
# Install dependencies and package in dev mode
uv pip install -e ".[dev]"

# Run all tests with coverage
pytest

# Run a single test file
pytest tests/test_services/test_git.py

# Run a specific test
pytest tests/test_services/test_git.py::test_function_name -v

# Type checking
mypy src/xenv_cli

# Linting
ruff check src/xenv_cli

# Run the CLI
xenv --help
```

## Architecture

### Layer Structure

```
src/xenv_cli/
├── main.py           # Typer app entry point, command registration
├── commands/         # CLI command handlers (thin layer calling services)
├── services/         # Business logic
│   ├── git.py        # Git operations (get origin, detect worktrees)
│   ├── env_file.py   # File sync logic (compare, copy to/from store)
│   └── config.py     # TOML config management (settings, project registry)
├── models/           # Data classes
│   └── env_file.py   # EnvFile, SyncStatus enum
└── utils/            # Helpers (paths, permissions, console output)
```

### Key Concepts

- **Origin slug**: Git remote origin URLs are converted to filesystem-safe slugs for storage (e.g., `github.com-user-repo`)
- **Store path**: Env files stored at `~/.config/xenv/origins/{origin_slug}/{relative_path}/{filename}`
- **Sync status**: Files compared by content hash (SHA256), with mtime used to determine direction when different
- **Global instances**: Services expose singleton instances (`git_service`, `env_file_manager`, `config_manager`) for convenience

### Testing

Tests use pytest fixtures in `conftest.py`:
- `temp_dir`: Temporary directory
- `git_repo`: Temp git repo with mock origin
- `conf_home`: Temp `~/.config/xenv` with `XDG_CONFIG_HOME` override
