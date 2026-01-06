# Discovery Session: xenv

**Date:** 2026-01-06
**Facilitator:** CPO Persona
**Product:** xenv (PyPI: xenv-cli)
**Mission:** "xenv exists to help you never lose a .env.local ever."

---

## Section 1: Product Foundation

### Q1: Product Name & Category

**Product:** xenv-cli (command: `xenv`)
**Category:** Developer Tools / Local Development Infrastructure

**Description:** CLI tool for centralized .env.local management, git-aware, worktree-native, with direnv integration.

**Assessment:**
- Name is short, memorable, extensible
- Category is well-understood by target audience
- Market of developers using .env files is large (30M+)

---

### Q2: Big Idea & Vision

**Vision:** Help developers manage, backup, and (in future) securely share .env files.

**MVP Focus:** Personal env management + backup
**Future:** Encrypted sharing with expiring links

**Assessment:**
- Local-first approach is underserved in the market
- Git-aware + worktree-native is unique combination
- Natural expansion path: Personal → Backup → Team

---

### Q3: Problem Statement

**Problem:** Developers lose .env files when cleaning up project folders and must manually copy them across git worktrees, wasting time and risking lost configuration.

**Pain Points:**
- Deleting folder = risk of losing .env.local
- New worktree = manual copy of .env files
- Machine migration = chaotic (Slack, S3, NCP, manual copy)
- No single source of truth for env files

**Assessment:**
- Severity: PAINKILLER (not vitamin)
- No dominant solution exists
- Solution uses proven, boring technology

---

### Q4: Solution Overview

**Solution Flow:**

| Scenario | What Happens |
|----------|--------------|
| Clone new repo (with .envrc) | Auto-creates/restores .env files |
| Clone new repo (no .envrc) | Run `xenv init` manually |
| Enter worktree | .envrc triggers auto-detection |
| Nuke & reclone | .envrc restores from CONF_HOME |
| Switch machines | Plakar restore → everything back |

**Key Innovation:**
- Git-origin-aware storage
- Worktree-native support
- .envrc integration for zero-friction setup
- Copy with drift detection (not symlinks)

---

### Q5: Mission Statement

> "xenv exists to help you never lose a .env.local ever."

**Assessment:**
- Simple, memorable, true
- Promise-oriented, not feature-oriented
- All MVP features support this mission

---

## Section 2: Market & User Context

### Q6: Target Market

| Layer | Description | Size |
|-------|-------------|------|
| TAM | All developers using .env files | 30M+ |
| SAM | Git users with local .env workflows | 10M+ |
| SOM | Direnv/worktree power users | 100K+ |
| **First 10** | Colleagues | ~10 |

**Go-to-Market:** Start with colleagues, validate, then expand via PyPI + GitHub.

---

### Q7: Primary Users

**Primary Persona: "Marc" - Senior Software Engineer**

- Works at a French tech company (50-200 employees)
- Maintains multiple Python microservices and TypeScript frontends
- Juggles 6 active repos, uses worktrees for feature branches
- Has lost .env.local twice this year
- Currently uses manual copying and private gists

---

### Q8: User Journey (Current State)

| Scenario | Current Solution | Pain Level |
|----------|------------------|------------|
| Clone new project | Create from scratch OR ask colleague | HIGH |
| Create worktree | Manually `cp ../.env.local .` | MEDIUM |
| Nuke folder | Hope you remembered to backup | CRITICAL |
| Switch machines | NCP / Slack / S3 / manual | HIGH |

---

### Q9: Competitive Landscape

| Tool | Approach | Gap |
|------|----------|-----|
| dotenv-vault | Cloud-synced .env | Cloud-dependent |
| envio | Encrypted local profiles | No git-awareness |
| Envault | Self-hosted web server | Heavy infrastructure |
| EnvKey | Full secrets platform | Overkill for local dev |
| git-local-backup | Backup untracked files | Not .env-specific |

**Gap:** No tool is git-aware + worktree-native + direnv-integrated + local-first.

---

### Q10: Differentiation

> "Unlike dotenv-vault or envio, xenv is **git-aware and worktree-native** - it automatically knows which project you're in and seamlessly shares env files across worktrees without manual copying."

---

## Section 3: Product Scope & Strategy

### Q11: Core Features (MVP)

| Command | Description | Priority |
|---------|-------------|----------|
| `init` | Create/restore env files, idempotent for .envrc | P0 |
| `save` | Persist local changes back to CONF_HOME | P0 |
| `list` | Show current project's env files | P0 |
| `list --all` | Show all projects, grouped by origin | P0 |
| `delete` | Remove env file (keeps backup) | P1 |
| `backup` | Trigger Plakar backup | P1 |

**Supporting Features:**
- Git origin detection
- Worktree support
- Multi-env (.env.local, .env.development, .env.test)
- Drift detection
- Monorepo support (path-aware storage)

---

### Q12: Success Metrics

| Metric | Type | Target (3 months) |
|--------|------|-------------------|
| PyPI downloads | Awareness | 500+ |
| Weekly active downloads | Retention | 50+ |
| GitHub stars | Social proof | 100+ |
| Colleagues using daily | Activation | 5+ |
| .env files lost | Mission | 0 |

**North Star:** Weekly PyPI downloads

---

### Q13: Business Model

**Model:** Free & Open Source + GitHub Sponsors

- MIT License
- Donations via GitHub Sponsors
- No paid tiers, no feature gating

---

### Q14: Platform Strategy

| Aspect | Decision |
|--------|----------|
| macOS | Primary |
| Linux | Primary |
| Windows | WSL recommended |
| Python | 3.10+ |
| Dependencies | Full-featured (typer, rich, tomli) |

---

### Q15: Timeline

**Timeline:** When it's ready. No artificial deadlines.

---

## Section 4: Technical & Resource Context

### Q16: Technical Constraints

| Constraint | Decision |
|------------|----------|
| Monorepo support | Store path relative to git root |
| Paths | Relative to $HOME |
| `list` default | Current project only |
| `list --all` | Grouped by origin |

---

### Q17: Team & Resources

**Team:** Solo developer

---

### Q18: Integration Needs

| Integration | Priority |
|-------------|----------|
| Git | P0 - Core |
| direnv (.envrc) | P0 - Core |
| Plakar | P1 - MVP |
| bash/zsh | P0 - Core |

---

### Q19: Scalability Requirements

No concerns. Personal/small team scale.

---

### Q20: Compliance & Security

| Requirement | Implementation |
|-------------|----------------|
| CONF_HOME directory | 700 (rwx------) |
| Env files | 600 (rw-------) |
| Config files | 600 (rw-------) |
| Secrets in output | Never displayed |
| Permission drift | Warn user |

---

## Summary

**xenv** is a local-first CLI tool for developers to manage .env files across projects and machines. It's git-aware, worktree-native, and integrates with direnv for zero-friction setup. The mission is simple: never lose a .env.local ever.
