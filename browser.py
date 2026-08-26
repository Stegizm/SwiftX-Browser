v"""
browser.py
SwiftX Browser v0.29 — giriş noktası.

Kullanım:
    python browser.py
"""
import sys
import os
import re

# Uygulama dondurulmuş (frozen) olsa da olmasa da kök dizini ekleyelim
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# PyInstaller'ın özel _internal dizinini de ekleyelim
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
    if base_path not in sys.path:
        sys.path.append(base_path)

__version__ = "0.29"

from PySide6.QtWidgets import QApplication
from PySide6.QtWebEngineCore import QWebEngineProfile

from windows.main_window import MainWindow


def _get_data_path() -> str:
    """Kalıcı veri dizini: çerezler, cache, localStorage vb."""
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
        return os.path.join(base, "profile")
    # Geliştirme modunda XDG standardını kullan
    xdg_data = os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))
    return os.path.join(xdg_data, 'swiftx-browser')


def main():
    # ── Kalıcı veri dizinini oluştur ──
    data_path = _get_data_path()
    os.makedirs(data_path, exist_ok=True)
    print(f"[SwiftX] Veri dizini: {data_path}")

    # ── Wayland tespiti ──
    is_wayland = os.environ.get('WAYLAND_DISPLAY') or os.environ.get('XDG_SESSION_TYPE') == 'wayland'

    flags = [
        # ── Medya ──
        "--enable-features=HardwareMediaKeyHandling,MediaSessionService",
        "--disable-features=PreloadMediaEngagementData",
        # ── Çerez & Site Verileri ──
        "--enable-features=NetworkService,SandboxTracking",
        # ── Performans ──
        "--disable-logging",
        "--log-level=3",
        "--num-raster-threads=4",
        "--dns-prefetch-enable",
    ]

    if is_wayland:
        # Wayland + Intel GPU: GPU'yu tamamen kapat
        # Video yazılımsal decode ile çalışır, WebGL crash önlenir
        flags.append("--disable-gpu")
        print("[SwiftX] Wayland tespit edildi, GPU devre dışı (stabil)")
    else:
        flags.append("--enable-accelerated-video-decode")
        flags.append("--enable-gpu-rasterization")

    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = " ".join(flags) + " "

    app = QApplication(sys.argv)
    app.setApplicationName("SwiftX Browser")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("YD Studio")

    # ── Web Engine Profili ───────────────────────────────────────────
    profile = QWebEngineProfile.defaultProfile()

    # Kalıcı depolama yolu — çerezler, localStorage, IndexedDB, cache
    profile.setPersistentStoragePath(data_path)
    profile.setCachePath(os.path.join(data_path, "cache"))

    # Çerez politikası — kalıcı + üçüncü taraf çerezlere izin ver
    profile.setPersistentCookiesPolicy(
        QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies
    )
    try:
        profile.setThirdPartyCookiePolicy(
            QWebEngineProfile.ThirdPartyCookiePolicy.AllowThirdPartyCookies
        )
    except Exception:
        pass

    # Gerçek Chromium sürümünü algıla ve UA'i buna göre ayarla
    real_ua = profile.httpUserAgent()
    chrome_ver = "120.0.0.0"
    m = re.search(r'Chrome/([\d.]+)', real_ua)
    if m:
        chrome_ver = m.group(1)
    profile.setHttpUserAgent(
        f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        f"(KHTML, like Gecko) Chrome/{chrome_ver} Safari/537.36"
    )
    print(f"[SwiftX] Chromium: {chrome_ver}")

    MainWindow().show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()