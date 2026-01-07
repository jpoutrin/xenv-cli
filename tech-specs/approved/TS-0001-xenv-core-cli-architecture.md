# TS-0001: xenv Core CLI Architecture

## Metadata

| Field | Value |
|-------|-------|
| **Tech Spec ID** | TS-0001 |
| **Title** | xenv Core CLI Architecture |
| **Status** | APPROVED |
| **Author** | |
| **Created** | 2026-01-06 |
| **Last Updated** | 2026-01-07 |
| **Decision Ref** | - |
| **PRD Ref** | product-docs/01-discovery/mvp-scope.md |

---

## Executive Summary

This technical specification defines the architecture for xenv, a CLI tool for centralized .env.local file management. xenv provides git-aware, worktree-native, and direnv-integrated local environment variable file management with the mission: "Never lose a .env.local ever."

The system consists of:
- A Python CLI application using Typer and Rich
- A local configuration store at `~/.config/xenv/`
- Git integration for origin detection and worktree support
- Plakar integration for encrypted backup

---

## Design Overview

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              User Workflow                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐             │
│   │  Clone   │───▶│  .envrc  │───▶│xenv init │───▶│  Work!   │             │
│   │  Repo    │    │ triggers │    │ restores │    │          │             │
│   └──────────┘    └──────────┘    └──────────┘    └──────────┘             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           CLI Layer (xenv)                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│   │   init   │  │   save   │  │   list   │  │  delete  │  │  backup  │    │
│   │          │  │          │  │          │  │          │  │          │    │
│   └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
│        │             │             │             │             │           │
│        └─────────────┴─────────────┴─────────────┴─────────────┘           │
│                                    │                                        │
└────────────────────────────────────┼────────────────────────────────────────┘
                                     │
┌────────────────────────────────────┼────────────────────────────────────────┐
│                        Core Services Layer                                  │
├────────────────────────────────────┼────────────────────────────────────────┤
│                                    │                                        │
│   ┌────────────────┐  ┌────────────┴───────────┐  ┌────────────────┐       │
│   │  Git Service   │  │  Env File Manager      │  │ Config Manager │       │
│   │                │  │                        │  │                │       │
│   │ - get_origin() │  │ - copy_to_project()    │  │ - load()       │       │
│   │ - get_root()   │  │ - copy_to_store()      │  │ - save()       │       │
│   │ - is_worktree()│  │ - detect_drift()       │  │ - get_origin() │       │
│   │ - get_rel_path │  │ - set_permissions()    │  │                │       │
│   └────────┬───────┘  └────────────┬───────────┘  └────────┬───────┘       │
│            │                       │                       │                │
└────────────┼───────────────────────┼───────────────────────┼────────────────┘
             │                       │                       │
┌────────────┼───────────────────────┼───────────────────────┼────────────────┐
│            ▼                       ▼                       ▼                │
│                           Storage Layer                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ~/.config/xenv/                                                          │
│   ├── config.toml                 # Global settings                        │
│   ├── projects.toml               # Project registry                       │
│   └── origins/                                                             │
│       └── github-com-user-repo/   # Slugified origin                       │
│           ├── .env.local          # Stored env files                       │
│           └── apps/frontend/      # Monorepo paths                         │
│               └── .env.local                                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                        External Integrations                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────┐       ┌──────────┐       ┌──────────┐                       │
│   │   Git    │       │  direnv  │       │  Plakar  │                       │
│   │          │       │          │       │          │                       │
│   │ - origin │       │ - .envrc │       │ - backup │                       │
│   │ - root   │       │ - hooks  │       │ - restore│                       │
│   │ - workt. │       │          │       │          │                       │
│   └──────────┘       └──────────┘       └──────────┘                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Component Overview

| Component | Purpose | Technology |
|-----------|---------|------------|
| CLI Layer | User-facing commands | Typer + Rich |
| Git Service | Repository detection | subprocess + git |
| Env File Manager | File operations | pathlib + shutil |
| Config Manager | Settings persistence | TOML |
| Storage Layer | Centralized store | Filesystem |

---

## Detailed Design

### 1. Project Structure

