"""
ui/tab_bar.py
Geleneksel tarayıcı sekme çubuğu.

Sekmeler soldan sağa dizilir, her sekmenin sağında kapat butonu her zaman görünür.
Sekme fazlaysa yatay kaydırma (scroll) yapılır.
'+' yeni sekme butonu sekmelerin hemen sonrasındadır.
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QScrollArea,
    QSizePolicy, QToolTip,
)
from PySide6.QtCore import Qt, QSize, Signal

from core.constants import TAB_COLORS


HIBERNATE_HTML = """<html><head><style>
body {
  background: #1c1b22;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  margin: 0;
  font-family: 'SF Pro Text', 'Helvetica Neue', 'Segoe UI', sans-serif;
  color: #6e6d85;
}
.container {
  text-align: center;
}
.sleep-icon { font-size: 48px; margin-bottom: 12px; }
.sleep-title { font-size: 16px; font-weight: bold; color: #9e9db5; }
.sleep-hint { font-size: 12px; margin-top: 8px; color: #4a4960; }
</style></head><body>
<div class="container">
  <div class="sleep-icon">💤</div>
  <div class="sleep-title">Sekme Uykuda</div>
  <div class="sleep-hint">Sekmeye tıklayarak yeniden aktif edin</div>
</div>
</body></html>"""


class TabItem(QWidget):
    """Tek bir sekme item'i: ikon + başlık + kapat butonu."""

    close_clicked = Signal()
    middle_clicked = Signal()

    def __init__(self, index: int, on_click, on_right_click):
        super().__init__()
        self.index = index
        self._on_click = on_click
        self._on_right_click = on_right_click
        self._hibernated = False
        self._color = ""

        self.setObjectName("tabItem")
        self.setFixedHeight(32)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 4, 0)
        layout.setSpacing(4)

        # Uyku göstergesi
        self._sleep_icon = QPushButton("")
        self._sleep_icon.setObjectName("tabSleepIcon")
        self._sleep_icon.setFixedSize(14, 14)
        self._sleep_icon.setVisible(False)
        self._sleep_icon.setText("💤")
        layout.addWidget(self._sleep_icon)

        # Başlık
        self.title_btn = QPushButton("Yeni Sekme")
        self.title_btn.setObjectName("tabTitleBtn")
        self.title_btn.setProperty("active", False)
        self.title_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.title_btn.clicked.connect(lambda: self._on_click(self.index))
        self.title_btn.setContextMenuPolicy(Qt.CustomContextMenu)
        self.title_btn.customContextMenuRequested.connect(
            lambda pos: self._on_right_click(pos, self.index)
        )
        layout.addWidget(self.title_btn)

        # Kapat butonu — HER ZAMAN görünür
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("tabCloseBtn")
        self.close_btn.setFixedSize(18, 18)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.close_clicked)
        layout.addWidget(self.close_btn)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.middle_clicked.emit()
        super().mouseReleaseEvent(event)

    def set_active(self, active: bool) -> None:
        self.title_btn.setProperty("active", active)
        self.title_btn.style().unpolish(self.title_btn)
        self.title_btn.style().polish(self.title_btn)
        self.style().unpolish(self)
        self.style().polish(self)

    def set_title(self, title: str) -> None:
        display = (title[:20] + "…") if len(title) > 22 else (title or "Yeni Sekme")
        if self._hibernated:
            display = "💤 " + display
        self.title_btn.setText(display)
        self.title_btn.setToolTip(title or "Yeni Sekme")

    def set_color(self, color_name: str) -> None:
        self._color = color_name
        bg, fg = TAB_COLORS.get(color_name, ("", ""))
        if bg:
            self.setStyleSheet(
                f"#tabItem {{ background: {bg}; border-top: 2px solid {bg}; }}"
                f"#tabTitleBtn {{ background: transparent; color: {fg}; }}"
                f"#tabTitleBtn:hover {{ background: rgba(255,255,255,0.1); }}"
            )
        else:
            self.setStyleSheet("")
            self.style().unpolish(self)
            self.style().polish(self)

    def set_hibernated(self, hibernated: bool) -> None:
        self._hibernated = hibernated
        self._sleep_icon.setVisible(hibernated)


