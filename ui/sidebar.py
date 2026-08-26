from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
)
from PySide6.QtCore import Qt, QTimer

from core.constants import SIDEBAR_W


class SidebarWidget(QWidget):
    """Sol kenar çubuğu: butonlar + açılır/kapanır animasyon."""

    def __init__(self, on_home, on_extensions, on_settings, on_toggle, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(SIDEBAR_W)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(2)
        layout.setAlignment(Qt.AlignTop)

        for icon, tip, fn in [
            ("⌕", "Ara",        None),
            ("⌂", "Ana Sayfa",   on_home),
            ("🧩", "Eklentiler",  on_extensions),
            ("⚙", "Ayarlar",    on_settings),
        ]:
            b = QPushButton(icon)
            b.setObjectName("sideBtn")
            b.setToolTip(tip)
            if fn:
                b.clicked.connect(fn)
            layout.addWidget(b, alignment=Qt.AlignHCenter)
        layout.addStretch()

        # ── Animasyon ──────────────────────────────────────────────────────
        self._open = True
        self._target = float(SIDEBAR_W)
        self._current = float(SIDEBAR_W)
        self._timer = QTimer(self)
        self._timer.setInterval(8)
        self._timer.timeout.connect(self._anim_step)
        self._on_toggle = on_toggle

    # ── Public API ──────────────────────────────────────────────────────────

    def toggle(self) -> bool:
        """Sidebar'ı aç/kapat; yeni durumu döndür."""
        self._open = not self._open
        self._target = float(SIDEBAR_W if self._open else 0)
        self._timer.start()
        return self._open

    @property
    def is_open(self) -> bool:
        return self._open

    # ── Internal ─────────────────────────────────────────────────────────────

    def _anim_step(self) -> None:
        diff = self._target - self._current
        if abs(diff) < 0.5:
            self._current = self._target
            self._timer.stop()
        else:
            self._current += diff * 0.07
        self.setFixedWidth(int(self._current))
