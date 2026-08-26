"""
core/constants.py
Uygulama genelinde kullanılan sabitler ve yapılandırma değerleri.
"""

import os
import sys
from typing import Dict, List, Tuple

# Uygulama Sürümü
VERSION = "0.29"

SIDEBAR_W = 48


def get_base_data_dir() -> str:
    """
    Uygulamanın çalıştırılma türüne göre (Portable / PyInstaller / Standard Linux)
    doğru veri dizinini döndürür.
    """
    # PyInstaller ile derlenmişse executable dizinini al
    if getattr(sys, "frozen", False):
        base_path = os.path.dirname(sys.executable)
        return os.path.join(base_path, "profile")

    # Standart çalıştırmada XDG standartlarına uy
    xdg_data = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
    return os.path.join(xdg_data, "swiftx-browser")


DATA_DIR = get_base_data_dir()

# Dizin yoksa otomatik oluştur
os.makedirs(DATA_DIR, exist_ok=True)

BM_FILE = os.path.join(DATA_DIR, "bookmarks.json")
HIST_FILE = os.path.join(DATA_DIR, "history.json")
DL_FILE = os.path.join(DATA_DIR, "downloads.json")
SESSION_FILE = os.path.join(DATA_DIR, "session.json")
EXTENSIONS_FILE = os.path.join(DATA_DIR, "extensions.json")

TAB_COLORS: Dict[str, Tuple[str, str]] = {
    "none": ("", ""),
    "kırmızı": ("#e74c3c", "#fff"),
    "turuncu": ("#e67e22", "#fff"),
    "sarı": ("#f1c40f", "#222"),
    "yeşil": ("#27ae60", "#fff"),
    "mavi": ("#3498db", "#fff"),
    "mor": ("#9b59b6", "#fff"),
}

AD_BLOCK_PATTERNS: List[str] = [
    "google.com/ads",
    "doubleclick.net",
    "pagead",
    "adsbygoogle",
    "ads.google",
    "googleadservices.com",
    "facebook.com/tr",
    "analytics.google.com",
    "youtube.com/api/stats",
    "amazon-adsystem.com",
    "criteo.com",
    "moatpixel.com",
    "rubiconproject.com",
    "pubmatic.com",
    "gumgum.com",
]

DEFAULT_EXTENSIONS: List[dict] = [
    {
        "id": "dark_reader",
        "name": "Dark Reader",
        "desc": "Web sayfalarına dark mode uygula",
        "icon": "🌙",
        "enabled": False,
        "version": "1.0.0",
    },
    {
        "id": "no_ads",
        "name": "No Ads",
        "desc": "Reklam ve izleme engelle",
        "icon": "🚫",
        "enabled": True,
        "version": "2.1.0",
    },
    {
        "id": "speedup",
        "name": "Page Speed",
        "desc": "Sayfa yüklemesini hızlandır",
        "icon": "⚡",
        "enabled": False,
        "version": "1.5.2",
    },
    {
        "id": "privacy",
        "name": "Privacy Guard",
        "desc": "İzleme ve profil oluşturmayı engelle",
        "icon": "🔒",
        "enabled": True,
        "version": "3.0.1",
    },
    {
        "id": "readmode",
        "name": "Read Mode",
        "desc": "Makale modunda okumayı etkinleştir",
        "icon": "📖",
        "enabled": False,
        "version": "1.2.0",
    },
]