```
xenv-cli/
├── pyproject.toml
├── README.md
├── src/
│   └── xenv_cli/
│       ├── __init__.py
│       ├── main.py              # CLI entry point
│       ├── commands/
│       │   ├── __init__.py
│       │   ├── init.py          # xenv init
│       │   ├── save.py          # xenv save
│       │   ├── list.py          # xenv list
│       │   ├── delete.py        # xenv delete
│       │   ├── backup.py        # xenv backup
│       │   ├── hook.py          # xenv hook (shell integration)
│       │   ├── sync.py          # xenv sync (auto init + save)
│       │   └── status.py        # xenv status (fast change detection)
│       ├── services/
│       │   ├── __init__.py
│       │   ├── git.py           # Git operations
│       │   ├── env_file.py      # Env file operations
│       │   └── config.py        # Config management
│       ├── models/
│       │   ├── __init__.py
│       │   ├── project.py       # Project model
│       │   └── env_file.py      # EnvFile model
│       └── utils/
│           ├── __init__.py
│           ├── paths.py         # Path utilities
│           ├── permissions.py   # File permissions
│           └── console.py       # Rich console
└── tests/
    ├── conftest.py
    ├── test_commands/
    ├── test_services/
    └── test_integration/
```

### 2. Core Data Models

#### 2.1 Project Model

```python
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

@dataclass
class Project:
    """Represents a tracked git project."""
    origin: str                    # Git remote origin URL
    paths: List[Path]              # Registered local paths (worktrees)
    env_files: List[str]           # Tracked env file names

    @property
    def origin_slug(self) -> str:
        """Slugified origin for filesystem storage."""
        # git@github.com:user/repo.git -> github-com-user-repo
        ...
```

#### 2.2 EnvFile Model

```python
from dataclasses import dataclass
from pathlib import Path
from enum import Enum
from datetime import datetime

class SyncStatus(Enum):
    SYNCED = "synced"
    LOCAL_CHANGES = "local_changes"
    MISSING_LOCAL = "missing_local"
    MISSING_STORE = "missing_store"

@dataclass
class EnvFile:
    """Represents an environment file."""
    name: str                      # e.g., ".env.local"
    relative_path: str             # Path relative to git root (for monorepo)
    local_path: Optional[Path]     # Full path in project
    store_path: Optional[Path]     # Full path in CONF_HOME
    status: SyncStatus
    local_mtime: Optional[datetime]
    store_mtime: Optional[datetime]
```

### 3. Configuration Files

#### 3.1 config.toml

```toml
[settings]
# Path relative to $HOME
conf_home = ".config/xenv"

# Env file patterns to track (glob patterns)
env_patterns = [
    ".env.local",
    ".env.development",
    ".env.development.local",
    ".env.test",
    ".env.test.local"
]

[backup]
tool = "plakar"
auto_backup = false

[display]
# Output verbosity: quiet, normal, verbose
verbosity = "normal"
```

#### 3.2 projects.toml

```toml
# Project registry - maps git origins to local paths

[[projects]]
origin = "git@github.com:jpoutrin/my-app.git"
paths = [
    "projects/github/jpoutrin/my-app",
    "projects/github/jpoutrin/my-app-feature-x"
]
env_files = [".env.local", ".env.development"]

[[projects]]
origin = "git@github.com:company/monorepo.git"
paths = ["work/monorepo"]
env_files = [
    ".env.local",
    "apps/frontend/.env.local",
    "apps/backend/.env.local"
]
```

### 4. Command Specifications

#### 4.1 `xenv init`

**Purpose:** Create or restore env files for the current project.

**Algorithm:**
```
1. Verify we're in a git repository
2. Get git root path
3. Get remote origin URL
4. Calculate relative path from git root (for monorepo support)
5. Generate origin slug
6. Check CONF_HOME/origins/{slug}/{relative_path}/ for stored env files
7. For each env file matching patterns:
   a. If exists in store and not in project → copy to project (restore)
   b. If exists in project and not in store → copy to store (initial save)
   c. If exists in both → compare and report status
8. Set file permissions to 600
9. Update projects.toml with current path
10. Return status
```

**CLI Interface:**
```bash
xenv init [--quiet] [--force]

Options:
  --quiet   Suppress output unless there's an action or warning
  --force   Overwrite local files with stored versions
```

**Output Examples:**
```
# Normal restore
📁 my-app (github.com/jpoutrin/my-app)

  ✓ Restored .env.local
  ✓ Restored .env.development

# Already initialized
📁 my-app (github.com/jpoutrin/my-app)

  ✓ .env.local (synced)
  ✓ .env.development (synced)

# Quiet mode with no changes
(no output)

# Quiet mode with restore
Restored 2 env files for my-app
```

