# MVP Scope: xenv

## Product Identity

| Attribute | Value |
|-----------|-------|
| **Product Name** | xenv |
| **PyPI Package** | `xenv-cli` |
| **CLI Command** | `xenv` |
| **Mission** | "Never lose a .env.local ever" |
| **License** | MIT |
| **Monetization** | Free + GitHub Sponsors |

---

## MVP Commands

### Core Commands (P0)

| Command | Description | Example |
|---------|-------------|---------|
| `xenv init` | Create/restore env files for current project | `xenv init` |
| `xenv save` | Persist local changes back to CONF_HOME | `xenv save` |
| `xenv list` | List env files for current project | `xenv list` |
| `xenv list --all` | List all env files, grouped by origin | `xenv list --all` |

### Important Commands (P1)

| Command | Description | Example |
|---------|-------------|---------|
| `xenv delete` | Remove env file from project (keeps backup) | `xenv delete .env.local` |
| `xenv backup` | Trigger Plakar backup of CONF_HOME | `xenv backup` |

### Future Commands (Post-MVP)

| Command | Description |
|---------|-------------|
| `xenv share` | Generate encrypted sharing link |
| `xenv import` | Import from shared link |

---

## Storage Architecture

### Directory Structure

```
~/.config/xenv/                          # CONF_HOME (700 permissions)
├── config.toml                          # Global settings (600)
├── projects.toml                        # Project mappings (600)
└── origins/
    └── github-com-jpoutrin-my-app/      # Slugified origin
        ├── .env.local                   # Root level (600)
        ├── .env.development             # Root level (600)
        └── apps/
            ├── frontend/.env.local      # Monorepo subfolder
            └── backend/.env.local       # Monorepo subfolder
```

### Config Files

**config.toml:**
```toml
[settings]
conf_home = ".config/xenv"  # Relative to $HOME

[backup]
tool = "plakar"
# Additional Plakar settings
```

**projects.toml:**
```toml
[[projects]]
origin = "git@github.com:jpoutrin/my-app.git"
paths = [
    "projects/github/jpoutrin/my-app",
    "projects/github/jpoutrin/my-app-feature"  # Worktree
]

[[projects]]
origin = "git@github.com:company/monorepo.git"
paths = [
    "work/monorepo"
]
```

---

## Technical Specifications

### Platform Support

| Platform | Support Level |
|----------|---------------|
| macOS | Primary |
| Linux | Primary |
| Windows | WSL recommended |

### Python Requirements

| Requirement | Value |
|-------------|-------|
| Python version | 3.10+ |
| Dependency style | Full-featured |

### Dependencies

```toml
[project]
dependencies = [
    "typer>=0.9.0",
    "rich>=13.0.0",
    "tomli>=2.0.0;python_version<'3.11'",
    "tomli-w>=1.0.0",
]

[project.scripts]
xenv = "xenv_cli.main:app"
```

---

## Security Requirements

| Requirement | Implementation |
|-------------|----------------|
| CONF_HOME directory | `700` (rwx------) |
| All env files | `600` (rw-------) |
| All config files | `600` (rw-------) |
| Secrets in output | Never displayed |
| Permission drift | Warn user |

### Security Checks

```python
# On every file access
def ensure_secure_permissions(path):
    mode = os.stat(path).st_mode
    if mode & (stat.S_IRWXG | stat.S_IRWXO):
        warn(f"Insecure permissions on {path}")
```

---

## Key Behaviors

### `xenv init`

1. Detect git root (`git rev-parse --show-toplevel`)
2. Get origin (`git remote get-url origin`)
3. Get relative path from $HOME
4. Check if env files exist in CONF_HOME for this origin
5. If exists: Copy to project, report "Restored from backup"
6. If not exists: Create empty, register in projects.toml
7. Set permissions to 600
8. **Idempotent:** Safe to run multiple times

### `xenv save`

1. Detect git root and origin
2. Compare local .env files with CONF_HOME versions
3. If different: Copy local → CONF_HOME, report changes
4. If same: Report "Already up to date"
5. Update projects.toml if needed

### `xenv list`

**Default (current project):**
```
📁 my-app (github.com/jpoutrin/my-app)

  .env.local              ✓ synced
  .env.development        ⚠ local changes
  .env.test               ✗ missing locally
```

**With `--all`:**
```
📁 github.com/jpoutrin/my-app
  .env.local              ✓ synced

📁 github.com/company/monorepo
  .env.local              ✓ synced
  apps/frontend/.env.local    ⚠ local changes
```

### `xenv delete`

1. Remove .env file from current project directory
2. Keep backup in CONF_HOME
3. Report: "Removed .env.local (backup preserved in ~/.config/xenv/...)"

### `xenv backup`

1. Run `plakar push ~/.config/xenv`
2. Report success/failure

---

## .envrc Integration

**Recommended .envrc snippet:**
```bash
# Load xenv for this project
eval "$(xenv init --quiet)"
```

**Behavior:**
- `--quiet` suppresses output unless there's an action/warning
- Idempotent: Safe to run on every `cd`
- Returns non-zero only on errors (doesn't break shell)

---

## Monorepo Support

**Detection:**
1. Find git root
2. Get current directory relative to git root
3. Use `origin + relative_path` as unique key

**Example:**
```
~/work/monorepo/                    # git root
~/work/monorepo/apps/frontend/      # cd here

xenv init  # Manages apps/frontend/.env.local
```

---

## Worktree Support

**Detection:**
1. Get origin (same for main and worktrees)
2. Get absolute path relative to $HOME
3. Register path in projects.toml

**Behavior:**
- All worktrees share same CONF_HOME env files
- Each worktree path tracked in projects.toml
- `xenv init` in any worktree restores from same source

---

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Origin changes (fork → upstream) | Detect new origin, offer to migrate |
| No git repo | Error: "Not a git repository" |
| No origin set | Error: "No remote origin configured" |
| .env exists but not tracked | Offer to `xenv save` first |
| Permission denied | Clear error with fix suggestion |
| Plakar not installed | Warn, skip backup command |

---

## Success Metrics

| Metric | Target (3 months) |
|--------|-------------------|
| PyPI downloads | 500+ |
| Weekly active downloads | 50+ |
| GitHub stars | 100+ |
| Colleagues using daily | 5+ |
| .env files lost | 0 |

---

## Out of Scope (Post-MVP)

- Encrypted sharing with expiring links
- Team collaboration features
- Web UI
- VS Code extension
- CI/CD integration
- Secret rotation
- .env.example template generation

---

## Definition of Done

MVP is complete when:
1. All P0 commands work reliably
2. P1 commands (`delete`, `backup`) work
3. Published on PyPI as `xenv-cli`
4. README with installation and usage
5. 5 colleagues using it daily
6. Zero .env files lost in 1 month of use
