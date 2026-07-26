"""
core/services/bookmark_manager.py
Yer imleri (bookmark) verisi ve işlemleri.
"""

from typing import Callable, Optional

from core.constants import BM_FILE
from core.storage import load, save


class BookmarkManager:
    """Yer imlerini yönetir; UI ile iletişim sinyal tabanlıdır."""

    def __init__(self):
        self._bookmarks: list[dict] = load(BM_FILE, [])
        self._on_changed: Optional[Callable] = None

    # ── Public API ──────────────────────────────────────────────────────────

    @property
    def bookmarks(self) -> list[dict]:
        return list(self._bookmarks)

    def set_on_changed(self, callback: Callable) -> None:
        """UI katmanını yer imi değişikliğini dinlemek için kaydeder."""
        self._on_changed = callback

    def add(self, url: str, title: str) -> str | None:
        """
        Yeni yer imi ekler.
        Returns:
            Hata mesajı (str) veya None (başarılı).
        """
        if not url or url.startswith("file://") or url == "about:blank":
            return "Bu sayfa yer imine eklenemez."
        if any(b["url"] == url for b in self._bookmarks):
            return "Bu sayfa zaten yer imlerinde."
        self._bookmarks.append({"title": title[:30], "url": url})
        self._save()
        self._notify()
        return None

    def remove(self, title: str) -> None:
        """Başlığa göre yer imini siler."""
        self._bookmarks = [b for b in self._bookmarks if b["title"] != title]
        self._save()
        self._notify()

    def clear_all(self) -> None:
        self._bookmarks = []
        self._save()
        self._notify()

    # ── Internal ─────────────────────────────────────────────────────────────

    def _save(self) -> None:
        save(BM_FILE, self._bookmarks)

    def _notify(self) -> None:
        if self._on_changed:
            self._on_changed(self._bookmarks)