#### 4.2 `xenv save`

**Purpose:** Persist local changes back to CONF_HOME.

**Algorithm:**
```
1. Verify git repository and get origin
2. Find local env files matching patterns
3. For each local env file:
   a. Compare with stored version (if exists)
   b. If different or new → copy to store
   c. Update file mtime metadata
4. Update projects.toml
5. Report changes
```

**CLI Interface:**
```bash
xenv save [--all] [<filename>]

Arguments:
  <filename>    Specific env file to save (e.g., ".env.local")

Options:
  --all         Save all env files (default behavior)
```

**Output Example:**
```
📁 my-app (github.com/jpoutrin/my-app)

  ✓ Saved .env.local (12 lines changed)
  · .env.development (no changes)
```

#### 4.3 `xenv list`

**Purpose:** Show env files for current project or all projects.

**Algorithm:**
```
1. If --all flag:
   a. Read projects.toml
   b. Group by origin
   c. Show all env files with sync status
2. Else:
   a. Get current project from git
   b. Show env files with sync status
```

**CLI Interface:**
```bash
xenv list [--all] [--json]

Options:
  --all     List all tracked projects
  --json    Output as JSON
```

**Output Examples:**
```
# Current project
📁 my-app (github.com/jpoutrin/my-app)

  .env.local              ✓ synced
  .env.development        ⚠ local changes
  .env.test               ✗ missing locally

# All projects
📁 github.com/jpoutrin/my-app
  .env.local              ✓ synced

📁 github.com/company/monorepo
  .env.local              ✓ synced
  apps/frontend/.env.local    ⚠ local changes
```

#### 4.4 `xenv delete`

**Purpose:** Remove env file from project (keeps backup).

**Algorithm:**
```
1. Verify file exists in project
2. Verify backup exists in store (or create one)
3. Remove file from project directory
4. Report with backup location
```

**CLI Interface:**
```bash
xenv delete <filename> [--force]

Arguments:
  <filename>    Env file to delete (e.g., ".env.local")

Options:
  --force       Skip confirmation prompt
```

**Output Example:**
```
Removed .env.local from my-app
Backup preserved: ~/.config/xenv/origins/github-com-jpoutrin-my-app/.env.local
```

#### 4.5 `xenv backup`

**Purpose:** Trigger Plakar backup of CONF_HOME.

**Algorithm:**
```
1. Check Plakar is installed
2. Run `plakar push ~/.config/xenv`
3. Report success/failure
```

**CLI Interface:**
```bash
xenv backup [--verbose]

Options:
  --verbose     Show Plakar output
```

**Output Example:**
```
✓ Backup complete
  15 files, 4.2 KB
  Snapshot: abc123...
```

#### 4.6 `xenv hook`

**Purpose:** Output shell code for automatic init and save - the core automation.

**Algorithm:**
```
1. Detect shell type (bash, zsh, fish)
2. Output shell function that runs on each prompt:
   a. Skip if not in a git repo
   b. Auto-init: If local .env missing but exists in store → restore
   c. Auto-save: If local .env newer than store → save silently
3. Must complete in < 50ms to not slow down prompt
4. Uses directory-based caching to avoid repeated checks
```

**CLI Interface:**
```bash
xenv hook [<shell>]

Arguments:
  <shell>    Shell type: bash, zsh, fish (auto-detected if omitted)
```

**Output (zsh):**
```zsh
# xenv shell integration - add to ~/.zshrc:
# eval "$(xenv hook zsh)"

_xenv_hook() {
  # Skip if not in a git repo
  [[ -d .git ]] || git rev-parse --git-dir &>/dev/null 2>&1 || return 0

  # Cache key based on directory + env file mtimes
  local cache_dir="/tmp/xenv_cache_$UID"
  local cache_key=$(pwd | md5sum | cut -d' ' -f1)
  local cache_file="$cache_dir/$cache_key"
  local now=$(date +%s)

  mkdir -p "$cache_dir" 2>/dev/null

  # Check cache (valid for 2 seconds)
  if [[ -f "$cache_file" ]]; then
    local cache_time=$(stat -f %m "$cache_file" 2>/dev/null || stat -c %Y "$cache_file" 2>/dev/null)
    (( now - cache_time < 2 )) && return 0
  fi

  # Run sync (shows brief output on save/restore)
  xenv sync 2>/dev/null

  # Update cache
  touch "$cache_file"
}

precmd_functions+=(_xenv_hook)
```

