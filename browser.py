"""
browser.py
SwiftX Browser v0.2.9 - Entry Point
    python browser.py
"""
import os
import re
import sys

# ── Platform ve Ortam Ayarları (Importlardan ve QApplication'dan ÖNCE yapılmalı) ──
is_linux = sys.platform.startswith("linux")
is_wayland = os.environ.get('WAYLAND_DISPLAY') or os.environ.get('XDG_SESSION_TYPE') == 'wayland'

if is_linux:
    # Wayland eklentisi EGL crash verirse X11 (xcb) katmanına düşmesini sağla
    if is_wayland and "QT_QPA_PLATFORM" not in os.environ:
        os.environ["QT_QPA_PLATFORM"] = "xcb;wayland"
    
    # WebEngine Linux sandbox ve mesa çakışmalarını engelle
    os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"

# Uygulama kök dizinini ekle
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# PyInstaller internal dizini
if getattr(sys, 'frozen', False):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    if base_path not in sys.path:
        sys.path.append(base_path)

from core.constants import DATA_DIR, VERSION

from PySide6.QtWebEngineCore import QWebEngineProfile
from PySide6.QtWidgets import QApplication

from windows.main_window import MainWindow


def main():
    # ── Kalıcı veri dizinini oluştur ──
    data_path = DATA_DIR
    os.makedirs(data_path, exist_ok=True)
    print(f"[SwiftX] Veri dizini: {data_path}")

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

    if is_linux:
        # PyInstaller ile derlenmiş Linux sürümlerinde chroot/sandbox ve GPU crashlerini önle
        flags.append("--no-sandbox")
        flags.append("--disable-gpu-compositing")
        if not is_wayland:
            flags.append("--enable-accelerated-video-decode")
            flags.append("--enable-gpu-rasterization")
    else:
        # Windows bayrakları
        flags.append("--enable-accelerated-video-decode")
        flags.append("--enable-gpu-rasterization")

    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = " ".join(flags) + " "

    app = QApplication(sys.argv)
    app.setApplicationName("SwiftX Browser")
    app.setApplicationVersion(VERSION)
    app.setOrganizationName("YD Studio")

    # ── Web Engine Profili ───────────────────────────────────────────
    profile = QWebEngineProfile.defaultProfile()

    profile.setPersistentStoragePath(data_path)
    profile.setCachePath(os.path.join(data_path, "cache"))

    profile.setPersistentCookiesPolicy(
        QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies
    )
    try:
        profile.setThirdPartyCookiePolicy(
            QWebEngineProfile.ThirdPartyCookiePolicy.AllowThirdPartyCookies
        )
    except Exception:
        pass

    # Dinamik OS ve Chromium UA Tanımlaması
    real_ua = profile.httpUserAgent()
    chrome_ver = "120.0.0.0"
    m = re.search(r'Chrome/([\d.]+)', real_ua)
    if m:
        chrome_ver = m.group(1)
        
    system_os = "Windows NT 10.0; Win64; x64" if sys.platform == "win32" else "X11; Linux x86_64"
    profile.setHttpUserAgent(
        f"Mozilla/5.0 ({system_os}) AppleWebKit/537.36 "
        f"(KHTML, like Gecko) Chrome/{chrome_ver} Safari/537.36"
    )
    print(f"[SwiftX v{VERSION}] Chromium: {chrome_ver} | Platform: {sys.platform}")

    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()