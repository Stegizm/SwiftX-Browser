"""
engine/browserpage.py
Web sayfası widget'ı.

NOT: Bu dosya hem "engine.browser_page" hem de "engine.browserpage"
     olarak import edilebilir (engine/__init__.py alias).

v0.28.1-2: YouTube video düzeltmesi, fullscreen desteği, düzgün smooth scroll.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import (
    QWebEngineSettings, QWebEngineScript, QWebEngineFullScreenRequest,
)
from PySide6.QtCore import QUrl, Qt

from engine.scripts import SMOOTH_SCROLL_JS, KEYBOARD_SCROLL_JS, AUTO_DARK_MODE_JS


class BrowserPage(QWidget):
    """Tek bir sekmeye karşılık gelen web görünümü."""

    def __init__(self, url: str = "", smooth_scroll: bool = True, dark_mode: bool = True,
                 on_fullscreen_request=None):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.view = QWebEngineView()
        self._on_fullscreen_request = on_fullscreen_request
        self._in_video_fullscreen = False
        self._initial_url = url or ""

        s = self.view.settings()
        # ── Temel ──
        s.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        s.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        s.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)
        s.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
        # ── Video & Medya (YouTube düzeltmesi) ──
        s.setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)
        s.setAttribute(QWebEngineSettings.WebAttribute.ScreenCaptureEnabled, True)
        s.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)
        s.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
        s.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True)
        s.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        # ── Plugins (Flash vs. gelmiş geçmiş ama medya oynatıcılar için gerekli) ──
        try:
            s.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        except Exception:
            pass

        # ── Fullscreen sinyalini yakala ──
        self.view.page().fullScreenRequested.connect(self._handle_fullscreen)

        # ── Script enjeksiyonu: SADECE gerçek sayfalarda, about:blank HARIÇ ──
        is_real_page = url and not url.startswith(("about:", "data:"))
        is_youtube = url and ('youtube.com' in url or 'youtu.be' in url)

        if is_real_page:
            # Smooth scroll — wheel her yerde çalışır
            if smooth_scroll:
                self._inject_script(
                    name="swiftx_smooth_scroll",
                    source=SMOOTH_SCROLL_JS,
                    point=QWebEngineScript.InjectionPoint.DocumentReady,
                    sub_frames=False,
                )
                # Keyboard scroll YouTube hariç (Space videoyu duraklatır)
                if not is_youtube:
                    self._inject_script(
                        name="swiftx_keyboard_scroll",
                        source=KEYBOARD_SCROLL_JS,
                        point=QWebEngineScript.InjectionPoint.DocumentReady,
                        sub_frames=False,
                    )

            # Dark mode — YouTube hariç (YouTube'un kendi dark modu var)
            if dark_mode and not is_youtube:
                self._inject_script(
                    name="swiftx_dark_mode",
                    source=AUTO_DARK_MODE_JS,
                    point=QWebEngineScript.InjectionPoint.DocumentReady,
                    sub_frames=False,
                )

        # Sayfa yüklenince YouTube tespiti ve dinamik script enjeksiyonu
        self.view.urlChanged.connect(self._on_url_changed)

        if url:
            self.view.load(QUrl(url))

        layout.addWidget(self.view)

    def _on_url_changed(self, url):
        """URL değiştiğinde YouTube tespiti yap, gerekirse script enjekte et."""
        url_str = url.toString()
        if url_str.startswith(("about:", "data:")):
            return
        # Script zaten enjekte edildiyse tekrar yapma
        page_scripts = self.view.page().scripts()
        if page_scripts.find("swiftx_smooth_scroll"):
            return
        is_yt = 'youtube.com' in url_str or 'youtu.be' in url_str
        if self.view.settings().testAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled):
            self._inject_script(
                name="swiftx_smooth_scroll",
                source=SMOOTH_SCROLL_JS,
                point=QWebEngineScript.InjectionPoint.DocumentReady,
                sub_frames=False,
            )
            if not is_yt:
                self._inject_script(
                    name="swiftx_dark_mode",
                    source=AUTO_DARK_MODE_JS,
                    point=QWebEngineScript.InjectionPoint.DocumentReady,
                    sub_frames=False,
                )

    # ── Fullscreen yönetimi ─────────────────────────────────────────────

    def _handle_fullscreen(self, request: QWebEngineFullScreenRequest):
        """YouTube/Hulu vb. sitelerin tam ekran isteğini yönet."""
        main_win = self.window()
        if not main_win:
            request.reject()
            return

        if request.toggleOn():
            self._in_video_fullscreen = True
            main_win.showFullScreen()
            request.accept()
        else:
            self._in_video_fullscreen = False
            main_win.showNormal()
            request.accept()

    @property
    def in_video_fullscreen(self) -> bool:
        return self._in_video_fullscreen

    # ── Yardımcılar ─────────────────────────────────────────────────────

    def _inject_script(self, name: str, source: str,
                       point: QWebEngineScript.InjectionPoint,
                       sub_frames: bool) -> None:
        script = QWebEngineScript()
        script.setName(name)
        script.setSourceCode(source)
        script.setInjectionPoint(point)
        script.setRunsOnSubFrames(sub_frames)
        script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
        self.view.page().scripts().insert(script)

    # ── Properties ─────────────────────────────────────────────────────

    @property
    def title(self) -> str:
        return self.view.title() or "Yeni Sekme"

    @property
    def url(self) -> str:
        return self.view.url().toString()