**Output (bash):**
```bash
# xenv shell integration - add to ~/.bashrc:
# eval "$(xenv hook bash)"

_xenv_hook() {
  # Skip if not in a git repo
  [[ -d .git ]] || git rev-parse --git-dir &>/dev/null 2>&1 || return 0

  # Cache key based on directory
  local cache_dir="/tmp/xenv_cache_$UID"
  local cache_key=$(echo -n "$PWD" | md5sum | cut -d' ' -f1)
  local cache_file="$cache_dir/$cache_key"
  local now=$(date +%s)

  mkdir -p "$cache_dir" 2>/dev/null

  # Check cache (valid for 2 seconds)
  if [[ -f "$cache_file" ]]; then
    local cache_time=$(stat -c %Y "$cache_file" 2>/dev/null || stat -f %m "$cache_file" 2>/dev/null)
    (( now - cache_time < 2 )) && return 0
  fi

  # Run sync (shows brief output on save/restore)
  xenv sync 2>/dev/null

  # Update cache
  touch "$cache_file"
}

PROMPT_COMMAND="_xenv_hook${PROMPT_COMMAND:+;$PROMPT_COMMAND}"
```

#### 4.7 `xenv sync`

**Purpose:** Combined init + save in one command. The workhorse behind the hook.

**Algorithm:**
```
1. Get current project origin and path
2. For each env file pattern:
   a. If exists in store but not locally → copy to local (restore)
   b. If exists locally but not in store → copy to store (save)
   c. If both exist and local is newer → copy to store (save)
   d. If both exist and store is newer → do nothing (local wins by default)
   e. If both exist and identical → do nothing
3. Show brief output for any action (default)
4. Update projects.toml registry
```

**CLI Interface:**
```bash
xenv sync [--silent] [--verbose] [--dry-run]

Options:
  --silent     No output at all
  --verbose    Show detailed operations including "in sync" status
  --dry-run    Show what would happen without doing it
```

**Output Examples:**
```
# Default (brief - only shows actions)
xenv: saved .env.local
xenv: restored .env.development

# Multiple files
xenv: saved .env.local, restored .env.development

# Nothing to do
(no output)

# Verbose mode (shows everything)
.env.local: local is newer (2026-01-07 10:30) → saved
.env.development: missing locally → restored
.env.test: in sync ✓

# Silent mode
(no output ever)

# Dry-run
xenv: would save .env.local
xenv: would restore .env.development
```

**Output Format:**
- Prefix: `xenv:` (distinguishes from other shell output)
- Action words: `saved`, `restored` (past tense, confirms completion)
- Compact: multiple files on one line when possible
- No output when nothing changes (reduces noise)

**Conflict Resolution:**
- Local file always wins (never overwrite unsaved local changes)
- To force restore from store: `xenv init --force`

**Performance:**
- Target: < 50ms
- Compares mtime first, hash only if mtimes differ
- Single pass over all env files

#### 4.8 `xenv status`

**Purpose:** Show sync status without making changes.

**Algorithm:**
```
1. Get current project origin and path
2. For each tracked env file:
   a. Compare local vs store (mtime + hash)
   b. Categorize: synced, local-newer, store-newer, missing-local, missing-store
3. Return status
```

**CLI Interface:**
```bash
xenv status [--porcelain]

Options:
  --porcelain    Machine-readable output for scripts
```

**Output Examples:**
```
# Human-readable (default)
.env.local          ✓ synced
.env.development    ↑ local changes (will save)
.env.test           ↓ missing locally (will restore)

# Porcelain mode (for scripts)
= .env.local
M .env.development
R .env.test
```

**Status Codes (porcelain):**
| Code | Meaning |
|------|---------|
| `=` | Synced (identical) |
| `M` | Modified locally (will auto-save) |
| `R` | Missing locally (will auto-restore) |
| `A` | New local file (will auto-save) |
| `?` | Untracked (not in patterns) |

**Performance:**
- Target: < 30ms
- Uses mtime comparison first, hash only when needed

### 5. Git Service

