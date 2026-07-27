from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton,
)

from core.services.settings_manager import SettingsManager


class SettingsPanelWidget(QWidget):
    """Ayarlar panelinin içerik widget'ı.

    SettingsManager'dan ayarları okur, toggle callback'leri ile
    değişiklikleri geri bildirir.
    """

    def __init__(
        self,
        settings: SettingsManager,
        on_toggle: callable,
        on_clear_history: callable,
        parent=None,
    ):
        super().__init__(parent)
        self.setStyleSheet("background: #17161d;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(16)

        self._btn_map: dict[str, QPushButton] = {}

        self._add_toggle_row(layout, "🚫 Reklam Bloker",         "ad_blocker_enabled", settings.ad_blocker_enabled, on_toggle)
        self._add_toggle_row(layout, "🎯 Smooth Scroll",          "smooth_scroll",        settings.smooth_scroll,        on_toggle)
        self._add_toggle_row(layout, "🌙 Auto Dark Mode",         "dark_mode",            settings.dark_mode,            on_toggle)
        self._add_toggle_row(layout, "💾 Son Oturumu Geri Yükle", "restore_session",      settings.restore_session,      on_toggle)
        self._add_toggle_row(layout, "💤 Sekme Uyutma",           "tab_hibernate",        settings.tab_hibernate,        on_toggle)

        clear_btn = QPushButton("🗑  Tüm Geçmiş Temizle")
        clear_btn.setStyleSheet(
            "QPushButton { background: #e74c3c; color: #fff; border: none; "
            "border-radius: 4px; padding: 8px 12px; font-weight: bold; }"
            "QPushButton:hover { background: #c0392b; }"
        )
        clear_btn.clicked.connect(on_clear_history)
        layout.addWidget(clear_btn)

        about = QLabel(
            " ℹ SwiftX Browser v0.28.1\n\n"
            "Hızlı, Güvenli ve Açık Kaynaklı Tarayıcı Denemesi\n\n"
            "✓ Reklam Engelleyici  ✓ Smooth Scroller\n"
            "✓ Auto Dark Mode      ✓ Session Recovery\n"
            "✓ Sekme Uyutma        ✓ Geleneksel Sekme Düzeni\n"
            "✓ Eklenti Merkezi     ✓ Yer İmleri & Geçmiş\n\n"
            "Made with 💜 by YD Studio Team"
        )
        about.setStyleSheet(
            "color: #9e9db5; font-size: 11px; line-height: 1.8; "
            "padding: 12px; background: #1c1b22; border-radius: 6px;"
        )
        layout.addWidget(about)
        layout.addStretch()

    # ── Public API ──────────────────────────────────────────────────────────

    def update_toggle_btn(self, attr_name: str, enabled: bool) -> None:
        """SettingsManager'dan gelen değişiklik ile butonu günceller."""
        btn = self._btn_map.get(attr_name)
        if btn:
            btn.setText("Açık" if enabled else "Kapalı")
            self._apply_toggle_style(btn, enabled)

    # ── Internal ─────────────────────────────────────────────────────────────

    def _add_toggle_row(self, parent_layout, label_text, attr_name, initial, on_toggle):
        row = QHBoxLayout()
        lbl = QLabel(label_text)
        lbl.setStyleSheet("color: #fbfbfe; font-weight: bold; font-size: 13px;")

        btn = QPushButton("Açık" if initial else "Kapalı")
        btn.setMaximumWidth(80)
        self._apply_toggle_style(btn, initial)
        btn.clicked.connect(lambda: on_toggle(attr_name))

        self._btn_map[attr_name] = btn

        row.addWidget(lbl)
        row.addStretch()
        row.addWidget(btn)
        parent_layout.addLayout(row)

    @staticmethod
    def _apply_toggle_style(btn: QPushButton, enabled: bool) -> None:
        c  = "#27ae60" if enabled else "#e74c3c"
        hc = "#229954" if enabled else "#c0392b"
        btn.setStyleSheet(
            f"QPushButton {{ background: {c}; color: #fff; border: none; "
            f"border-radius: 4px; padding: 6px 12px; font-weight: bold; }}"
            f"QPushButton:hover {{ background: {hc}; }}"
        )
