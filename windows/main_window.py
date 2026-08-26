# windows/main_window.py
# Ana pencere — sadece bileşenleri koordine eder.
# İş mantığı core.services'a, UI bileşenleri ui/ modüllerine taşındı.
import os
import sys
import time
from datetime import datetime

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QProgressBar, QStackedWidget,
    QStatusBar, QMenu, QListWidgetItem,
    QSizePolicy, QLabel,
)
from PySide6.QtWebEngineCore import (
    QWebEnginePermission, QWebEngineProfile,
)
from PySide6.QtCore import QUrl, Qt, QTimer
from PySide6.QtGui import QAction, QCursor

from core.constants import TAB_COLORS
from core.storage import load, save
from core.styles import STYLE, MENU_STYLE
from core.services.bookmark_manager import BookmarkManager
from core.services.history_manager import HistoryManager
from core.services.download_manager import DownloadManager
from core.services.settings_manager import SettingsManager
from engine.ad_blocker import AdBlocker
from engine.browserpage import BrowserPage
from ui.tab_bar import TabBar, HIBERNATE_HTML
from ui.extension_store import ExtensionStore
from ui.side_panel import SidePanel
from ui.sidebar import SidebarWidget
from ui.settings_panel import SettingsPanelWidget
from ui.bookmark_bar import BookmarkBar


# ── Sekme uyutma sabitleri ─────────────────────────────────────────────────
HIBERNATE_CHECK_INTERVAL = 30_000   # 30 saniyede bir kontrol
HIBERNATE_IDLE_SECONDS = 300        # 5 dakika hiç dokunulmazsa uyut
MIN_ACTIVE_TABS = 1                  # En az bu kadar sekme her zaman uyanık kalır


