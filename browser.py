"""
browser.py
SwiftX Browser v0.28.1-2 — giriş noktası.

Kullanım:
    python browser.py
"""
import sys
import os

# Uygulama dondurulmuş (frozen) olsa da olmasa da kök dizini ekleyelim
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# PyInstaller'ın özel _internal dizinini de ekleyelim
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
    if base_path not in sys.path:
        sys.path.append(base_path)

__version__ = "0.28.1-2"

from PySide6.QtWidgets import QApplication
from PySide6.QtWebEngineCore import QWebEngineProfile

from windows.main_window import MainWindow


def main():
    # Wayland tespiti — GPU flag'lerini platforma göre ayarla
    is_wayland = os.environ.get('WAYLAND_DISPLAY') or os.environ.get('XDG_SESSION_TYPE') == 'wayland'

    flags = [
        # ── Medya ──
        "--enable-features=HardwareMediaKeyHandling,MediaSessionService",
        "--disable-features=PreloadMediaEngagementData",
        # ── Performans ──
        "--disable-logging",
        "--log-level=3",
        "--num-raster-threads=4",
        "--dns-prefetch-enable",
    ]

    # Wayland'de GPU context kaybını önlemek için ek flag'ler
    if is_wayland:
        flags.append("--enable-features=VizDisplayCompositor")
        flags.append("--ozone-platform-hint=auto")
        print("[SwiftX] Wayland tespit edildi, GPU flag'leri ayarlandı")
    else:
        flags.append("--enable-accelerated-video-decode")
        flags.append("--enable-gpu-rasterization")

    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = " ".join(flags) + " "

    app = QApplication(sys.argv)
    app.setApplicationName("SwiftX Browser")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("YD Studio")

    profile = QWebEngineProfile.defaultProfile()

    # Gerçek Chromium sürümünü algıla ve UA'i buna göre ayarla
    # YouTube, UA'daki Chrome sürümüne göre codec seçer — yanlış versiyon = oynatma hatası
    real_ua = profile.httpUserAgent()
    chrome_ver = "120.0.0.0"
    import re
    m = re.search(r'Chrome/([\d.]+)', real_ua)
    if m:
        chrome_ver = m.group(1)
    profile.setHttpUserAgent(
        f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        f"(KHTML, like Gecko) Chrome/{chrome_ver} Safari/537.36"
    )
    print(f"[SwiftX] Chromium: {chrome_ver}")

    profile.setPersistentCookiesPolicy(
        QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies
    )

    MainWindow().show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
