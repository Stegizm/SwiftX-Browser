"""
core/services/settings_manager.py
Uygulama ayarlarını merkezi olarak yönetir.
"""

from typing import Callable, Optional

from core.constants import EXTENSIONS_FILE, DEFAULT_EXTENSIONS
from core.storage import load, save


class SettingsManager:
    """Tüm ayar bayraklarını ve eklentileri tutar; değişiklikte sinyal gönderir."""

    def __init__(self):
        self._extensions: list[dict] = load(EXTENSIONS_FILE, DEFAULT_EXTENSIONS)
        self._ad_blocker_enabled: bool = True
        self._smooth_scroll: bool = True
        self._dark_mode: bool = True
        self._restore_session: bool = True
        self._on_changed: Optional[Callable] = None

    # ── Public properties ──────────────────────────────────────────────────

    @property
    def extensions(self) -> list[dict]:
        return self._extensions

    @property
    def ad_blocker_enabled(self) -> bool:
        return self._ad_blocker_enabled

    @property
    def smooth_scroll(self) -> bool:
        return self._smooth_scroll

    @property
    def dark_mode(self) -> bool:
        return self._dark_mode

    @property
    def restore_session(self) -> bool:
        return self._restore_session

    def set_on_changed(self, callback: Callable) -> None:
        """Ayar değişikliğinde UI'yı güncellemek için kaydedilir."""
        self._on_changed = callback

    # ── Toggle helpers (DRY) ────────────────────────────────────────────────

    def toggle(self, attr_name: str) -> bool:
        """Genel toggle: attribute adını ver, yeni değeri döndür."""
        current = getattr(self, attr_name)
        setattr(self, f"_{attr_name}", not current)
        if self._on_changed:
            self._on_changed(attr_name, not current)
        return not current

    # ── Eklenti yönetimi ────────────────────────────────────────────────────

    def apply_extension_changes(self, changes: dict) -> None:
        for ext in self._extensions:
            if ext["id"] in changes:
                ext["enabled"] = changes[ext["id"]]
        save(EXTENSIONS_FILE, self._extensions)

    @property
    def active_extension_count(self) -> int:
        return sum(1 for e in self._extensions if e["enabled"])

    @property
    def total_extension_count(self) -> int:
        return len(self._extensions)