class MainWindow(QMainWindow):
    """Koordinatör pencere — iş mantığı delegasyonda."""

    def __init__(self):
        super().__init__()

        self.HOME = self._resolve_home()

        # ── Servisler ──────────────────────────────────────────────────────
        self._settings = SettingsManager()
        self._bookmarks = BookmarkManager()
        self._history = HistoryManager()
        self._downloads = DownloadManager(parent=self)
        self._ad_blocker = AdBlocker()
        self._ad_blocker.enabled = self._settings.ad_blocker_enabled

        # Servis sinyallerini bağla
        self._bookmarks.set_on_changed(self._on_bookmarks_changed)
        self._downloads.set_on_started(self._on_download_started)
        self._downloads.set_on_finished(self._on_download_finished)
        self._settings.set_on_changed(self._on_setting_changed)

        # ── Web Engine profili ────────────────────────────────────────────
        # Not: Profile ayarları browser.py'de yapılıyor (depolama yolu, çerez, cache)

        # ── Pencere temel ayarları ────────────────────────────────────────
        self.setWindowTitle("SwiftX")
        _here = self._data_dir()
        self.setWindowIcon(
            self.style().standardIcon(
                getattr(self.style(), "SP_ComputerIcon", 16)
            )
            if not os.path.exists(os.path.join(_here, "SXBETALOGO3.png"))
            else self._load_icon(os.path.join(_here, "SXBETALOGO3.png"))
        )
        self.resize(1360, 860)
        self.setStyleSheet(STYLE)

        # ── Sekme durumu ─────────────────────────────────────────────────
        self._tabs: list[tuple[object, BrowserPage]] = []  # (TabItem, BrowserPage)
        self._tab_last_active: dict[int, float] = {}       # idx → son aktif zamanı
        self._hibernated_tabs: set[int] = set()            # uyutulmuş sekme index'leri
        self._active: int = -1
        self._panel_visible = False

        self._build_ui()
        self._load_session()

        # ── Sekme uyutma zamanlayıcı ──────────────────────────────────────
        self._hibernate_timer = QTimer(self)
        self._hibernate_timer.setInterval(HIBERNATE_CHECK_INTERVAL)
        self._hibernate_timer.timeout.connect(self._check_hibernation)
        self._hibernate_timer.start()

    # ══════════════════════════════════════════════════════════════════════
    # Yardımcılar
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
        root = os.path.dirname(base)
        candidate = os.path.join(root, "data")
        return candidate if os.path.isdir(candidate) else root

    def _resolve_home(self) -> str:
        _here = self._data_dir()
        html = os.path.join(_here, "home (v6).html")
        if os.path.exists(html):
            path = html.replace("\\", "/")
            if not path.startswith("/"):
                path = "/" + path
            return "file://" + path
        return "https://www.startpage.com"

    def _load_icon(self, path: str):
        from PySide6.QtGui import QIcon
        return QIcon(path)

    # ══════════════════════════════════════════════════════════════════════
    # UI İnşası
    # ══════════════════════════════════════════════════════════════════════

    def _build_ui(self):
        root = QWidget()
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

    # ── Sidebar (delege) ──────────────────────────────────────────────────

    def _build_sidebar(self) -> SidebarWidget:
        self._sidebar = SidebarWidget(
            on_home=self._go_home,
            on_extensions=self._open_extensions,
            on_settings=self._toggle_settings,
            on_toggle=self._toggle_sidebar,
        )
        return self._sidebar

    # ── Orta alan ─────────────────────────────────────────────────────────

    def _build_center(self) -> QWidget:
        mid = QWidget()
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
        """Geleneksel sekme çubuğu: sol tarafta toggle, ortada kaydırılabilir sekmeler, sonda '+' butonu."""
        tab_strip = QWidget()
        tab_strip.setObjectName("tabStrip")
        strip_h = QHBoxLayout(tab_strip)
        strip_h.setContentsMargins(0, 0, 0, 0)
        strip_h.setSpacing(0)

        # Sol: Sidebar toggle
        self._toggle_btn = QPushButton("☰")
        self._toggle_btn.setObjectName("toggleBtn")
        self._toggle_btn.setToolTip("Sidebar Aç/Kapat (Ctrl+B)")
        self._toggle_btn.clicked.connect(self._toggle_sidebar)
        strip_h.addWidget(self._toggle_btn)

        # Orta: Yeni TabBar widget
        self._tab_bar = TabBar()
        self._tab_bar.new_tab_requested.connect(self._new_tab)
        self._tab_bar.tab_close_requested.connect(self._close)
        self._tab_bar.tab_switch_requested.connect(self._switch)
        self._tab_bar.tab_context_requested.connect(self._tab_context_menu)
        strip_h.addWidget(self._tab_bar)

        return tab_strip

    def _build_nav_bar(self) -> QWidget:
        nav_bar = QWidget()
        nav_bar.setObjectName("navBar")
        nav_h = QHBoxLayout(nav_bar)
        nav_h.setContentsMargins(8, 6, 8, 6)
        nav_h.setSpacing(4)

        self.btn_back = self._nav_btn("←")
        self.btn_forward = self._nav_btn("→")
        self.btn_reload = self._nav_btn("↻")

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

    # ── Bookmark bar (delege) ────────────────────────────────────────────

    def _build_bookmark_bar(self) -> BookmarkBar:
        self._bm_bar = BookmarkBar(
            on_click=self._open_url,
            on_remove=self._bookmarks.remove,
            on_add=self._add_bookmark,
        )
        self._bm_bar.refresh(self._bookmarks.bookmarks)
        return self._bm_bar

    # ── Download bar ─────────────────────────────────────────────────────

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

    # ── Sağ Panel (delege) ───────────────────────────────────────────────

    def _build_panel(self) -> SidePanel:
        self._panel = SidePanel(
            on_close=self._close_panel,
            on_clear=self._clear_panel,
        )
        self._panel.list_widget.itemDoubleClicked.connect(self._panel_item_clicked)
        self._panel.setVisible(False)

        # Ayarlar widget'ı
        self._settings_widget = SettingsPanelWidget(
            settings=self._settings,
            on_toggle=self._on_setting_toggle,
            on_clear_history=self._clear_all_history,
        )

        return self._panel

    # ── Kısayollar ──────────────────────────────────────────────────────

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
            ("F11",        self._toggle_fullscreen),
        ]
        for key, fn in shortcuts:
            a = QAction(self)
            a.setShortcut(key)
            a.triggered.connect(fn)
            self.addAction(a)

    def _toggle_fullscreen(self):
        # Video tam ekrandaysa F11 ile karışmasın
        p = self._cur()
        if p and p.in_video_fullscreen:
            return
        if self.isFullScreen():
            self.showNormal()
            self.status.showMessage("Tam ekrandan çıkıldı", 1500)
        else:
            self.showFullScreen()
            self.status.showMessage("Tam ekran modu (F11 ile çık)", 1500)

    # ══════════════════════════════════════════════════════════════════════
    # Servis callback'leri
    # ══════════════════════════════════════════════════════════════════════

    def _on_bookmarks_changed(self, bookmarks: list[dict]) -> None:
        self._bm_bar.refresh(bookmarks)

    def _on_download_started(self, name: str) -> None:
        self._dl_label.setText(f"⬇  İndiriliyor: {name}")
        self._dl_bar.setVisible(True)

    def _on_download_finished(self, name: str) -> None:
        self._dl_label.setText(f"✓  İndirildi: {name}")
        QTimer.singleShot(4000, lambda: self._dl_bar.setVisible(False))

    def _on_setting_changed(self, attr_name: str, value: bool) -> None:
        """SettingsManager'dan gelen değişiklik — ayarlar paneli + ad blocker güncelle."""
        self._settings_widget.update_toggle_btn(attr_name, value)
        if attr_name == "ad_blocker_enabled":
            self._ad_blocker.enabled = value
            state = "Açık" if value else "Kapalı"
            self.status.showMessage(f"🚫 Reklam Bloker {state}", 2000)
        elif attr_name == "smooth_scroll":
            state = "Açık" if value else "Kapalı"
            self.status.showMessage(f"🎯 Smooth Scroll {state} (Yeni sekmelerde geçerli)", 2000)
        elif attr_name == "dark_mode":
            state = "Açık" if value else "Kapalı"
            self.status.showMessage(f"🌙 Auto Dark Mode {state} (Yeni sekmelerde geçerli)", 2000)
        elif attr_name == "restore_session":
            state = "Açık" if value else "Kapalı"
            self.status.showMessage(f"💾 Session Recovery {state}", 2000)
        elif attr_name == "tab_hibernate":
            state = "Açık" if value else "Kapalı"
            if value:
                self._hibernate_timer.start()
            else:
                self._hibernate_timer.stop()
                self._wake_all_tabs()
            self.status.showMessage(f"💤 Sekme Uyutma {state}", 2000)

    def _on_setting_toggle(self, attr_name: str) -> None:
        """SettingsPanelWidget'dan butona basılınca çağrılır."""
        self._settings.toggle(attr_name)

    # ══════════════════════════════════════════════════════════════════════
    # Sekme uyutma (hibernation) sistemi
    # ══════════════════════════════════════════════════════════════════════

    def _check_hibernation(self):
        """Zamanlayıcıdan çağrılır — uyutulması gereken sekmeleri kontrol et."""
        if not self._settings.tab_hibernate:
            return
        now = time.monotonic()
        for idx in range(len(self._tabs)):
            if idx == self._active:
                self._tab_last_active[idx] = now
                continue
            if idx in self._hibernated_tabs:
                continue
            last = self._tab_last_active.get(idx, now)
            if now - last >= HIBERNATE_IDLE_SECONDS:
                self._hibernate_tab(idx)

    def _hibernate_tab(self, idx: int):
        """Belirtilen sekmeyi uyut — hafıza tasarrufu sağla."""
        if idx == self._active or idx in self._hibernated_tabs:
            return
        if idx < 0 or idx >= len(self._tabs):
            return

        _, page = self._tabs[idx]
        # Gerçek URL'yi kaydet (home page değilse)
        saved_url = page.url
        saved_title = page.title
        if not saved_url or saved_url == "about:blank":
            return

        # Hafif HTML yükle — ağır sayfa serbest bırakılır
        page.view.setHtml(HIBERNATE_HTML, QUrl(saved_url))
        page._hibernated_url = saved_url
        page._hibernated_title = saved_title

        self._hibernated_tabs.add(idx)
        tab_item = self._tab_bar.get_item(idx)
        if tab_item:
            tab_item.set_hibernated(True)

    def _wake_tab(self, idx: int):
        """Uyutulmuş sekmeyi uyandır — orijinal sayfayı yeniden yükle."""
        if idx not in self._hibernated_tabs:
            return
        if idx < 0 or idx >= len(self._tabs):
            return

        _, page = self._tabs[idx]
        url = getattr(page, '_hibernated_url', '')
        if url:
            page.view.load(QUrl(url))
        del page._hibernated_url
        del page._hibernated_title

        self._hibernated_tabs.discard(idx)
        tab_item = self._tab_bar.get_item(idx)
        if tab_item:
            tab_item.set_hibernated(False)

    def _wake_all_tabs(self):
        """Tüm uyutulmuş sekmeleri uyandır."""
        for idx in list(self._hibernated_tabs):
            self._wake_tab(idx)

    # ══════════════════════════════════════════════════════════════════════
    # Oturum yönetimi
    # ══════════════════════════════════════════════════════════════════════

    def _save_session(self):
        from core.constants import SESSION_FILE
        session = {
            "tabs": [
                {"url": t[1].url, "title": t[1].title}
                for t in self._tabs if t[1].url != self.HOME
            ],
            "active": self._active,
        }
        save(SESSION_FILE, session)

    def _load_session(self):
        from core.constants import SESSION_FILE
        if not self._settings.restore_session:
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
    # Sidebar (delege)
    # ══════════════════════════════════════════════════════════════════════

    def _toggle_sidebar(self):
        is_open = self._sidebar.toggle()
        self._toggle_btn.setText("☰" if is_open else "▶")

    # ══════════════════════════════════════════════════════════════════════
    # Eklenti merkezi
    # ══════════════════════════════════════════════════════════════════════

    def _open_extensions(self):
        dialog = ExtensionStore(self._settings.extensions, self)
        if dialog.exec():
            self._settings.apply_extension_changes(dialog.changes)
            active = self._settings.active_extension_count
            total = self._settings.total_extension_count
            self.status.showMessage(
                f"✓ {active} eklenti aktif, {total - active} devre dışı", 3000
            )

    # ══════════════════════════════════════════════════════════════════════
    # Yer imleri (delege)
    # ══════════════════════════════════════════════════════════════════════

    def _add_bookmark(self):
        p = self._cur()
        if not p:
            return
        url, title = p.url, p.title or p.url
        err = self._bookmarks.add(url, title)
        if err:
            self.status.showMessage(err, 2000)
            return
        self.btn_star.setText("★")
        QTimer.singleShot(1500, lambda: self.btn_star.setText("☆"))
        self.status.showMessage(f"'{title[:30]}' yer imlerine eklendi.", 2000)

    # ══════════════════════════════════════════════════════════════════════
    # Geçmiş paneli
    # ══════════════════════════════════════════════════════════════════════

    def _toggle_history(self):
        if self._panel_visible and self._panel.title == "Geçmiş":
            self._close_panel()
            return
        self._panel.list_widget.clear()
        for h in self._history.history:
            item = QListWidgetItem(f"  {h['time']}  —  {h['title'][:50]}")
            item.setData(Qt.UserRole, h["url"])
            self._panel.list_widget.addItem(item)
        self._panel.show_list("Geçmiş")
        self._panel_visible = True

    # ══════════════════════════════════════════════════════════════════════
    # İndirilenler paneli
    # ══════════════════════════════════════════════════════════════════════

    def _toggle_downloads(self):
        if self._panel_visible and self._panel.title == "İndirilenler":
            self._close_panel()
            return
        self._panel.list_widget.clear()
        for d in self._downloads.downloads:
            item = QListWidgetItem(f"  {d['time']}  —  {d['name']}")
            item.setData(Qt.UserRole, d.get("path", ""))
            self._panel.list_widget.addItem(item)
        self._panel.show_list("İndirilenler")
        self._panel_visible = True

    # ══════════════════════════════════════════════════════════════════════
    # Ayarlar paneli
    # ══════════════════════════════════════════════════════════════════════

    def _toggle_settings(self):
        if self._panel_visible and self._panel.title == "Ayarlar":
            self._close_panel()
            return
        self._panel.show_settings("Ayarlar", self._settings_widget)
        self._panel_visible = True

    def _clear_all_history(self):
        self._history.clear()
        self._downloads.clear()
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
            self._history.clear()
        elif title == "İndirilenler":
            self._downloads.clear()
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
            host = permission.origin().host() or "sayfa"
            self.status.showMessage(f"✓ {host} → {label} izni verildi", 3000)
        else:
            permission.deny()

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
        dup_act = menu.addAction("⧉  Kopyala")

        # Uyut/Uyanık sekmeyse menüye özel seçenek ekle
        wake_act = None
        if idx in self._hibernated_tabs:
            wake_act = menu.addAction("💤  Uyandır")
        else:
            menu.addAction("💤  Uyut").setData("__hibernate__")

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
        elif action == wake_act:
            self._wake_tab(idx)
        elif action.data() == "__hibernate__":
            self._hibernate_tab(idx)

    # ══════════════════════════════════════════════════════════════════════
    # Sekme yönetimi
    # ══════════════════════════════════════════════════════════════════════

    def _new_tab(self, url=None):
        idx = len(self._tabs)
        page = BrowserPage(
            url or self.HOME,
            smooth_scroll=self._settings.smooth_scroll,
            dark_mode=self._settings.dark_mode,
        )

        # TabBar'a yeni sekme ekle
        tab_item = self._tab_bar.add_tab(
            index=idx,
            on_click=self._switch,
            on_close=self._close,
            on_right_click=self._tab_context_menu,
        )

        self.stack.addWidget(page)
        self._tabs.append((tab_item, page))
        self._tab_last_active[idx] = time.monotonic()

        page.view.titleChanged.connect(lambda t, i=idx: self._on_title(t, i))
        page.view.urlChanged.connect(lambda u, i=idx: self._on_url(u, i))
        page.view.loadProgress.connect(self._on_progress)
        page.view.loadFinished.connect(self._on_finish)
        page.view.page().linkHovered.connect(self.status.showMessage)
        page.view.page().profile().downloadRequested.connect(self._downloads.handle_request)
        page.view.page().permissionRequested.connect(self._handle_permission)
        self._switch(idx)

    def _switch(self, idx: int):
        if not (0 <= idx < len(self._tabs)):
            return

        # Aktif sekmeyi güncelle
        self._tab_last_active[idx] = time.monotonic()

        # Uyutulmuş sekmeyi uyandır
        if idx in self._hibernated_tabs:
            self._wake_tab(idx)

        self._active = idx
        self._tab_bar.set_active(idx)
        self.stack.setCurrentWidget(self._tabs[idx][1])
        self.url_bar.setText(self._tabs[idx][1].url)
        self._tab_bar.scroll_to_tab(idx)

    def _close(self, idx: int):
        if len(self._tabs) <= 1:
            self._tabs[0][1].view.load(QUrl(self.HOME))
            return

        # Hibernation verilerini temizle
        self._hibernated_tabs.discard(idx)

        tab_item, page = self._tabs.pop(idx)
        self._tab_bar.remove_tab(idx)
        self.stack.removeWidget(page)
        page.deleteLater()

        # Index'leri yeniden düzenle
        self._tab_bar.rewire(
            on_click=self._switch,
            on_close=self._close,
            on_right_click=self._tab_context_menu,
        )
        self._tab_last_active = {i: self._tab_last_active.get(i + (1 if i >= idx else 0), time.monotonic())
                                 for i in range(len(self._tabs))}
        self._hibernated_tabs = {i - 1 if i > idx else i for i in self._hibernated_tabs if i != idx}

        self._active = -1
        self._switch(min(idx, len(self._tabs) - 1))

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
        # URL değiştiğinde uyutulmuşluktan çıkar
        self._hibernated_tabs.discard(idx)
        tab_item = self._tab_bar.get_item(idx)
        if tab_item:
            tab_item.set_hibernated(False)

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
            self._history.add(p.title, p.url)

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

    def keyPressEvent(self, event):
        """F11 ve Escape ile tam ekran kontrolü."""
        if event.key() == Qt.Key.Key_Escape and self.isFullScreen():
            self.showNormal()
        super().keyPressEvent(event)