class TabBar(QWidget):
    """Geleneksel tarayıcı sekme çubuğu — scrollable, + butonu sekmelerin sonunda."""

    new_tab_requested = Signal()
    tab_close_requested = Signal(int)
    tab_switch_requested = Signal(int)
    tab_context_requested = Signal(object, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("tabBarContainer")

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Scroll area for tabs — + butonu DAHİL'de
        self._scroll = QScrollArea()
        self._scroll.setObjectName("tabScrollArea")
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._scroll.setFixedHeight(36)

        self._scroll_content = QWidget()
        self._scroll_content.setObjectName("tabScrollContent")
        self._tabs_layout = QHBoxLayout(self._scroll_content)
        self._tabs_layout.setContentsMargins(4, 2, 2, 2)
        self._tabs_layout.setSpacing(1)
        self._tabs_layout.addStretch()

        # '+' butonunu scroll alanının İÇİNE ekle (stretch'ten önce)
        self._new_tab_btn = QPushButton("+")
        self._new_tab_btn.setObjectName("newTabBtn")
        self._new_tab_btn.setFixedSize(28, 28)
        self._new_tab_btn.setCursor(Qt.PointingHandCursor)
        self._new_tab_btn.clicked.connect(self.new_tab_requested.emit)
        self._tabs_layout.insertWidget(self._tabs_layout.count() - 1, self._new_tab_btn)

        self._scroll.setWidget(self._scroll_content)
        root.addWidget(self._scroll)

        self._items: list[TabItem] = []

    def add_tab(self, index: int, on_click, on_close, on_right_click) -> TabItem:
        """Yeni sekme ekle ve TabItem döndür."""
        item = TabItem(
            index=index,
            on_click=on_click,
            on_right_click=on_right_click,
        )
        item.close_clicked.connect(lambda i=index: on_close(i))
        item.middle_clicked.connect(lambda i=index: on_close(i))

        # '+' butonundan önce ekle (stretch'ten 2 önce)
        insert_pos = self._tabs_layout.count() - 2  # -1 = stretch, -2 = + btn
        self._tabs_layout.insertWidget(insert_pos, item)

        self._items.append(item)
        return item

    def remove_tab(self, index: int) -> None:
        """Sekmeyi kaldır."""
        if 0 <= index < len(self._items):
            item = self._items.pop(index)
            self._tabs_layout.removeWidget(item)
            item.deleteLater()

    def rewire(self, on_click, on_close, on_right_click):
        """Sekme silindikten sonra index'leri güncelle."""
        for i, item in enumerate(self._items):
            item.index = i
            try:
                item.title_btn.clicked.disconnect()
            except Exception:
                pass
            try:
                item.title_btn.customContextMenuRequested.disconnect()
            except Exception:
                pass
            try:
                item.close_clicked.disconnect()
            except Exception:
                pass
            try:
                item.middle_clicked.disconnect()
            except Exception:
                pass

            item.title_btn.clicked.connect(lambda checked=False, idx=i: on_click(idx))
            item.title_btn.customContextMenuRequested.connect(
                lambda pos, idx=i: on_right_click(pos, idx)
            )
            item.close_clicked.connect(lambda idx=i: on_close(idx))
            item.middle_clicked.connect(lambda idx=i: on_close(idx))

    def set_active(self, index: int) -> None:
        """Tüm sekmeleri pasif yap, sadece verilen index'i aktif et."""
        for i, item in enumerate(self._items):
            item.set_active(i == index)

    def get_item(self, index: int) -> TabItem | None:
        """Belirtilen index'teki TabItem'ı döndür."""
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def scroll_to_tab(self, index: int) -> None:
        """Belirtilen sekmeyi görünebilir hale getir."""
        if 0 <= index < len(self._items):
            item = self._items[index]
            self._scroll.ensureWidgetVisible(item, 0, 0)

    @property
    def count(self) -> int:
        return len(self._items)
