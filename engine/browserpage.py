"""
engine/browser_page.py
Web sayfası widget'ı ve smooth scroll motoru.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings, QWebEngineScript, QWebEnginePermission
from PySide6.QtCore import QUrl, Qt, QTimer, QObject
from PySide6.QtGui import QWheelEvent

from engine.scripts import KEYBOARD_SCROLL_JS, AUTO_DARK_MODE_JS


class SmoothScroller(QObject):
    """60 fps smooth scroll — QWebEngineView.page().runJavaScript ile senkron."""

    PIXELS   = 220
    FRICTION = 0.82
    MIN_VEL  = 0.5

    def __init__(self, view: QWebEngineView):
        super().__init__(view)
        self._view  = view
        self._vel   = 0.0
        self._timer = QTimer(self)
        self._timer.setInterval(8)
        self._timer.timeout.connect(self._step)
        view.installEventFilter(self)

    def eventFilter(self, obj, event):
        if isinstance(event, QWheelEvent):
            if event.buttons() & Qt.MiddleButton or event.modifiers() & Qt.ControlModifier:
                return False
            delta = event.angleDelta().y()
            if delta == 0:
                return False
            self._vel += -(delta / 120.0) * self.PIXELS
            if not self._timer.isActive():
                self._timer.start()
            return True
        return False

    def _step(self):
        if abs(self._vel) < self.MIN_VEL:
            self._vel = 0.0
            self._timer.stop()
            return
        move = self._vel
        self._vel *= self.FRICTION
        self._view.page().runJavaScript(f"window.scrollBy(0, {move:.3f});")


class BrowserPage(QWidget):
    """Tek bir sekmeye karşılık gelen web görünümü."""

    def __init__(self, url: str = "", smooth_scroll: bool = True, dark_mode: bool = True):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.view = QWebEngineView()
        s = self.view.settings()
        s.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        s.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        s.setAttribute(QWebEngineSettings.WebAttribute.ScreenCaptureEnabled, True)
        s.setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)
        s.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)

        # YouTube gibi sitelerde script'leri devre dışı bırak (çakışma önlemek için)
        is_youtube = url and ('youtube.com' in url or 'youtu.be' in url)

        if smooth_scroll and not is_youtube:
            self._inject_script(
                name="swiftx_smooth_scroll",
                source=KEYBOARD_SCROLL_JS,
                point=QWebEngineScript.InjectionPoint.DocumentReady,
                sub_frames=False,
            )

        if dark_mode and not is_youtube:
            self._inject_script(
                name="swiftx_dark_mode",
                source=AUTO_DARK_MODE_JS,
                point=QWebEngineScript.InjectionPoint.DocumentCreation,
                sub_frames=True,
            )

        if url:
            self.view.load(QUrl(url))

        layout.addWidget(self.view)

        if smooth_scroll:
            self.scroller = SmoothScroller(self.view)

        # Mikrofon ve kamera izinleri için
        self.view.page().permissionRequested.connect(self._handle_permission)

    # ── Yardımcılar ────────────────────────────────────────────────────────

    def _handle_permission(self, permission):
        # Mikrofon, kamera vb. izinleri otomatik kabul et
        if permission.permissionType() in [
            QWebEnginePermission.PermissionType.MediaAudioCapture,
            QWebEnginePermission.PermissionType.MediaVideoCapture,
            QWebEnginePermission.PermissionType.MediaAudioVideoCapture,
        ]:
            permission.grant()
        else:
            permission.deny()

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

    # ── Properties ─────────────────────────────────────────────────────────

    @property
    def title(self) -> str:
        return self.view.title() or "Yeni Sekme"

    @property
    def url(self) -> str:
        return self.view.url().toString()
