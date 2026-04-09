# windows/main_window.py
# Ana pencere — artık sadece koordinasyon yapar.
# Tüm alt bileşenler ayrı modüllerde; bu sınıf onları birbirine bağlar.
import os
import sys
from datetime import datetime

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QProgressBar, QStackedWidget,
    QScrollArea, QSizePolicy, QStatusBar, QFrame, QLabel,
    QMenu, QListWidgetItem,
)
from PySide6.QtWebEngineCore import QWebEngineDownloadRequest, QWebEnginePermission, QWebEngineProfile
from PySide6.QtCore import QUrl, Qt, QTimer, QSize
from PySide6.QtGui import QAction, QCursor, QIcon

from core.constants import (
    SIDEBAR_W, TAB_COLORS,
    BM_FILE, HIST_FILE, DL_FILE, SESSION_FILE, EXTENSIONS_FILE,
    DEFAULT_EXTENSIONS,
)
from core.storage  import load, save
from core.styles   import STYLE, MENU_STYLE
from engine.ad_blocker  import AdBlocker
from engine.browser_page import BrowserPage
from ui.tab_widget       import TabWidget
from ui.extension_store  import ExtensionStore
from ui.side_panel       import SidePanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.HOME = self._resolve_home()

        # ── Kalıcı veriler ────────────────────────────────────────────────
        self._bookmarks  = load(BM_FILE,  [])
        self._history    = load(HIST_FILE, [])
        self._downloads  = load(DL_FILE,  [])
        self._extensions = load(EXTENSIONS_FILE, DEFAULT_EXTENSIONS)
        self._ad_blocker = AdBlocker()

        # ── Ayarlar ───────────────────────────────────────────────────────
        self._smooth_scroll    = True
        self._dark_mode        = True
        self._restore_session  = True

        # ── Web Engine profili ────────────────────────────────────────────
        profile = QWebEngineProfile.defaultProfile()
        profile.setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies
        )

        # ── Pencere temel ayarları ────────────────────────────────────────
        self.setWindowTitle("SwiftX")
        _here = self._data_dir()
        self.setWindowIcon(QIcon(os.path.join(_here, "SXBETALOGO3.png")))
        self.resize(1360, 860)
        self.setStyleSheet(STYLE)

        self._tabs:   list[tuple[TabWidget, BrowserPage]] = []
        self._active: int  = -1
        self._sidebar_open = True
        self._panel_visible = False

        self._build_ui()
        self._load_session()

    # ══════════════════════════════════════════════════════════════════════
    # Yardımcı: HOME url belirleme
    # ══════════════════════════════════════════════════════════════════════

    def _data_dir(self) -> str:
        if getattr(sys, "frozen", False):
            base = os.path.dirname(sys.executable)
            for candidate in [
                os.path.join(base, "data"),
                os.path.join(base, "_internal", "data"),
            ]:
                if os.path.isdir(candidate):
                    return candidate
            return base
        base = os.path.dirname(os.path.abspath(__file__))
        # windows/ klasöründeyiz, üst dizine bak
        root = os.path.dirname(base)
        candidate = os.path.join(root, "data")
        return candidate if os.path.isdir(candidate) else root

    def _resolve_home(self) -> str:
        _here = self._data_dir()
        html  = os.path.join(_here, "home (v6).html")
        if os.path.exists(html):
            path = html.replace("\\", "/")
            if not path.startswith("/"):
                path = "/" + path
            return "file://" + path
        return "https://www.startpage.com"

    # ══════════════════════════════════════════════════════════════════════
    # UI İnşası
    # ══════════════════════════════════════════════════════════════════════

    def _build_ui(self):
        root   = QWidget()
        root_h = QHBoxLayout(root)
        root_h.setContentsMargins(0, 0, 0, 0)
        root_h.setSpacing(0)

        root_h.addWidget(self._build_sidebar())
        root_h.addWidget(self._build_center())
        root_h.addWidget(self._build_panel())

        self.setCentralWidget(root)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        self.btn_back.clicked.connect(self._go_back)
        self.btn_forward.clicked.connect(self._go_forward)
        self.btn_reload.clicked.connect(self._reload)

        self._register_shortcuts()
        self.destroyed.connect(self._save_session)

    # ── Sidebar ────────────────────────────────────────────────────────────

    def _build_sidebar(self) -> QWidget:
        self._sidebar = QWidget()
        self._sidebar.setObjectName("sidebar")
        self._sidebar.setFixedWidth(SIDEBAR_W)
        sb = QVBoxLayout(self._sidebar)
        sb.setContentsMargins(0, 8, 0, 8)
        sb.setSpacing(2)
        sb.setAlignment(Qt.AlignTop)

        for icon, tip, fn in [
            ("⌕", "Ara",       None),
            ("⌂", "Ana Sayfa", "_go_home"),
            ("🧩", "Eklentiler", "_open_extensions"),
            ("⚙", "Ayarlar",   "_toggle_settings"),
        ]:
            b = QPushButton(icon)
            b.setObjectName("sideBtn")
            b.setToolTip(tip)
            if fn:
                b.clicked.connect(getattr(self, fn))
            sb.addWidget(b, alignment=Qt.AlignHCenter)
        sb.addStretch()

        # Animasyon değişkenleri
        self._anim_timer   = QTimer()
        self._anim_timer.setInterval(8)
        self._anim_timer.timeout.connect(self._anim_step)
        self._anim_target  = float(SIDEBAR_W)
        self._anim_current = float(SIDEBAR_W)

        return self._sidebar

    # ── Orta alan ──────────────────────────────────────────────────────────

    def _build_center(self) -> QWidget:
        mid   = QWidget()
        mid_v = QVBoxLayout(mid)
        mid_v.setContentsMargins(0, 0, 0, 0)
        mid_v.setSpacing(0)

        mid_v.addWidget(self._build_tab_strip())
        mid_v.addWidget(self._build_nav_bar())
        mid_v.addWidget(self._build_bookmark_bar())

        self.progress = QProgressBar()
        self.progress.setObjectName("progress")
        self.progress.setTextVisible(False)
        self.progress.setRange(0, 100)
        self.progress.setVisible(False)
        mid_v.addWidget(self.progress)

        self.stack = QStackedWidget()
        mid_v.addWidget(self.stack)
        mid_v.addWidget(self._build_dl_bar())

        return mid

    def _build_tab_strip(self) -> QWidget:
        tab_strip = QWidget()
        tab_strip.setObjectName("tabStrip")
        self._tl = QHBoxLayout(tab_strip)
        self._tl.setContentsMargins(0, 0, 6, 0)
        self._tl.setSpacing(0)

        self._toggle_btn = QPushButton("☰")
        self._toggle_btn.setObjectName("toggleBtn")
        self._toggle_btn.setToolTip("Sidebar Aç/Kapat (Ctrl+B)")
        self._toggle_btn.clicked.connect(self._toggle_sidebar)
        self._tl.addWidget(self._toggle_btn)
        self._tl.addStretch()

        ntb = QPushButton("+")
        ntb.setObjectName("newTabBtn")
        ntb.clicked.connect(self._new_tab)
        self._tl.addWidget(ntb)

        return tab_strip

    def _build_nav_bar(self) -> QWidget:
        nav_bar = QWidget()
        nav_bar.setObjectName("navBar")
        nav_h = QHBoxLayout(nav_bar)
        nav_h.setContentsMargins(8, 6, 8, 6)
        nav_h.setSpacing(4)

        self.btn_back    = self._nav_btn("←")
        self.btn_forward = self._nav_btn("→")
        self.btn_reload  = self._nav_btn("↻")

        self.url_bar = QLineEdit()
        self.url_bar.setObjectName("urlBar")
        self.url_bar.setPlaceholderText("Ara veya adres gir")
        self.url_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.url_bar.returnPressed.connect(self._navigate)

        self.btn_star = self._nav_btn("☆")
        self.btn_star.setToolTip("Yer İmine Ekle (Ctrl+D)")
        self.btn_star.clicked.connect(self._add_bookmark)

        self.btn_hist = self._nav_btn("🕐")
        self.btn_hist.setToolTip("Geçmiş (Ctrl+H)")
        self.btn_hist.clicked.connect(self._toggle_history)

        self.btn_dl = self._nav_btn("↓")
        self.btn_dl.setToolTip("İndirilenler (Ctrl+J)")
        self.btn_dl.clicked.connect(self._toggle_downloads)

        for w in [self.btn_back, self.btn_forward, self.btn_reload]:
            nav_h.addWidget(w)
        nav_h.addSpacing(6)
        nav_h.addWidget(self.url_bar)
        nav_h.addSpacing(4)
        for w in [self.btn_star, self.btn_hist, self.btn_dl]:
            nav_h.addWidget(w)

        return nav_bar

    def _nav_btn(self, text: str) -> QPushButton:
        b = QPushButton(text)
        b.setObjectName("navBtn")
        return b

    def _build_bookmark_bar(self) -> QWidget:
        container = QWidget()
        container.setObjectName("bmBar")
        h = QHBoxLayout(container)
        h.setContentsMargins(4, 0, 4, 0)
        h.setSpacing(0)

        bm_scroll = QScrollArea()
        bm_scroll.setWidgetResizable(True)
        bm_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        bm_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        bm_scroll.setFrameShape(QFrame.NoFrame)
        bm_scroll.setFixedHeight(30)

        bm_inner = QWidget()
        self._bm_inner_layout = QHBoxLayout(bm_inner)
        self._bm_inner_layout.setContentsMargins(0, 0, 0, 0)
        self._bm_inner_layout.setSpacing(0)
        self._bm_inner_layout.addStretch()
        bm_scroll.setWidget(bm_inner)
        h.addWidget(bm_scroll)

        add_bm = QPushButton("+")
        add_bm.setObjectName("bmAddBtn")
        add_bm.setToolTip("Mevcut sayfayı ekle")
        add_bm.clicked.connect(self._add_bookmark)
        h.addWidget(add_bm)

        self._refresh_bookmarks()
        return container

    def _build_dl_bar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("dlBar")
        h = QHBoxLayout(bar)
        h.setContentsMargins(12, 0, 8, 0)
        h.setSpacing(8)

        self._dl_label = QLabel("")
        self._dl_label.setObjectName("dlLabel")

        dl_close = QPushButton("✕")
        dl_close.setObjectName("dlCloseBtn")
        dl_close.clicked.connect(lambda: bar.setVisible(False))

        h.addWidget(self._dl_label)
        h.addStretch()
        h.addWidget(dl_close)
        bar.setVisible(False)
        self._dl_bar = bar
        return bar

    # ── Sağ Panel ──────────────────────────────────────────────────────────

    def _build_panel(self) -> SidePanel:
        self._panel = SidePanel(
            on_close=self._close_panel,
            on_clear=self._clear_panel,
        )
        self._panel.list_widget.itemDoubleClicked.connect(self._panel_item_clicked)
        self._panel.setVisible(False)

        # Ayarlar widget'ını tek seferinde inşa et
        self._settings_widget = self._build_settings_widget()

        return self._panel

    def _build_settings_widget(self) -> QWidget:
        """Ayarlar panelinin içerik widget'ı."""
        inner = QWidget()
        inner.setStyleSheet("background: #17161d;")
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(16)

        def _toggle_row(label_text, initial, on_toggle):
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setStyleSheet("color: #fbfbfe; font-weight: bold; font-size: 13px;")
            btn = QPushButton("Açık" if initial else "Kapalı")
            btn.setMaximumWidth(80)
            self._apply_toggle_style(btn, initial)
            btn.clicked.connect(lambda: on_toggle(btn))
            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(btn)
            layout.addLayout(row)
            return btn

        self._ad_block_btn  = _toggle_row("🚫 Reklam Bloker",          self._ad_blocker.enabled, self._toggle_ad_blocker)
        self._smooth_btn    = _toggle_row("🎯 Smooth Scroll",           self._smooth_scroll,       self._toggle_smooth_scroll)
        self._dark_btn      = _toggle_row("🌙 Auto Dark Mode",          self._dark_mode,           self._toggle_dark_mode)
        self._session_btn   = _toggle_row("💾 Son Oturumu Geri Yükle",  self._restore_session,     self._toggle_session_recovery)

        clear_btn = QPushButton("🗑  Tüm Geçmiş Temizle")
        clear_btn.setStyleSheet(
            "QPushButton { background: #e74c3c; color: #fff; border: none; "
            "border-radius: 4px; padding: 8px 12px; font-weight: bold; }"
            "QPushButton:hover { background: #c0392b; }"
        )
        clear_btn.clicked.connect(self._clear_all_history)
        layout.addWidget(clear_btn)

        about = QLabel(
            " ℹ SwiftX Browser v0.27.1-OpenAlpha\n\n"
            "   Build Date: 4.04.2026\n\n"
            "Hızlı, Güvenli ve Açık Kaynaklı Tarayıcı Denemesi\n\n"
            "✓ Reklam Engelleyici  ✓ Smooth Scroller\n"
            "✓ Auto Dark Mode      ✓ Session Recovery\n"
            "✓ Eklenti Merkezi     ✓ Yer İmleri & Geçmiş\n\n"
            "Made with 💜 by YD Studio Team"
        )
        about.setStyleSheet(
            "color: #9e9db5; font-size: 11px; line-height: 1.8; "
            "padding: 12px; background: #1c1b22; border-radius: 6px;"
        )
        layout.addWidget(about)
        layout.addStretch()
        return inner

    # ── Kısayollar ────────────────────────────────────────────────────────

    def _register_shortcuts(self):
        shortcuts = [
            ("Ctrl+T",     self._new_tab),
            ("Ctrl+W",     self._close_current),
            ("F5",         self._reload),
            ("Ctrl+R",     self._reload),
            ("Alt+Left",   self._go_back),
            ("Alt+Right",  self._go_forward),
            ("Ctrl+L",     self._focus_url),
            ("Ctrl+B",     self._toggle_sidebar),
            ("Ctrl+D",     self._add_bookmark),
            ("Ctrl+H",     self._toggle_history),
            ("Ctrl+J",     self._toggle_downloads),
        ]
        for key, fn in shortcuts:
            a = QAction(self)
            a.setShortcut(key)
            a.triggered.connect(fn)
            self.addAction(a)

    # ══════════════════════════════════════════════════════════════════════
    # Oturum yönetimi
    # ══════════════════════════════════════════════════════════════════════

    def _save_session(self):
        session = {
            "tabs": [
                {"url": t[1].url, "title": t[1].title}
                for t in self._tabs if t[1].url != self.HOME
            ],
            "active": self._active,
        }
        save(SESSION_FILE, session)

    def _load_session(self):
        if not self._restore_session:
            self._new_tab()
            return
        session = load(SESSION_FILE, None)
        if session and session.get("tabs"):
            for td in session["tabs"]:
                self._new_tab(td.get("url", self.HOME))
            idx = session.get("active", 0)
            if 0 <= idx < len(self._tabs):
                self._switch(idx)
            self.status.showMessage(f"✓ {len(session['tabs'])} sekme geri yüklendi", 3000)
        else:
            self._new_tab()

    # ══════════════════════════════════════════════════════════════════════
    # Sidebar animasyonu
    # ══════════════════════════════════════════════════════════════════════

    def _toggle_sidebar(self):
        self._sidebar_open = not self._sidebar_open
        self._anim_target = float(SIDEBAR_W if self._sidebar_open else 0)
        self._toggle_btn.setText("☰" if self._sidebar_open else "▶")
        self._anim_timer.start()

    def _anim_step(self):
        diff = self._anim_target - self._anim_current
        if abs(diff) < 0.5:
            self._anim_current = self._anim_target
            self._anim_timer.stop()
        else:
            self._anim_current += diff * 0.07
        self._sidebar.setFixedWidth(int(self._anim_current))

    # ══════════════════════════════════════════════════════════════════════
    # Eklenti merkezi
    # ══════════════════════════════════════════════════════════════════════

    def _open_extensions(self):
        dialog = ExtensionStore(self._extensions, self)
        if dialog.exec():
            for ext in self._extensions:
                if ext["id"] in dialog.changes:
                    ext["enabled"] = dialog.changes[ext["id"]]
            save(EXTENSIONS_FILE, self._extensions)
            enabled = sum(1 for e in self._extensions if e["enabled"])
            self.status.showMessage(
                f"✓ {enabled} eklenti aktif, {len(self._extensions) - enabled} devre dışı", 3000
            )

    # ══════════════════════════════════════════════════════════════════════
    # Yer imleri
    # ══════════════════════════════════════════════════════════════════════

    def _refresh_bookmarks(self):
        while self._bm_inner_layout.count() > 1:
            item = self._bm_inner_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for bm in self._bookmarks:
            btn = QPushButton(bm["title"])
            btn.setObjectName("bmBtn")
            btn.setToolTip(bm["url"])
            url = bm["url"]
            btn.clicked.connect(lambda checked=False, u=url: self._open_url(u))
            btn.setContextMenuPolicy(Qt.CustomContextMenu)
            title = bm["title"]
            btn.customContextMenuRequested.connect(
                lambda pos, t=title: self._bm_context(pos, t)
            )
            self._bm_inner_layout.insertWidget(self._bm_inner_layout.count() - 1, btn)

    def _add_bookmark(self):
        p = self._cur()
        if not p:
            return
        url, title = p.url, p.title or p.url
        if url.startswith("file://") or not url or url == "about:blank":
            return
        if any(b["url"] == url for b in self._bookmarks):
            self.status.showMessage("Bu sayfa zaten yer imlerinde.", 2000)
            return
        self._bookmarks.append({"title": title[:30], "url": url})
        save(BM_FILE, self._bookmarks)
        self._refresh_bookmarks()
        self.btn_star.setText("★")
        QTimer.singleShot(1500, lambda: self.btn_star.setText("☆"))
        self.status.showMessage(f"'{title[:30]}' yer imlerine eklendi.", 2000)

    def _bm_context(self, pos, title: str):
        menu = QMenu(self)
        menu.setStyleSheet(MENU_STYLE)
        rem = menu.addAction("🗑  Kaldır")
        if menu.exec(QCursor.pos()) == rem:
            self._bookmarks = [b for b in self._bookmarks if b["title"] != title]
            save(BM_FILE, self._bookmarks)
            self._refresh_bookmarks()

    # ══════════════════════════════════════════════════════════════════════
    # Geçmiş
    # ══════════════════════════════════════════════════════════════════════

    def _add_history(self, title: str, url: str):
        if not url or url.startswith("file://") or url == "about:blank":
            return
        self._history.insert(0, {
            "title": title or url,
            "url": url,
            "time": datetime.now().strftime("%d.%m.%Y %H:%M"),
        })
        self._history = self._history[:500]
        save(HIST_FILE, self._history)

    def _toggle_history(self):
        if self._panel_visible and self._panel.title == "Geçmiş":
            self._close_panel()
            return
        self._panel.list_widget.clear()
        for h in self._history:
            item = QListWidgetItem(f"  {h['time']}  —  {h['title'][:50]}")
            item.setData(Qt.UserRole, h["url"])
            self._panel.list_widget.addItem(item)
        self._panel.show_list("Geçmiş")
        self._panel_visible = True

    # ══════════════════════════════════════════════════════════════════════
    # İndirilenler
    # ══════════════════════════════════════════════════════════════════════

    def _toggle_downloads(self):
        if self._panel_visible and self._panel.title == "İndirilenler":
            self._close_panel()
            return
        self._panel.list_widget.clear()
        for d in self._downloads:
            item = QListWidgetItem(f"  {d['time']}  —  {d['name']}")
            item.setData(Qt.UserRole, d.get("path", ""))
            self._panel.list_widget.addItem(item)
        self._panel.show_list("İndirilenler")
        self._panel_visible = True

    # ══════════════════════════════════════════════════════════════════════
    # Ayarlar
    # ══════════════════════════════════════════════════════════════════════

    def _toggle_settings(self):
        if self._panel_visible and self._panel.title == "Ayarlar":
            self._close_panel()
            return
        self._panel.show_settings("Ayarlar", self._settings_widget)
        self._panel_visible = True

    def _apply_toggle_style(self, btn: QPushButton, enabled: bool):
        c  = "#27ae60" if enabled else "#e74c3c"
        hc = "#229954" if enabled else "#c0392b"
        btn.setStyleSheet(
            f"QPushButton {{ background: {c}; color: #fff; border: none; "
            f"border-radius: 4px; padding: 6px 12px; font-weight: bold; }}"
            f"QPushButton:hover {{ background: {hc}; }}"
        )

    def _toggle_ad_blocker(self, btn: QPushButton):
        self._ad_blocker.enabled = not self._ad_blocker.enabled
        state = "Açık" if self._ad_blocker.enabled else "Kapalı"
        btn.setText(state)
        self._apply_toggle_style(btn, self._ad_blocker.enabled)
        self.status.showMessage(f"🚫 Reklam Bloker {state}", 2000)

    def _toggle_smooth_scroll(self, btn: QPushButton):
        self._smooth_scroll = not self._smooth_scroll
        state = "Açık" if self._smooth_scroll else "Kapalı"
        btn.setText(state)
        self._apply_toggle_style(btn, self._smooth_scroll)
        self.status.showMessage(f"🎯 Smooth Scroll {state} (Yeni sekmelerde geçerli)", 2000)

    def _toggle_dark_mode(self, btn: QPushButton):
        self._dark_mode = not self._dark_mode
        state = "Açık" if self._dark_mode else "Kapalı"
        btn.setText(state)
        self._apply_toggle_style(btn, self._dark_mode)
        self.status.showMessage(f"🌙 Auto Dark Mode {state} (Yeni sekmelerde geçerli)", 2000)

    def _toggle_session_recovery(self, btn: QPushButton):
        self._restore_session = not self._restore_session
        state = "Açık" if self._restore_session else "Kapalı"
        btn.setText(state)
        self._apply_toggle_style(btn, self._restore_session)
        self.status.showMessage(f"💾 Session Recovery {state}", 2000)

    def _clear_all_history(self):
        self._history = []
        self._downloads = []
        save(HIST_FILE, self._history)
        save(DL_FILE,   self._downloads)
        self.status.showMessage("✓ Geçmiş ve indirilenler temizlendi", 2000)

    # ══════════════════════════════════════════════════════════════════════
    # Panel ortak
    # ══════════════════════════════════════════════════════════════════════

    def _close_panel(self):
        self._panel.hide_panel()
        self._panel_visible = False

    def _panel_item_clicked(self, item):
        url = item.data(Qt.UserRole)
        if url:
            self._open_url(url)

    def _clear_panel(self):
        title = self._panel.title
        if title == "Geçmiş":
            self._history = []
            save(HIST_FILE, self._history)
        elif title == "İndirilenler":
            self._downloads = []
            save(DL_FILE, self._downloads)
        self._panel.list_widget.clear()

    # ══════════════════════════════════════════════════════════════════════
    # İzinler & İndirmeler
    # ══════════════════════════════════════════════════════════════════════

    def _handle_permission(self, permission: QWebEnginePermission):
        P = QWebEnginePermission.PermissionType
        granted = [
            P.MediaAudioCapture, P.MediaVideoCapture, P.MediaAudioVideoCapture,
            P.Notifications, P.Geolocation, P.ClipboardReadWrite,
        ]
        names = {
            P.MediaAudioCapture:      "🎤 Mikrofon",
            P.MediaVideoCapture:      "📷 Kamera",
            P.MediaAudioVideoCapture: "🎤📷 Mikrofon+Kamera",
            P.Notifications:          "🔔 Bildirim",
            P.Geolocation:            "📍 Konum",
            P.ClipboardReadWrite:     "📋 Pano",
        }
        ptype = permission.permissionType()
        if ptype in granted:
            permission.grant()
            label = names.get(ptype, "İzin")
            host  = permission.origin().host() or "sayfa"
            self.status.showMessage(f"✓ {host} → {label} izni verildi", 3000)
        else:
            permission.deny()

    def _handle_download(self, dl: QWebEngineDownloadRequest):
        import os
        dl_dir = os.path.expanduser("~/Downloads")
        if not os.path.exists(dl_dir):
            dl_dir = os.path.expanduser("~")
        path = os.path.join(dl_dir, dl.suggestedFileName())
        dl.setDownloadDirectory(dl_dir)
        dl.setDownloadFileName(dl.suggestedFileName())
        dl.accept()
        name = dl.suggestedFileName()
        self._dl_label.setText(f"⬇  İndiriliyor: {name}")
        self._dl_bar.setVisible(True)

        def on_finish():
            record = {
                "name": name,
                "path": path,
                "time": datetime.now().strftime("%d.%m.%Y %H:%M"),
            }
            self._downloads.insert(0, record)
            save(DL_FILE, self._downloads)
            self._dl_label.setText(f"✓  İndirildi: {name}")
            QTimer.singleShot(4000, lambda: self._dl_bar.setVisible(False))

        dl.isFinishedChanged.connect(lambda: on_finish() if dl.isFinished() else None)

    # ══════════════════════════════════════════════════════════════════════
    # Sekme bağlam menüsü
    # ══════════════════════════════════════════════════════════════════════

    def _tab_context_menu(self, pos, idx: int):
        menu = QMenu(self)
        menu.setStyleSheet(MENU_STYLE)
        color_menu = menu.addMenu("🎨  Grup rengi")
        color_menu.setStyleSheet(MENU_STYLE)
        for name, (bg, _) in TAB_COLORS.items():
            label = f"{'●  ' if bg else '○  '}{name.capitalize()}"
            act = color_menu.addAction(label)
            act.setData(name)
        dup_act   = menu.addAction("⧉  Kopyala")
        menu.addSeparator()
        close_act = menu.addAction("✕  Kapat")

        action = menu.exec(QCursor.pos())
        if not action:
            return
        if action == close_act:
            self._close(idx)
        elif action == dup_act:
            self._new_tab(self._tabs[idx][1].url)
        elif action.data() in TAB_COLORS:
            self._tabs[idx][0].set_color(action.data())

    # ══════════════════════════════════════════════════════════════════════
    # Sekme yönetimi
    # ══════════════════════════════════════════════════════════════════════

    def _new_tab(self, url=None):
        idx  = len(self._tabs)
        page = BrowserPage(
            url or self.HOME,
            smooth_scroll=self._smooth_scroll,
            dark_mode=self._dark_mode,
        )
        tw = TabWidget(
            on_click=lambda chk=False, i=idx: self._switch(i),
            on_close=lambda chk=False, i=idx: self._close(i),
            on_right_click=lambda pos, i=idx: self._tab_context_menu(pos, i),
        )
        self._tl.insertWidget(self._tl.count() - 2, tw)
        self.stack.addWidget(page)
        self._tabs.append((tw, page))

        page.view.titleChanged.connect(lambda t, i=idx: self._on_title(t, i))
        page.view.urlChanged.connect(lambda u, i=idx: self._on_url(u, i))
        page.view.loadProgress.connect(self._on_progress)
        page.view.loadFinished.connect(self._on_finish)
        page.view.page().linkHovered.connect(self.status.showMessage)
        page.view.page().profile().downloadRequested.connect(self._handle_download)
        page.view.page().permissionRequested.connect(self._handle_permission)
        self._switch(idx)

    def _switch(self, idx: int):
        if not (0 <= idx < len(self._tabs)):
            return
        if 0 <= self._active < len(self._tabs):
            self._tabs[self._active][0].set_active(False)
        self._active = idx
        self._tabs[idx][0].set_active(True)
        self.stack.setCurrentWidget(self._tabs[idx][1])
        self.url_bar.setText(self._tabs[idx][1].url)

    def _close(self, idx: int):
        if len(self._tabs) <= 1:
            self._tabs[0][1].view.load(QUrl(self.HOME))
            return
        tw, page = self._tabs.pop(idx)
        self._tl.removeWidget(tw)
        tw.deleteLater()
        self.stack.removeWidget(page)
        page.deleteLater()
        self._rewire()
        self._active = -1
        self._switch(min(idx, len(self._tabs) - 1))

    def _rewire(self):
        for i, (tw, _) in enumerate(self._tabs):
            for sig, slot in [
                (tw.btn.clicked,                      lambda chk=False, i=i: self._switch(i)),
                (tw.close_btn.clicked,                lambda chk=False, i=i: self._close(i)),
                (tw.btn.customContextMenuRequested,   lambda pos, i=i: self._tab_context_menu(pos, i)),
            ]:
                try:
                    sig.disconnect()
                except Exception:
                    pass
                sig.connect(slot)

    def _close_current(self):
        self._close(self._active)

    def _cur(self):
        return self._tabs[self._active][1] if 0 <= self._active < len(self._tabs) else None

    # ══════════════════════════════════════════════════════════════════════
    # Olaylar
    # ══════════════════════════════════════════════════════════════════════

    def _on_title(self, t: str, idx: int):
        if idx < len(self._tabs):
            self._tabs[idx][0].set_title(t)
        if idx == self._active:
            self.setWindowTitle(f"{t} — SwiftX")

    def _on_url(self, u, idx: int):
        if idx == self._active:
            self.url_bar.setText(u.toString())

    def _on_progress(self, v: int):
        self.progress.setVisible(v < 100)
        self.progress.setValue(v)

    def _on_finish(self, ok: bool):
        self.progress.setVisible(False)
        if not ok:
            self.status.showMessage("Sayfa yüklenemedi.", 3000)
            return
        p = self._cur()
        if p:
            self._add_history(p.title, p.url)

    # ══════════════════════════════════════════════════════════════════════
    # Gezinti
    # ══════════════════════════════════════════════════════════════════════

    def _navigate(self):
        t = self.url_bar.text().strip()
        if not t:
            return
        if t.startswith(("http://", "https://", "file://")):
            url = t
        elif "." in t and " " not in t:
            url = "https://" + t
        else:
            url = "https://www.google.com/search?q=" + t.replace(" ", "+")
        if p := self._cur():
            p.view.load(QUrl(url))

    def _open_url(self, url: str):
        if p := self._cur():
            p.view.load(QUrl(url))

    def _go_back(self):
        if p := self._cur(): p.view.back()

    def _go_forward(self):
        if p := self._cur(): p.view.forward()

    def _reload(self):
        if p := self._cur(): p.view.reload()

    def _go_home(self):
        if p := self._cur(): p.view.load(QUrl(self.HOME))

    def _focus_url(self):
        self.url_bar.setFocus()
        self.url_bar.selectAll()