```python
# services/git.py

import subprocess
from pathlib import Path
from typing import Optional, Tuple

class GitError(Exception):
    """Git operation failed."""
    pass

class GitService:
    """Git repository operations."""

    def get_root(self, path: Path = None) -> Path:
        """Get git repository root directory."""
        cmd = ["git", "rev-parse", "--show-toplevel"]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=path)
        if result.returncode != 0:
            raise GitError("Not a git repository")
        return Path(result.stdout.strip())

    def get_origin(self, path: Path = None) -> str:
        """Get remote origin URL."""
        cmd = ["git", "remote", "get-url", "origin"]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=path)
        if result.returncode != 0:
            raise GitError("No remote origin configured")
        return result.stdout.strip()

    def is_worktree(self, path: Path = None) -> bool:
        """Check if current directory is a git worktree."""
        cmd = ["git", "rev-parse", "--is-inside-work-tree"]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=path)
        # Additional check for worktree vs main repo
        ...

    def get_relative_path(self, path: Path = None) -> str:
        """Get path relative to git root (for monorepo support)."""
        root = self.get_root(path)
        current = Path.cwd() if path is None else path
        return str(current.relative_to(root))

    @staticmethod
    def slugify_origin(origin: str) -> str:
        """Convert origin URL to filesystem-safe slug.

        Examples:
            git@github.com:user/repo.git -> github-com-user-repo
            https://github.com/user/repo.git -> github-com-user-repo
        """
        # Remove protocol
        slug = origin.replace("git@", "").replace("https://", "").replace("http://", "")
        # Remove .git suffix
        slug = slug.removesuffix(".git")
        # Replace separators with dashes
        slug = slug.replace(":", "-").replace("/", "-")
        # Clean up multiple dashes
        while "--" in slug:
            slug = slug.replace("--", "-")
        return slug.strip("-")
```

### 6. Permissions Management

```python
# utils/permissions.py

import os
import stat
from pathlib import Path
from typing import Optional

# Secure permission modes
DIR_MODE = 0o700   # rwx------
FILE_MODE = 0o600  # rw-------

class PermissionError(Exception):
    """File permission issue."""
    pass

def ensure_secure_dir(path: Path) -> None:
    """Create directory with secure permissions."""
    path.mkdir(parents=True, exist_ok=True)
    os.chmod(path, DIR_MODE)

def ensure_secure_file(path: Path) -> None:
    """Set secure permissions on file."""
    os.chmod(path, FILE_MODE)

def check_permissions(path: Path) -> Optional[str]:
    """Check if file/dir has secure permissions.

    Returns:
        None if secure, warning message if insecure
    """
    mode = os.stat(path).st_mode
    if path.is_dir():
        if mode & (stat.S_IRWXG | stat.S_IRWXO):
            return f"Insecure permissions on directory: {path} (should be 700)"
    else:
        if mode & (stat.S_IRWXG | stat.S_IRWXO):
            return f"Insecure permissions on file: {path} (should be 600)"
    return None

def warn_if_insecure(path: Path, console) -> None:
    """Print warning if permissions are insecure."""
    warning = check_permissions(path)
    if warning:
        console.print(f"[yellow]⚠ {warning}[/yellow]")
```

### 7. direnv Integration

**Recommended .envrc:**
```bash
# .envrc - xenv integration
# Add this single line to your project's .envrc

eval "$(xenv init --quiet)"
```

