"""
browser.py
SwiftX Browser v0.28 — giriş noktası.

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

__version__ = "0.28.0"

from PySide6.QtWidgets import QApplication
from PySide6.QtWebEngineCore import QWebEngineProfile

from windows.main_window import MainWindow


def main():
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
        "--disable-gpu-sandbox "
        "--ignore-gpu-blacklist "
        "--enable-features=VizDisplayCompositor "
        "--disable-logging "
        "--log-level=3"
    )

    app = QApplication(sys.argv)
    app.setApplicationName("SwiftX Browser")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("YD Studio")

    profile = QWebEngineProfile.defaultProfile()
    profile.setHttpUserAgent(
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
    )
    profile.setPersistentCookiesPolicy(
        QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies
    )

    MainWindow().show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
