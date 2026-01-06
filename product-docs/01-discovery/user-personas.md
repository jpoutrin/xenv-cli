# User Personas: xenv

## Primary Persona

### Marc - Senior Software Engineer

![Persona Type: Primary User]

**Demographics:**
- Age: 28-35
- Location: France
- Role: Senior Software Engineer
- Company: Mid-size tech company (50-200 employees)

**Technical Profile:**
- Languages: Python, TypeScript
- Experience: 5-8 years
- OS: macOS or Linux
- Shell: zsh with oh-my-zsh
- Editor: VS Code or JetBrains IDE

**Work Context:**
- Maintains 5-8 active repositories
- Mix of Python microservices and TypeScript frontends
- Uses git worktrees for parallel feature development
- Works with monorepos (multiple .env files per repo)
- Remote/hybrid work setup

**Current .env Workflow:**
1. Clone repo → ask colleague for .env values or recreate from memory
2. Create worktree → manually `cp ../.env.local .`
3. Clean up folder → sometimes forgets to backup .env first
4. Switch machines → uses Slack DM to self or private gist

**Pain Points:**
- Lost .env.local twice this year when nuking broken git states
- Wastes 20+ minutes recreating env files from memory
- Forgets to copy .env to new worktrees, debugs for 10 minutes before realizing
- No reliable backup - uses ad-hoc methods
- Onboarding new colleagues takes time due to env setup

**Goals:**
- Never lose .env files again
- Zero friction when creating worktrees
- Easy backup and restore across machines
- Spend time coding, not configuring

**Motivations:**
- Efficiency - hates repetitive manual tasks
- Reliability - wants things to "just work"
- Independence - doesn't want to ask colleagues for env values

**Frustrations:**
- "I just want to clone and start working"
- "Why do I have to copy .env to every worktree?"
- "I deleted my project folder and lost my env config... again"

---

## Behavioral Patterns

### How Marc Discovers Tools:
1. Googles problem ("git worktree share env files")
2. Asks colleagues
3. Browses Reddit/HN for recommendations
4. Checks GitHub stars and recent activity
5. Reads README - if clear, tries it

### What Makes Marc Adopt a Tool:
- Solves a real problem he has
- Easy to install (`pip install` or `brew`)
- Works in 5 minutes or less
- Doesn't require accounts or cloud services
- Open source (can inspect, trust)

### What Makes Marc Abandon a Tool:
- Complex setup (> 10 minutes)
- Requires account creation
- Breaks existing workflow
- Poor error messages
- No recent updates (abandoned)

---

## User Journey Map

### Awareness
- **Trigger:** Loses .env file, frustrated
- **Action:** Searches for solution
- **Touchpoint:** GitHub, Reddit, HN
- **Emotion:** Frustrated, seeking solution

### Consideration
- **Trigger:** Finds xenv
- **Action:** Reads README, checks stars
- **Touchpoint:** GitHub README
- **Emotion:** Curious, slightly skeptical

### Adoption
- **Trigger:** README looks promising
- **Action:** `pip install xenv-cli && xenv init`
- **Touchpoint:** CLI
- **Emotion:** Hopeful

### Activation
- **Trigger:** First successful restore
- **Action:** Adds to .envrc, uses daily
- **Touchpoint:** .envrc integration
- **Emotion:** Relieved, satisfied

### Retention
- **Trigger:** Creates worktree, env just works
- **Action:** Keeps using, recommends to colleague
- **Touchpoint:** Daily workflow
- **Emotion:** Trusting, appreciative

### Advocacy
- **Trigger:** Colleague loses .env
- **Action:** Recommends xenv
- **Touchpoint:** Slack/conversation
- **Emotion:** Helpful, proud

---

## Jobs to Be Done

### Primary Job
> When I **delete a project folder or switch machines**, I want to **easily restore my .env files**, so I can **get back to coding without recreating configuration**.

### Secondary Jobs
> When I **create a git worktree**, I want to **automatically have my .env files available**, so I can **start working immediately**.

> When I **clone a project I've worked on before**, I want to **restore my previous env configuration**, so I can **avoid asking colleagues or recreating from memory**.

> When I **set up a new machine**, I want to **restore all my env files at once**, so I can **be productive quickly**.

---

## Design Implications

Based on Marc's profile:

| Insight | Design Decision |
|---------|-----------------|
| Uses direnv | .envrc integration is essential |
| Hates manual steps | Idempotent `xenv init` in .envrc |
| Works with monorepos | Support multiple .env files per repo |
| Uses worktrees | Auto-detect and share env files |
| Values open source | MIT license, transparent code |
| Wants CLI tools | Full-featured CLI with typer/rich |
| Limited time | Must work in < 5 minutes |

---

## Quotes (Synthesized)

> "I just want to clone a repo and have everything work."

> "Every time I make a new worktree, I forget to copy the .env file."

> "I've lost .env files twice this year. Never again."

> "I don't want another cloud account. Just give me a CLI tool."

> "If it takes more than 5 minutes to set up, I'm not using it."
