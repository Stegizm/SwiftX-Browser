"""
ui/side_panel.py
Sağ taraf paneli: Geçmiş, İndirilenler ve Ayarlar görünümleri.
Panel içeriği MainWindow tarafından doldurulur; bu modül sadece
widget ağacını ve stilini yönetir.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QListWidget, QScrollArea, QFrame,
)
from PySide6.QtCore import Qt


class SidePanel(QWidget):
    """
    Geçmiş / İndirilenler / Ayarlar için ortak çerçeve.

    Kullanım:
        panel = SidePanel(on_close=self._close_panel, on_clear=self._clear_panel)
        # Geçmiş göstermek için:
        panel.show_list("Geçmiş", items)
        # Ayarlar göstermek için:
        panel.show_settings(settings_widget)
    """

    def __init__(self, on_close, on_clear, parent=None):
        super().__init__(parent)
        self.setObjectName("panel")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Başlık satırı ──────────────────────────────────────────────────
        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)

        self._title_lbl = QLabel("Panel")
        self._title_lbl.setObjectName("panelTitle")

        close_btn = QPushButton("✕")
        close_btn.setObjectName("panelCloseBtn")
        close_btn.clicked.connect(on_close)

        top.addWidget(self._title_lbl)
        top.addStretch()
        top.addWidget(close_btn)
        root.addLayout(top)

        # ── Liste scroll alanı (geçmiş / indirilenler) ─────────────────────
        self._list_scroll = QScrollArea()
        self._list_scroll.setWidgetResizable(True)
        self._list_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._list_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._list_scroll.setFrameShape(QFrame.NoFrame)
        self._list_scroll.setStyleSheet(
            "QScrollArea { background: #17161d; }"
            "QScrollBar:vertical { width: 8px; background: #1c1b22; }"
            "QScrollBar::handle:vertical { background: #35343e; border-radius: 4px; }"
        )

        self.list_widget = QListWidget()
        self.list_widget.setObjectName("panelList")
        self.list_widget.setStyleSheet("")  # global #panelList stilini kullan

        self._clear_btn = QPushButton("Tümünü Temizle")
        self._clear_btn.setObjectName("clearBtn")
        self._clear_btn.clicked.connect(on_clear)

        list_container = QWidget()
        lc_layout = QVBoxLayout(list_container)
        lc_layout.setContentsMargins(0, 0, 0, 0)
        lc_layout.setSpacing(0)
        lc_layout.addWidget(self.list_widget)
        lc_layout.addWidget(self._clear_btn)

        self._list_scroll.setWidget(list_container)

        # ── Ayarlar scroll alanı ───────────────────────────────────────────
        self._settings_scroll = QScrollArea()
        self._settings_scroll.setWidgetResizable(True)
        self._settings_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._settings_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._settings_scroll.setFrameShape(QFrame.NoFrame)
        self._settings_scroll.setStyleSheet(
            "QScrollArea { background: #17161d; }"
            "QScrollBar:vertical { width: 8px; background: #1c1b22; }"
            "QScrollBar::handle:vertical { background: #35343e; border-radius: 4px; }"
        )

        root.addWidget(self._list_scroll)
        root.addWidget(self._settings_scroll)
        self._list_scroll.setVisible(False)
        self._settings_scroll.setVisible(False)

    # ── Genel arayüz ───────────────────────────────────────────────────────

    @property
    def title(self) -> str:
        return self._title_lbl.text()

    def show_list(self, title: str) -> None:
        """Liste görünümünü aktif et (içeriği caller doldurur)."""
        self._title_lbl.setText(title)
        self._list_scroll.setVisible(True)
        self._settings_scroll.setVisible(False)
        self.setVisible(True)

    def show_settings(self, title: str, settings_widget: QWidget) -> None:
        """Ayarlar görünümünü aktif et."""
        self._title_lbl.setText(title)
        self._settings_scroll.setWidget(settings_widget)
        self._list_scroll.setVisible(False)
        self._settings_scroll.setVisible(True)
        self.setVisible(True)

    def hide_panel(self) -> None:
        self.setVisible(False)
