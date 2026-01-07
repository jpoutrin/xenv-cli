"""Environment file model."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional


class SyncStatus(Enum):
    """Sync status between local and store."""

    SYNCED = "synced"
    LOCAL_NEWER = "local_newer"  # Local file is newer - will save
    STORE_NEWER = "store_newer"  # Store file is newer - will NOT overwrite
    MISSING_LOCAL = "missing_local"
    MISSING_STORE = "missing_store"


@dataclass
class EnvFile:
    """Represents an environment file."""

    name: str  # e.g., ".env.local"
    relative_path: str  # Path relative to git root (for monorepo)
    local_path: Optional[Path] = None  # Full path in project
    store_path: Optional[Path] = None  # Full path in CONF_HOME
    status: SyncStatus = SyncStatus.SYNCED
    local_mtime: Optional[datetime] = None
    store_mtime: Optional[datetime] = None

    @property
    def full_relative_path(self) -> str:
        """Get the full relative path including the filename."""
        if self.relative_path and self.relative_path != ".":
            return f"{self.relative_path}/{self.name}"
        return self.name

    def get_status_symbol(self) -> str:
        """Get status symbol for display."""
        symbols = {
            SyncStatus.SYNCED: "\u2713",  # checkmark
            SyncStatus.LOCAL_NEWER: "\u2191",  # up arrow
            SyncStatus.STORE_NEWER: "\u2193",  # down arrow
            SyncStatus.MISSING_LOCAL: "\u2717",  # x mark
            SyncStatus.MISSING_STORE: "+",
        }
        return symbols.get(self.status, "?")

    def get_status_text(self) -> str:
        """Get human-readable status text."""
        texts = {
            SyncStatus.SYNCED: "synced",
            SyncStatus.LOCAL_NEWER: "local newer (will save)",
            SyncStatus.STORE_NEWER: "store newer (will restore)",
            SyncStatus.MISSING_LOCAL: "missing locally",
            SyncStatus.MISSING_STORE: "new (not in store)",
        }
        return texts.get(self.status, "unknown")
