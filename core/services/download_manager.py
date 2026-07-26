"""
core/services/download_manager.py
İndirme (download) verisi ve Qt indirme isteği yönetimi.
"""

import os
from datetime import datetime
from typing import Callable, Optional

from PySide6.QtCore import QObject, QTimer
from PySide6.QtWebEngineCore import QWebEngineDownloadRequest

from core.constants import DL_FILE
from core.storage import load, save


class DownloadManager(QObject):
    """İndirme isteklerini karşılar ve kayıt tutar."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._downloads: list[dict] = load(DL_FILE, [])
        self._on_download_started: Optional[Callable] = None
        self._on_download_finished: Optional[Callable] = None

    # ── Public API ──────────────────────────────────────────────────────────

    @property
    def downloads(self) -> list[dict]:
        return list(self._downloads)

    def set_on_started(self, callback: Callable) -> None:
        self._on_download_started = callback

    def set_on_finished(self, callback: Callable) -> None:
        self._on_download_finished = callback

    def handle_request(self, dl: QWebEngineDownloadRequest) -> None:
        """QWebEngineProfile.downloadRequested sinyaline bağlanır."""
        dl_dir = os.path.expanduser("~/Downloads")
        if not os.path.exists(dl_dir):
            dl_dir = os.path.expanduser("~")
        name = dl.suggestedFileName()
        path = os.path.join(dl_dir, name)
        dl.setDownloadDirectory(dl_dir)
        dl.setDownloadFileName(name)
        dl.accept()

        if self._on_download_started:
            self._on_download_started(name)

        def on_finish():
            if not dl.isFinished():
                return
            self._downloads.insert(0, {
                "name": name,
                "path": path,
                "time": datetime.now().strftime("%d.%m.%Y %H:%M"),
            })
            self._save()
            if self._on_download_finished:
                self._on_download_finished(name)

        dl.isFinishedChanged.connect(lambda: on_finish())

    def clear(self) -> None:
        self._downloads = []
        self._save()

    # ── Internal ─────────────────────────────────────────────────────────────

    def _save(self) -> None:
        save(DL_FILE, self._downloads)
