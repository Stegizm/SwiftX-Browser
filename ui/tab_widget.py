"""
ui/tab_widget.py
Sekme çubuğundaki tek bir sekmeyi temsil eden widget.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt

from core.constants import TAB_COLORS


class TabWidget(QWidget):
    """Sekme butonu + kapat butonu çifti."""

    def __init__(self, on_click, on_close, on_right_click):
        super().__init__()
        self.setObjectName("tabWidget")
        self._color = ""

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.btn = QPushButton("Yeni Sekme")
        self.btn.setObjectName("tabBtn")
        self.btn.setProperty("active", False)
        self.btn.clicked.connect(on_click)
        self.btn.setContextMenuPolicy(Qt.CustomContextMenu)
        self.btn.customContextMenuRequested.connect(on_right_click)

        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("tabCloseBtn")
        self.close_btn.clicked.connect(on_close)

        layout.addWidget(self.btn)
        layout.addWidget(self.close_btn)

    # ── Durum güncellemeleri ───────────────────────────────────────────────

    def set_active(self, active: bool) -> None:
        self.btn.setProperty("active", active)
        self.btn.style().unpolish(self.btn)
        self.btn.style().polish(self.btn)

    def set_title(self, title: str) -> None:
        self.btn.setText((title[:22] + "…") if len(title) > 24 else title or "Yeni Sekme")

    def set_color(self, color_name: str) -> None:
        self._color = color_name
        bg, fg = TAB_COLORS.get(color_name, ("", ""))
        if bg:
            self.btn.setStyleSheet(
                f"#tabBtn {{ background: {bg}; color: {fg}; border-radius: 6px; }}"
                f"#tabBtn:hover {{ background: {bg}; opacity: 0.8; }}"
            )
        else:
            self.btn.setStyleSheet("")
            self.btn.style().unpolish(self.btn)
            self.btn.style().polish(self.btn)
