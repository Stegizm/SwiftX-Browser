"""
core/constants.py
Uygulama genelinde kullanılan sabitler ve yapılandırma değerleri.
"""

import os

SIDEBAR_W = 48
DATA_DIR  = os.path.expanduser("~/.swiftx")

BM_FILE         = os.path.join(DATA_DIR, "bookmarks.json")
HIST_FILE       = os.path.join(DATA_DIR, "history.json")
DL_FILE         = os.path.join(DATA_DIR, "downloads.json")
SESSION_FILE    = os.path.join(DATA_DIR, "session.json")
EXTENSIONS_FILE = os.path.join(DATA_DIR, "extensions.json")

TAB_COLORS = {
    "none":    ("", ""),
    "kırmızı": ("#e74c3c", "#fff"),
    "turuncu": ("#e67e22", "#fff"),
    "sarı":    ("#f1c40f", "#222"),
    "yeşil":   ("#27ae60", "#fff"),
    "mavi":    ("#3498db", "#fff"),
    "mor":     ("#9b59b6", "#fff"),
}

AD_BLOCK_PATTERNS = [
    "google.com/ads", "doubleclick.net", "pagead", "adsbygoogle",
    "ads.google", "googleadservices.com", "facebook.com/tr",
    "analytics.google.com", "youtube.com/api/stats",
    "amazon-adsystem.com", "criteo.com", "moatpixel.com",
    "rubiconproject.com", "pubmatic.com", "gumgum.com",
]

DEFAULT_EXTENSIONS = [
    {"id": "dark_reader", "name": "Dark Reader",    "desc": "Web sayfalarına dark mode uygula",       "icon": "🌙", "enabled": False, "version": "1.0.0"},
    {"id": "no_ads",      "name": "No Ads",          "desc": "Reklam ve izleme engelle",               "icon": "🚫", "enabled": True,  "version": "2.1.0"},
    {"id": "speedup",     "name": "Page Speed",      "desc": "Sayfa yüklemesini hızlandır",            "icon": "⚡", "enabled": False, "version": "1.5.2"},
    {"id": "privacy",     "name": "Privacy Guard",   "desc": "İzleme ve profil oluşturmayı engelle",   "icon": "🔒", "enabled": True,  "version": "3.0.1"},
    {"id": "readmode",    "name": "Read Mode",       "desc": "Makale modunda okumayı etkinleştir",     "icon": "📖", "enabled": False, "version": "1.2.0"},
]
