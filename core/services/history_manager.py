"""
core/services/history_manager.py
Geçmiş (history) verisi ve işlemleri.
"""

from datetime import datetime
from typing import Callable, Optional

from core.constants import HIST_FILE
from core.storage import load, save


class HistoryManager:
    """Geçmiş kayıtlarını yönetir."""

    MAX_ENTRIES = 500

    def __init__(self):
        self._history: list[dict] = load(HIST_FILE, [])
        self._on_changed: Optional[Callable] = None

    # ── Public API ──────────────────────────────────────────────────────────

    @property
    def history(self) -> list[dict]:
        return list(self._history)

    def set_on_changed(self, callback: Callable) -> None:
        self._on_changed = callback

    def add(self, title: str, url: str) -> None:
        if not url or url.startswith("file://") or url == "about:blank":
            return
        self._history.insert(0, {
            "title": title or url,
            "url": url,
            "time": datetime.now().strftime("%d.%m.%Y %H:%M"),
        })
        self._history = self._history[: self.MAX_ENTRIES]
        self._save()

    def clear(self) -> None:
        self._history = []
        self._save()
        if self._on_changed:
            self._on_changed(self._history)

    # ── Internal ─────────────────────────────────────────────────────────────

    def _save(self) -> None:
        save(HIST_FILE, self._history)
