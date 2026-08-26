"""
ui/bookmark_bar.py
Yer imleri çubuğu widget'ı.
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton,
    QScrollArea, QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor

from core.styles import MENU_STYLE


class BookmarkBar(QWidget):
    """Yer imi butonlarını gösterir; BookmarkManager'dan beslenir."""

    def __init__(self, on_click, on_remove, on_add, parent=None):
        super().__init__(parent)
        self.setObjectName("bmBar")
        self._on_click = on_click
        self._on_remove = on_remove

        h = QHBoxLayout(self)
        h.setContentsMargins(4, 0, 4, 0)
        h.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setFixedHeight(30)

        inner = QWidget()
        self._inner_layout = QHBoxLayout(inner)
        self._inner_layout.setContentsMargins(0, 0, 0, 0)
        self._inner_layout.setSpacing(0)
        self._inner_layout.addStretch()
        scroll.setWidget(inner)
        h.addWidget(scroll)

        add_btn = QPushButton("+")
        add_btn.setObjectName("bmAddBtn")
        add_btn.setToolTip("Mevcut sayfayı ekle")
        add_btn.clicked.connect(on_add)
        h.addWidget(add_btn)

    # ── Public API ──────────────────────────────────────────────────────────

    def refresh(self, bookmarks: list[dict]) -> None:
        """BookmarkManager'ın on_changed callback'inden çağrılır."""
        while self._inner_layout.count() > 1:
            item = self._inner_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for bm in bookmarks:
            btn = QPushButton(bm["title"])
            btn.setObjectName("bmBtn")
            btn.setToolTip(bm["url"])
            url = bm["url"]
            title = bm["title"]
            btn.clicked.connect(lambda checked=False, u=url: self._on_click(u))
            btn.setContextMenuPolicy(Qt.CustomContextMenu)
            btn.customContextMenuRequested.connect(
                lambda pos, t=title: self._context_menu(t)
            )
            self._inner_layout.insertWidget(self._inner_layout.count() - 1, btn)

    # ── Internal ─────────────────────────────────────────────────────────────

    def _context_menu(self, title: str) -> None:
        from PySide6.QtWidgets import QMenu

        menu = QMenu(self)
        menu.setStyleSheet(MENU_STYLE)
        rem = menu.addAction("🗑  Kaldır")
        if menu.exec(QCursor.pos()) == rem:
            self._on_remove(title)
