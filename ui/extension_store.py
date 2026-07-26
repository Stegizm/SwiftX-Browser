"""
ui/extension_store.py
Eklenti merkezi diyalogu.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QWidget,
)


class ExtensionStore(QDialog):
    """Eklentileri listeleyip etkinleştirmeye/devre dışı bırakmaya yarayan dialog."""

    def __init__(self, extensions: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Eklenti Merkezi")
        self.setGeometry(100, 100, 500, 600)
        self.extensions = extensions
        self.changes: dict = {}  # {ext_id: bool}

        self._build_ui()

    # ── UI inşası ──────────────────────────────────────────────────────────

    def _build_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("📦 SwiftX Eklenti Merkezi")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #fbfbfe; padding: 12px;")
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            "QScrollArea { background: #1c1b22; border: none; }"
            "QScrollBar:vertical { width: 8px; background: #2a2930; }"
            "QScrollBar::handle:vertical { background: #35343e; border-radius: 4px; }"
        )

        inner = QWidget()
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(12, 12, 12, 12)
        inner_layout.setSpacing(12)

        for ext in self.extensions:
            inner_layout.addWidget(self._create_item(ext))

        inner_layout.addStretch()
        scroll.setWidget(inner)
        layout.addWidget(scroll)

        # Butonlar
        btn_layout = QHBoxLayout()

        save_btn = QPushButton("💾 Değişiklikleri Kaydet")
        save_btn.setStyleSheet(
            "QPushButton { background: #5b5bef; color: #fff; border: none; "
            "border-radius: 4px; padding: 8px 16px; font-weight: bold; }"
            "QPushButton:hover { background: #7575ff; }"
        )
        save_btn.clicked.connect(self.accept)

        cancel_btn = QPushButton("✕ İptal")
        cancel_btn.setStyleSheet(
            "QPushButton { background: #2a2930; color: #fbfbfe; border: none; "
            "border-radius: 4px; padding: 8px 16px; }"
            "QPushButton:hover { background: #35343e; }"
        )
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def _create_item(self, ext: dict) -> QWidget:
        """Tek bir eklenti satırı oluştur."""
        widget = QWidget()
        widget.setStyleSheet("background: #2a2930; border-radius: 6px; padding: 12px;")
        h = QHBoxLayout(widget)

        info = QVBoxLayout()
        name_lbl = QLabel(f"{ext['icon']}  {ext['name']}")
        name_lbl.setStyleSheet("font-weight: bold; color: #fbfbfe; font-size: 13px;")
        desc_lbl = QLabel(ext["desc"])
        desc_lbl.setStyleSheet("color: #9e9db5; font-size: 11px;")
        ver_lbl = QLabel(f"v{ext['version']}")
        ver_lbl.setStyleSheet("color: #6e6d85; font-size: 10px;")
        info.addWidget(name_lbl)
        info.addWidget(desc_lbl)
        info.addWidget(ver_lbl)

        toggle_btn = QPushButton("Açık" if ext["enabled"] else "Kapalı")
        toggle_btn.setMaximumWidth(70)
        is_enabled = [ext["enabled"]]  # liste, closure'da değiştirilebilsin

        def _apply_style():
            c  = "#27ae60" if is_enabled[0] else "#e74c3c"
            hc = "#229954" if is_enabled[0] else "#c0392b"
            toggle_btn.setStyleSheet(
                f"QPushButton {{ background: {c}; color: #fff; border: none; "
                f"border-radius: 4px; padding: 6px 12px; font-weight: bold; }}"
                f"QPushButton:hover {{ background: {hc}; }}"
            )

        def _toggle():
            is_enabled[0] = not is_enabled[0]
            toggle_btn.setText("Açık" if is_enabled[0] else "Kapalı")
            _apply_style()
            self.changes[ext["id"]] = is_enabled[0]

        _apply_style()
        toggle_btn.clicked.connect(_toggle)

        h.addLayout(info)
        h.addStretch()
        h.addWidget(toggle_btn)
        return widget
