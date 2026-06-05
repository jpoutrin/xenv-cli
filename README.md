# xenv

> Never lose a .env.local ever.

A CLI tool for centralized `.env.local` file management with git-aware, worktree-native, and direnv-integrated local environment variable file management.

## Features

- **Centralized storage**: All env files stored in `~/.config/xenv/`
- **Git-aware**: Automatically detects repository origin
- **Worktree support**: Same env files across all worktrees
- **Auto-sync**: Shell hook automatically saves/restores env files
- **Secure**: Files stored with 600 permissions
- **Backup ready**: Plakar integration for encrypted backups

## Installation

### With uv (recommended)

```bash
# Install globally as a CLI tool
uv tool install .

# Or install in development mode
uv pip install -e .
```

### With pip

```bash
pip install -e .
```

### Verify installation

```bash
xenv --version
```

## Quick Start

```bash
# 1. Initialize in your project (saves existing .env files)
cd your-project
xenv init

# 2. Add shell hook for automatic sync (add to ~/.zshrc or ~/.bashrc)
eval "$(xenv hook zsh)"

# That's it! Your env files are now automatically synced.
```

## Commands

| Command | Description |
|---------|-------------|
| `xenv init` | Create or restore env files for the current project |
| `xenv save` | Persist local changes to the store |
| `xenv list` | Show env files for current project or all projects |
| `xenv status` | Show sync status without making changes |
| `xenv sync` | Combined init + save (used by shell hook) |
| `xenv delete` | Remove env file from project (keeps backup) |
| `xenv hook` | Output shell integration code |
| `xenv backup` | Trigger Plakar backup of the store |

## Usage Examples

### Initialize a project

```bash
$ xenv init
📁 my-app (github.com/user/my-app)

✓ Restored .env.local
✓ Restored .env.development
```

### Check status

```bash
$ xenv status
.env.local                     ✓ synced
.env.development               ↑ local changes (will save)
.env.test                      ↓ missing locally (will restore)
```

### List all projects

```bash
$ xenv list --all
📁 github.com/user/my-app
  .env.local                     ✓ stored

📁 github.com/company/monorepo
  .env.local                     ✓ stored
  apps/frontend/.env.local       ✓ stored
```

### Shell hook (automatic sync)

```bash
# Add to ~/.zshrc
eval "$(xenv hook zsh)"

# Add to ~/.bashrc
eval "$(xenv hook bash)"

# Add to ~/.config/fish/config.fish
xenv hook fish | source
```

With the shell hook enabled, xenv automatically:
- **Restores** missing .env files when you `cd` into a project
- **Saves** modified .env files when you make changes

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                     Your Workflow                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Clone Repo  →  cd into project  →  .env.local restored!  │
│                                                             │
│   Edit .env   →  next command     →  .env.local saved!     │
│                                                             │
│   Delete repo →  re-clone         →  .env.local restored!  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Storage Structure

```
~/.config/xenv/
├── config.toml           # Global settings
├── projects.toml         # Project registry
└── origins/
    └── github.com-user-repo/
        ├── .env.local
        └── apps/frontend/
            └── .env.local
```

## Configuration

Default env file patterns tracked:
- `.env.local`
- `.env.development`
- `.env.development.local`
- `.env.test`
- `.env.test.local`

## direnv Integration

Add to your project's `.envrc`:

```bash
if command -v xenv &> /dev/null; then
    eval "$(xenv init --quiet)"
fi

dotenv .env.local
```

## License

MIT
