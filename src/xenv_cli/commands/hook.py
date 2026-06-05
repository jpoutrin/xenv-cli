"""xenv hook command."""

import os
from typing import Optional

import typer

from xenv_cli.utils.console import console

# Shell hook templates
ZSH_HOOK = '''# xenv shell integration - add to ~/.zshrc:
# eval "$(xenv hook zsh)"

_xenv_hook() {
  # Skip if not in a git repo
  [[ -d .git ]] || git rev-parse --git-dir &>/dev/null 2>&1 || return 0

  # Cache key based on directory + env file mtimes
  local cache_dir="/tmp/xenv_cache_$UID"
  local env_mtime=""
  for f in .env.local .env.development .env.development.local .env.test .env.test.local; do
    [[ -f "$f" ]] && env_mtime+=$(stat -f %m "$f" 2>/dev/null || stat -c %Y "$f" 2>/dev/null)
  done
  local cache_key=$(echo -n "$PWD:$env_mtime" | md5 2>/dev/null || md5sum 2>/dev/null | cut -d' ' -f1)
  local cache_file="$cache_dir/$cache_key"

  mkdir -p "$cache_dir" 2>/dev/null

  # Skip if we already processed this exact state
  [[ -f "$cache_file" ]] && return 0

  # Run sync
  xenv sync 2>/dev/null

  # Mark this state as processed
  touch "$cache_file"

  # Cleanup old cache files (keep last 100)
  find "$cache_dir" -type f -mmin +60 -delete 2>/dev/null
}

precmd_functions+=(_xenv_hook)
'''

BASH_HOOK = '''# xenv shell integration - add to ~/.bashrc:
# eval "$(xenv hook bash)"

_xenv_hook() {
  # Skip if not in a git repo
  [[ -d .git ]] || git rev-parse --git-dir &>/dev/null 2>&1 || return 0

  # Cache key based on directory + env file mtimes
  local cache_dir="/tmp/xenv_cache_$UID"
  local env_mtime=""
  for f in .env.local .env.development .env.development.local .env.test .env.test.local; do
    [[ -f "$f" ]] && env_mtime+=$(stat -c %Y "$f" 2>/dev/null || stat -f %m "$f" 2>/dev/null)
  done
  local cache_key=$(echo -n "$PWD:$env_mtime" | md5sum 2>/dev/null | cut -d' ' -f1 || md5 2>/dev/null)
  local cache_file="$cache_dir/$cache_key"

  mkdir -p "$cache_dir" 2>/dev/null

  # Skip if we already processed this exact state
  [[ -f "$cache_file" ]] && return 0

  # Run sync
  xenv sync 2>/dev/null

  # Mark this state as processed
  touch "$cache_file"

  # Cleanup old cache files (keep last 100)
  find "$cache_dir" -type f -mmin +60 -delete 2>/dev/null
}

PROMPT_COMMAND="_xenv_hook${PROMPT_COMMAND:+;$PROMPT_COMMAND}"
'''

FISH_HOOK = '''# xenv shell integration - add to ~/.config/fish/config.fish:
# xenv hook fish | source

function _xenv_hook --on-variable PWD --on-event fish_prompt
  # Skip if not in a git repo
  if not test -d .git; and not git rev-parse --git-dir >/dev/null 2>&1
    return 0
  end

  # Cache key based on directory + env file mtimes
  set -l cache_dir /tmp/xenv_cache_(id -u)
  set -l env_mtime ""
  for f in .env.local .env.development .env.development.local .env.test .env.test.local
    if test -f $f
      set env_mtime $env_mtime(stat -c %Y $f 2>/dev/null; or stat -f %m $f 2>/dev/null)
    end
  end
  set -l cache_key (echo -n "$PWD:$env_mtime" | md5sum 2>/dev/null | cut -d' ' -f1; or md5 2>/dev/null)
  set -l cache_file $cache_dir/$cache_key

  mkdir -p $cache_dir 2>/dev/null

  # Skip if we already processed this exact state
  if test -f $cache_file
    return 0
  end

  # Run sync
  xenv sync 2>/dev/null

  # Mark this state as processed
  touch $cache_file

  # Cleanup old cache files
  find $cache_dir -type f -mmin +60 -delete 2>/dev/null
end
'''


def hook_cmd(
    shell: Optional[str] = typer.Argument(
        None,
        help="Shell type: bash, zsh, fish (auto-detected if omitted).",
    ),
) -> None:
    """Output shell code for automatic init and save.

    The hook runs on each prompt and automatically:
    - Restores missing .env files from the store
    - Saves modified .env files to the store
    """
    if shell is None:
        shell = _detect_shell()

    shell = shell.lower()

    if shell == "zsh":
        typer.echo(ZSH_HOOK)
    elif shell == "bash":
        typer.echo(BASH_HOOK)
    elif shell == "fish":
        typer.echo(FISH_HOOK)
    else:
        console.print(f"[red]Unknown shell: {shell}[/red]")
        console.print("Supported shells: bash, zsh, fish")
        raise typer.Exit(code=1)


def _detect_shell() -> str:
    """Detect the current shell from environment."""
    shell_path = os.environ.get("SHELL", "")
    if "zsh" in shell_path:
        return "zsh"
    elif "fish" in shell_path:
        return "fish"
    elif "bash" in shell_path:
        return "bash"
    else:
        # Default to zsh on macOS, bash otherwise
        import platform

        if platform.system() == "Darwin":
            return "zsh"
        return "bash"
