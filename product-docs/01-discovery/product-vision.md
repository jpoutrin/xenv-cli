# Product Vision: xenv

## Mission Statement

> "xenv exists to help you never lose a .env.local ever."

---

## Vision

Help developers manage, backup, and securely share .env files - starting with a rock-solid personal workflow, then expanding to team collaboration.

---

## Product Positioning

### What xenv IS:
- A CLI tool for managing .env files across projects
- Git-aware (knows which project you're in by origin)
- Worktree-native (seamlessly shares env files across worktrees)
- Direnv-integrated (zero-friction via .envrc)
- Local-first (your secrets never leave your machine)
- Backup-ready (Plakar integration for encrypted backup)

### What xenv is NOT:
- A secrets management platform (no vault, no rotation)
- A cloud service (no accounts, no subscriptions)
- A team collaboration tool (not in MVP)
- A replacement for proper secrets management in production

---

## Differentiation Statement

> "Unlike dotenv-vault or envio, xenv is **git-aware and worktree-native** - it automatically knows which project you're in and seamlessly shares env files across worktrees without manual copying."

---

## Value Proposition

### For Individual Developers:
- **Never lose .env files** - Centralized storage survives folder deletion
- **Zero worktree friction** - Env files automatically available in all worktrees
- **Machine portability** - Backup and restore across machines with Plakar
- **Just works** - One line in .envrc, everything handled

### Before xenv:
```
Clone project → Ask colleague for .env → Create manually
Create worktree → cp ../.env.local . → Forget sometimes
Nuke folder → Panic → Recreate from memory/Slack
Switch machines → S3/Slack/NCP chaos
```

### After xenv:
```
Clone project → .envrc runs xenv init → Done
Create worktree → .envrc runs xenv init → Done
Nuke folder → Re-clone → .envrc restores → Done
Switch machines → plakar restore → xenv init → Done
```

---

## Product Principles

1. **Local-first** - No cloud dependency, no accounts, no subscriptions
2. **Git-native** - Understands your project by its origin
3. **Zero-friction** - Works automatically via direnv
4. **Secure by default** - Strict file permissions, no secrets in output
5. **Idempotent** - Run `xenv init` 100 times, same result
6. **Transparent** - Show what's happening, no magic

---

## Roadmap Vision

### Phase 1: Personal (MVP)
- `init`, `save`, `list`, `delete`, `backup`
- Git origin detection
- Worktree support
- Monorepo support
- Direnv integration
- Plakar backup

### Phase 2: Polish
- Better drift detection and merge support
- Template support (.env.example → .env.local)
- Shell completions (bash, zsh, fish)
- Better error messages and recovery

### Phase 3: Team (Future)
- Encrypted sharing with expiring links
- Team key management
- Import from shared links
- Audit log

---

## Success Criteria

The product is successful when:
1. You (and colleagues) use it daily without thinking
2. Zero .env files lost in 6 months
3. New team members onboard faster
4. Community adopts and contributes

---

## Brand Voice

- **Practical** - Solves real problems, no hype
- **Developer-friendly** - CLI-native, Unix philosophy
- **Trustworthy** - Open source, transparent, secure
- **Humble** - Does one thing well
