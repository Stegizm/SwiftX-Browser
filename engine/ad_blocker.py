"""
engine/ad_blocker.py
URL tabanlı reklam ve izleyici engelleme.
"""

from PySide6.QtWebEngineCore import QWebEngineUrlRequestInterceptor

from core.constants import AD_BLOCK_PATTERNS


class AdBlocker(QWebEngineUrlRequestInterceptor):
    """Basit URL filtreleme ile reklam/izleyici engelleyici."""

    def __init__(self):
        super().__init__()
        self.enabled  = True
        self.patterns = AD_BLOCK_PATTERNS

    def interceptRequest(self, info):
        if not self.enabled:
            return
        url = info.requestUrl().toString()
        if self.should_block(url):
            info.block(True)

    def should_block(self, url: str) -> bool:
        # YouTube için ad blocker'ı devre dışı bırak (çakışma önlemek için)
        if 'youtube.com' in url or 'youtu.be' in url:
            return False
        url_lower = url.lower()
        return any(p.lower() in url_lower for p in self.patterns)
