"""
browser.py
SwiftX Browser — giriş noktası.

Kullanım:
    python browser.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
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
    # AA_EnableHighDpiScaling deprecated (PySide6 6.11.0), modern QT otomatik şekilde handle eder
    app.setApplicationName("SwiftX Browser")

    profile = QWebEngineProfile.defaultProfile()
    profile.setHttpUserAgent(
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
    )
    profile.setPersistentCookiesPolicy(
        QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies
    )
    # PySide6 QWebEngineProfile'da setIgnoreSslErrors metodu yok.
    # SSL hata yönetimini özelleştirmek için QWebEnginePage.certificateError kullanmalısın.

    MainWindow().show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