**Behavior:**
- `--quiet` suppresses all output unless there's a restore action or warning
- Returns exit code 0 on success (doesn't break direnv flow)
- Idempotent - safe to run on every directory change

**Error Handling:**
- If xenv not installed: direnv will show error, user can install
- If not a git repo: silent exit (might be intentional)
- If no origin: silent exit with optional warning

### 8. Shell Prompt Integration (Zero-Friction Automation)

**Purpose:** Automatically sync .env files on every prompt - no manual commands needed.

**Setup (zsh - recommended):**
```bash
# Add to ~/.zshrc
eval "$(xenv hook zsh)"
```

**Setup (bash):**
```bash
# Add to ~/.bashrc
eval "$(xenv hook bash)"
```

**What It Does:**

The hook runs on every prompt and automatically:
- **Restores** missing .env files from the store
- **Saves** modified .env files to the store

Brief feedback when actions occur:
```
~/projects/app $ cd ../other-app
xenv: restored .env.local
~/projects/other-app $ vim .env.local
~/projects/other-app $ ls
xenv: saved .env.local
```

No output when nothing changes (most prompts).

**How It Works:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    Shell Hook Flow (Silent)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   User presses Enter                                            │
│         │                                                       │
│         ▼                                                       │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐      │
│   │  precmd /   │────▶│  In git     │────▶│ Cache valid?│      │
│   │PROMPT_CMD   │     │   repo?     │     │  (2 sec)    │      │
│   └─────────────┘     └──────┬──────┘     └──────┬──────┘      │
│                              │                   │              │
│                     No ──────┤          Yes ─────┼───── skip    │
│                              │                   │              │
│                              ▼                   ▼              │
│                         (skip)           ┌─────────────┐        │
│                                          │ xenv sync   │        │
│                                          │  --quiet    │        │
│                                          └──────┬──────┘        │
│                                                 │               │
│                           ┌─────────────────────┼─────────────┐ │
│                           │                     │             │ │
│                           ▼                     ▼             │ │
│                    ┌─────────────┐       ┌─────────────┐      │ │
│                    │  Auto-init  │       │  Auto-save  │      │ │
│                    │  (restore)  │       │  (backup)   │      │ │
│                    └─────────────┘       └─────────────┘      │ │
│                           │                     │             │ │
│                           └─────────────────────┘             │ │
│                                    │                          │ │
│                                    ▼                          │ │
│                             (silent, done)                    │ │
│                                                               │ │
└───────────────────────────────────────────────────────────────┴─┘
```

**User Workflow (Zero Effort):**

```
# 1. Clone a project (first time)
$ git clone git@github.com:company/app.git
$ cd app
# → Hook auto-restores .env.local from store (if you worked on it before)

# 2. Create a worktree
$ git worktree add ../app-feature
$ cd ../app-feature
# → Hook auto-restores .env.local (same origin = same env files)

# 3. Edit .env.local
$ vim .env.local  # make changes
$ ls              # just press enter
# → Hook auto-saves to store (silently)

# 4. Nuke and re-clone
$ rm -rf app
$ git clone git@github.com:company/app.git
$ cd app
# → Hook auto-restores .env.local (never lost!)
```

**Performance Optimizations:**

| Optimization | Description |
|--------------|-------------|
| 2-second cache | Skip sync if checked recently |
| Directory-based cache | Different cache per project directory |
| Early git check | Skip immediately if not in a git repo |
| mtime comparison | Only hash files when mtimes differ |
| Target: < 50ms | Imperceptible prompt delay |

**Manual Commands (Still Available):**

| Command | When to Use |
|---------|-------------|
| `xenv status` | See what would sync |
| `xenv sync --dry-run` | Preview without changes |
| `xenv init --force` | Force restore from store (overwrite local) |
| `xenv save` | Explicit save (hook does this automatically) |

**Configuration (optional):**

```toml
# ~/.config/xenv/config.toml

[hook]
# Enable/disable auto-sync (default: true)
enabled = true

# Cache TTL in seconds (default: 2)
cache_ttl = 2

# Output mode: "default", "silent", "verbose"
output = "default"

# Disable auto-save (only auto-restore)
auto_save = true

# Disable auto-restore (only auto-save)
auto_restore = true
```

**Output Modes:**

| Mode | Behavior |
|------|----------|
| `default` | Show `xenv: saved/restored` when actions occur |
| `silent` | Never show output (like `--silent` flag) |
| `verbose` | Show detailed info including "in sync" status |

---

## API Reference

### CLI Commands

| Command | Arguments | Options | Description |
|---------|-----------|---------|-------------|
| `init` | - | `--quiet`, `--force` | Create/restore env files |
| `save` | `[filename]` | `--all` | Persist changes to store |
| `list` | - | `--all`, `--json` | Show env files |
| `delete` | `<filename>` | `--force` | Remove env file |
| `backup` | - | `--verbose` | Trigger Plakar backup |
| `hook` | `[shell]` | - | Output shell integration code |
| `sync` | - | `--silent`, `--verbose`, `--dry-run` | Auto init + save (used by hook) |
| `status` | - | `--porcelain` | Show sync status |

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Not a git repository |
| 3 | No remote origin configured |
| 4 | File not found |
| 5 | Permission denied |

---

## Data Model

### Storage Paths

| Item | Path | Permissions |
|------|------|-------------|
| Config home | `~/.config/xenv/` | 700 |
| Global config | `~/.config/xenv/config.toml` | 600 |
| Project registry | `~/.config/xenv/projects.toml` | 600 |
| Origin storage | `~/.config/xenv/origins/{slug}/` | 700 |
| Env files | `~/.config/xenv/origins/{slug}/.env.*` | 600 |

### Origin Slug Examples

| Origin | Slug |
|--------|------|
| `git@github.com:user/repo.git` | `github-com-user-repo` |
| `https://github.com/user/repo.git` | `github-com-user-repo` |
| `git@gitlab.com:org/project.git` | `gitlab-com-org-project` |

---

## Error Handling

### Error Messages

| Scenario | Message | Exit Code |
|----------|---------|-----------|
| Not in git repo | "Error: Not a git repository. Run `git init` first." | 2 |
| No origin | "Error: No remote origin configured. Run `git remote add origin <url>`." | 3 |
| Env file not found | "Error: .env.local not found in project or store." | 4 |
| Permission denied | "Error: Permission denied. Check file permissions." | 5 |
| Plakar not installed | "Warning: Plakar not installed. Backup skipped." | 0 (warning only) |

### Recovery Suggestions

Each error includes actionable suggestions:
```
Error: Not a git repository.

This command must be run inside a git repository.
Run `git init` to initialize a new repository.
```

---

## Security Considerations

### File Permissions

1. **CONF_HOME directory**: 700 (rwx------)
2. **All env files**: 600 (rw-------)
3. **All config files**: 600 (rw-------)
4. **Permission drift detection**: Warn user if permissions change

### Secrets Protection

1. **Never display secrets** in output (only file names and status)
2. **Never log secrets** to any log files
3. **Never commit** CONF_HOME to git (add to global gitignore)

### File Content Safety

1. Copy files without parsing (preserve exact content)
2. Don't validate or transform env file content
3. Preserve line endings and encoding

---

## Performance Considerations

### Startup Time

Target: < 100ms for common operations

Optimizations:
1. Lazy-load config files
2. Minimal git subprocess calls
3. No network operations

### File Operations

1. Use pathlib for cross-platform compatibility
2. Atomic file writes (write to temp, then rename)
3. Batch file comparisons when possible

---

## Testing Strategy

### Unit Tests

- Git service mocking
- File operations with temp directories
- Config parsing edge cases
- Origin slug generation

### Integration Tests

- Full command workflows
- Git repository fixtures
- Worktree scenarios
- Monorepo scenarios

### Manual Test Cases

1. Clone repo with .envrc → auto-restore works
2. Create worktree → env files available
3. Modify env → save persists changes
4. Delete folder → reclone → restore works
5. New machine → plakar restore → xenv init

---

## Dependencies

### Runtime Dependencies

```toml
[project]
dependencies = [
    "typer>=0.9.0",        # CLI framework
    "rich>=13.0.0",        # Terminal formatting
    "tomli>=2.0.0;python_version<'3.11'",  # TOML reading
    "tomli-w>=1.0.0",      # TOML writing
]
```

### Development Dependencies

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "mypy>=1.0.0",
    "ruff>=0.1.0",
]
```

---

## Migration & Compatibility

### Version 1.0 Guarantees

1. Config file format will remain backward compatible
2. Storage structure will remain stable
3. CLI interface will follow semantic versioning

### Future Considerations

1. Config file versioning for migrations
2. Storage format upgrades with automatic migration
3. Deprecation warnings before breaking changes

---

## Appendix

### A. Full pyproject.toml

```toml
[project]
name = "xenv-cli"
version = "0.1.0"
description = "Never lose a .env.local ever"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.10"
keywords = ["env", "dotenv", "cli", "git", "worktree"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: MacOS",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development",
    "Topic :: System :: Systems Administration",
]

dependencies = [
    "typer>=0.9.0",
    "rich>=13.0.0",
    "tomli>=2.0.0;python_version<'3.11'",
    "tomli-w>=1.0.0",
]

[project.scripts]
xenv = "xenv_cli.main:app"

[project.urls]
Homepage = "https://github.com/jpoutrin/xenv-cli"
Repository = "https://github.com/jpoutrin/xenv-cli"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/xenv_cli"]

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.mypy]
python_version = "3.10"
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --cov=xenv_cli"
```

### B. Example .envrc

```bash
# .envrc for projects using xenv
#
# This file should be committed to the repository.
# It integrates with direnv to auto-restore .env files.

# Check if xenv is installed
if command -v xenv &> /dev/null; then
    eval "$(xenv init --quiet)"
else
    echo "xenv not installed. Run: pip install xenv-cli"
fi

# Load the env file for this project
dotenv .env.local
```

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | 2026-01-06 | Initial draft |
