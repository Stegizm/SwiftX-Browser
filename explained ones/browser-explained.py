"""
SwiftX Browser (v27) — EXPLAINED VERSION
============================================
Bu dosya, orijinal browser.py dosyasının birebir kopyasıdır.
Fark: Her fonksiyon, class ve önemli kod bloğunun üstünde/yanında
ne yaptığını açıklayan Türkçe yorumlar eklenmiştir.
-
eğer bir fork yaratıcaksanız lütfen bu dosyayı değiştirmeyin.
sürüm güncellemelerinde bu dosyaya dokunulmayacaktır bu sadece öğrenmek isteyenler içindir.

Meraklı geliştiriciler için hazırlanmıştır.
Gereksinim: pip install PySide6
"""

# ── Standart kütüphaneler ──────────────────────────────────────────────────
# sys      → Python sistem fonksiyonları (sys.exit, sys.argv)
# os       → Dosya/dizin işlemleri (yol oluşturma, dosya varlığı kontrolü)
# json     → JSON okuma/yazma (yer imleri, geçmiş, ayarlar dosyaları)
# time     → Zaman işlemleri (animasyon zamanlaması için)
# datetime → Tarih/saat bilgisi (indirme kaydına zaman damgası eklemek için)
import sys, os, json, time
from datetime import datetime

# ── PySide6 Widget İmportları ──────────────────────────────────────────────
# PySide6, Qt framework'ünün Python bağlantısıdır.
# Tüm görsel arayüz bileşenleri (butonlar, pencereler, listeler) buradan gelir.
from PySide6.QtWidgets import (
    QApplication,    # Uygulamanın kendisi — her Qt programında bir tane olmalı
    QMainWindow,     # Ana pencere sınıfı — menü çubuğu, status bar destekler
    QWidget,         # Tüm görsel bileşenlerin temel sınıfı
    QVBoxLayout,     # Dikey düzen yöneticisi (bileşenleri üst üste dizer)
    QHBoxLayout,     # Yatay düzen yöneticisi (bileşenleri yan yana dizer)
    QLineEdit,       # Tek satır metin girişi — URL çubuğu için kullanılır
    QPushButton,     # Tıklanabilir buton
    QProgressBar,    # Sayfa yükleme ilerleme çubuğu
    QStackedWidget,  # Üst üste yığılmış widget'lar — sekme içerikleri için
    QScrollArea,     # Kaydırılabilir alan — geçmiş/ayarlar paneli için
    QSizePolicy,     # Widget boyutlanma politikası
    QStatusBar,      # Alt durum çubuğu — hover URL, mesajlar için
    QFrame,          # Çerçeve widget'ı — ayırıcı çizgiler için
    QLabel,          # Metin/görsel etiketi
    QMenu,           # Sağ tık bağlam menüsü
    QDialog,         # Modal iletişim kutusu — eklenti merkezi için
    QListWidget,     # Liste görünümü — geçmiş ve indirilenler için
    QListWidgetItem, # Liste elemanı
    QColorDialog,    # Renk seçici diyaloğu
    QInputDialog,    # Kullanıcıdan metin girişi almak için
    QToolButton,     # Araç çubuğu butonu
    QMessageBox      # Bilgi/uyarı popup'ı
)

# ── WebEngine İmportları ───────────────────────────────────────────────────
# QWebEngineView   → Chromium tabanlı web görüntüleyici — asıl tarayıcı motoru
# QWebEngineSettings → JavaScript, yerel dosya erişimi gibi ayarlar
# QWebEngineDownloadRequest → İndirme isteklerini yönetir
# QWebEngineScript → Sayfalara JavaScript enjekte etmek için
# QWebEnginePermission → Kamera/mikrofon/konum izinlerini yönetir
# QWebEngineProfile → Çerez, önbellek, kullanıcı ajanı ayarları
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import (
    QWebEngineSettings, QWebEngineDownloadRequest,
    QWebEngineScript, QWebEnginePermission, QWebEngineProfile
)

# ── Qt Temel İmportları ────────────────────────────────────────────────────
# QUrl        → URL nesnesi oluşturmak için (string'den daha güvenli)
# Qt          → Sabitler (Qt.AlignTop, Qt.UserRole vb.)
# QTimer      → Belirli aralıklarla fonksiyon çağırmak için (animasyon, saat)
# QSize       → Genişlik/yükseklik çifti
# QPoint      → X/Y koordinat çifti
# QObject     → Qt nesne sisteminin temel sınıfı (sinyal/slot için)
from PySide6.QtCore import QUrl, Qt, QTimer, QSize, QPoint, QObject

# ── Qt GUI İmportları ──────────────────────────────────────────────────────
# QAction     → Klavye kısayolu tanımlamak için (Ctrl+T, F5 vb.)
# QColor      → Renk nesnesi
# QPalette    → Widget renk paleti
# QCursor     → Fare imleci konumu (bağlam menüsü konumlandırma)
# QWheelEvent → Fare tekerleği olayı (smooth scroll için)
# QIcon       → Pencere/uygulama ikonu
from PySide6.QtGui import QAction, QColor, QPalette, QCursor, QWheelEvent, QIcon

# ── Sabitler ──────────────────────────────────────────────────────────────
SIDEBAR_W  = 48   # Sidebar'ın piksel genişliği
DATA_DIR   = os.path.expanduser("~/.swiftx")          # Kullanıcı verisinin saklandığı dizin (~/.swiftx)
BM_FILE    = os.path.join(DATA_DIR, "bookmarks.json") # Yer imleri dosyası
HIST_FILE  = os.path.join(DATA_DIR, "history.json")   # Geçmiş dosyası
DL_FILE    = os.path.join(DATA_DIR, "downloads.json") # İndirilenler dosyası
SESSION_FILE = os.path.join(DATA_DIR, "session.json") # Oturum kayıt dosyası
EXTENSIONS_FILE = os.path.join(DATA_DIR, "extensions.json") # Eklenti durumları

# ── Sekme Renk Grupları ────────────────────────────────────────────────────
# Sağ tık menüsünden sekmelere renk atamak için kullanılır.
# Format: "renk_adı": ("arka_plan_rengi", "yazı_rengi")
# "none" → renk grubu yok (varsayılan)
TAB_COLORS = {
    "none":   ("", ""),
    "kırmızı":("#e74c3c", "#fff"),
    "turuncu":("#e67e22", "#fff"),
    "sarı":   ("#f1c40f", "#222"),
    "yeşil":  ("#27ae60", "#fff"),
    "mavi":   ("#3498db", "#fff"),
    "mor":    ("#9b59b6", "#fff"),
}

# ── Reklam Engelleme Desenleri ─────────────────────────────────────────────
# URL içinde bu desenlerden biri varsa istek engellenir.
# AdBlocker sınıfı tarafından kullanılır.
AD_BLOCK_PATTERNS = [
    "google.com/ads", "doubleclick.net", "pagead", "adsbygoogle",
    "ads.google", "googleadservices.com", "facebook.com/tr",
    "analytics.google.com", "youtube.com/api/stats",
    "amazon-adsystem.com", "criteo.com", "moatpixel.com",
    "rubiconproject.com", "pubmatic.com", "gumgum.com",
]

# ── Varsayılan Eklentiler ──────────────────────────────────────────────────
# Kullanıcının extensions.json dosyası yoksa bu liste kullanılır.
# Her eklenti bir sözlük: id, name, desc, icon, enabled, version
DEFAULT_EXTENSIONS = [
    {
        "id": "dark_reader",
        "name": "Dark Reader",
        "desc": "Web sayfalarına dark mode uygula",
        "icon": "🌙",
        "enabled": False,
        "version": "1.0.0"
    },
    {
        "id": "no_ads",
        "name": "No Ads",
        "desc": "Reklam ve izleme engelle",
        "icon": "🚫",
        "enabled": True,
        "version": "2.1.0"
    },
    {
        "id": "speedup",
        "name": "Page Speed",
        "desc": "Sayfa yüklemesini hızlandır",
        "icon": "⚡",
        "enabled": False,
        "version": "1.5.2"
    },
    {
        "id": "privacy",
        "name": "Privacy Guard",
        "desc": "İzleme ve profil oluşturmayı engelle",
        "icon": "🔒",
        "enabled": True,
        "version": "3.0.1"
    },
    {
        "id": "readmode",
        "name": "Read Mode",
        "desc": "Makale modunda okumayı etkinleştir",
        "icon": "📖",
        "enabled": False,
        "version": "1.2.0"
    },
]

# ~/.swiftx dizinini oluştur (yoksa). exist_ok=True → zaten varsa hata verme
os.makedirs(DATA_DIR, exist_ok=True)

# ── Yardımcı Fonksiyonlar ──────────────────────────────────────────────────

def _load(path, default):
    """
    JSON dosyasını okur ve Python nesnesine dönüştürür.
    Dosya yoksa veya bozuksa 'default' değerini döndürür.
    Kullanım: bookmarks = _load(BM_FILE, [])
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def _save(path, data):
    """
    Python nesnesini JSON dosyasına yazar.
    ensure_ascii=False → Türkçe karakterlerin bozulmaması için
    indent=2 → okunabilir, girintili JSON formatı
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ── Ana Stil Tanımı ────────────────────────────────────────────────────────
# Qt Style Sheet (QSS) — CSS'e benzer sözdizimi ile tüm arayüzün görünümünü belirler.
# app.setStyleSheet(STYLE) ile tüm uygulamaya uygulanır.
# #objectName → ID seçici (CSS'deki gibi)
# QPushButton[active="true"] → özellik seçici
STYLE = """
* { outline: none; }
QMainWindow, QWidget {
    background: #1c1b22;
    color: #fbfbfe;
    font-family: 'SF Pro Text', 'Helvetica Neue', 'Segoe UI', sans-serif;
    font-size: 13px;
}
#toggleBtn {
    background: transparent; border: none;
    border-right: 1px solid #2a2930;
    color: #9e9db5; font-size: 17px;
    min-width: 40px; max-width: 40px;
    min-height: 40px; max-height: 40px; padding: 0;
}
#toggleBtn:hover   { background: #2a2930; color: #fbfbfe; }
#toggleBtn:pressed { background: #35343e; }
#sidebar { background: #1c1b22; border-right: 1px solid #2a2930; }
#sideBtn {
    background: transparent; border: none; border-radius: 8px;
    color: #9e9db5; font-size: 17px;
    min-width: 36px; max-width: 36px;
    min-height: 36px; max-height: 36px;
    padding: 0; margin: 2px 6px;
}
#sideBtn:hover   { background: #2a2930; color: #fbfbfe; }
#sideBtn:pressed { background: #35343e; }
#tabStrip { background: #1c1b22; min-height: 36px; max-height: 36px; }
#tabBtn {
    background: transparent; color: #9e9db5; border: none;
    border-radius: 6px; padding: 0 10px; font-size: 12px;
    min-height: 28px; max-height: 28px;
    min-width: 80px; max-width: 200px;
    text-align: left; margin: 4px 1px;
}
#tabBtn[active="true"] { background: #2a2930; color: #fbfbfe; }
#tabBtn:hover:!pressed { background: #252430; color: #c8c7de; }
#tabCloseBtn {
    background: transparent; color: transparent; border: none;
    border-radius: 4px; font-size: 10px;
    min-width: 16px; max-width: 16px;
    min-height: 16px; max-height: 16px;
    padding: 0; margin: 0 2px 0 0;
}
#tabCloseBtn:hover { background: #3d3c4e; color: #c8c7de; }
#newTabBtn {
    background: transparent; color: #6e6d85; border: none;
    border-radius: 6px; font-size: 18px;
    min-width: 28px; max-width: 28px;
    min-height: 28px; max-height: 28px;
    padding: 0; margin: 4px 4px;
}
#newTabBtn:hover { background: #2a2930; color: #c8c7de; }
#navBar {
    background: #1c1b22; border-bottom: 1px solid #2a2930;
    min-height: 44px; max-height: 44px;
}
#navBtn {
    background: transparent; color: #9e9db5; border: none;
    border-radius: 6px; font-size: 15px;
    min-width: 30px; max-width: 30px;
    min-height: 30px; max-height: 30px; padding: 0;
}
#navBtn:hover   { background: #2a2930; color: #fbfbfe; }
#navBtn:pressed { background: #35343e; }
#navBtn:disabled { color: #3a3948; }
#urlBar {
    background: #2a2930; color: #fbfbfe;
    border: 1px solid transparent; border-radius: 8px;
    padding: 0 14px; font-size: 13px;
    min-height: 32px; max-height: 32px;
    selection-background-color: #5b5bef;
}
#urlBar:focus        { border: 1px solid #5b5bef; background: #35343e; }
#urlBar:hover:!focus { background: #35343e; }
#bmBar {
    background: #17161d;
    border-bottom: 1px solid #2a2930;
    min-height: 30px; max-height: 30px;
    padding: 0 6px;
}
#bmBtn {
    background: transparent; color: #9e9db5; border: none;
    border-radius: 5px; font-size: 12px;
    height: 24px; padding: 0 8px; margin: 3px 1px;
}
#bmBtn:hover   { background: #2a2930; color: #fbfbfe; }
#bmBtn:pressed { background: #35343e; }
#bmAddBtn {
    background: transparent; color: #6e6d85; border: none;
    border-radius: 5px; font-size: 16px;
    min-width: 24px; max-width: 24px;
    height: 24px; padding: 0; margin: 3px 2px;
}
#bmAddBtn:hover { background: #2a2930; color: #c8c7de; }
#dlBar {
    background: #1e1d28; border-top: 1px solid #2a2930;
    min-height: 36px; max-height: 36px; padding: 0 12px;
}
#dlLabel { color: #9e9db5; font-size: 12px; }
#dlCloseBtn {
    background: transparent; color: #6e6d85; border: none;
    border-radius: 4px; font-size: 13px;
    min-width: 24px; max-width: 24px;
    min-height: 24px; max-height: 24px; padding: 0;
}
#dlCloseBtn:hover { background: #2a2930; color: #fbfbfe; }
#progress { background: transparent; border: none; max-height: 2px; min-height: 2px; }
#progress::chunk {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #5b5bef,stop:1 #a16ef8);
    border-radius: 1px;
}
QStatusBar {
    background: #1c1b22; color: #6e6d85;
    border-top: 1px solid #2a2930;
    font-size: 11px; min-height: 20px; max-height: 20px;
}
#panel {
    background: #17161d;
    border-left: 1px solid #2a2930;
    min-width: 300px; max-width: 300px;
}
#panelTitle {
    font-size: 14px; font-weight: bold;
    color: #fbfbfe; padding: 12px 16px 8px;
    border-bottom: 1px solid #2a2930;
}
#panelList {
    background: transparent; border: none;
    font-size: 12px; color: #c8c7de;
}
#panelList::item { padding: 8px 16px; border-bottom: 1px solid #1c1b22; }
#panelList::item:hover { background: #2a2930; }
#panelList::item:selected { background: #35343e; color: #fbfbfe; }
#panelCloseBtn {
    background: transparent; color: #6e6d85; border: none;
    border-radius: 6px; font-size: 15px;
    min-width: 28px; max-width: 28px;
    min-height: 28px; max-height: 28px; padding: 0;
    margin: 8px 8px 0 0;
}
#panelCloseBtn:hover { background: #2a2930; color: #fbfbfe; }
#clearBtn {
    background: transparent; color: #6e6d85; border: none;
    border-top: 1px solid #2a2930;
    font-size: 12px; height: 32px; padding: 0 16px;
}
#clearBtn:hover { color: #e74c3c; }
QDialog {
    background: #1c1b22;
    color: #fbfbfe;
}
QMessageBox {
    background: #1c1b22;
}
QMessageBox QLabel {
    color: #fbfbfe;
}
"""

# ── Home Sayfası için Ek CSS ───────────────────────────────────────────────
# Bu CSS, home (v6).html içine enjekte edilmez; sadece Python tarafında
# referans olarak tutulur. Ana sayfa HTML'i kendi stilini zaten içerir.
HOME_BRAND_CSS = """
<style>
.home-brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  animation: none !important;
  opacity: 1 !important;
  transform: none !important;
}
.home-logo {
  width: 42px;
  height: auto;
}
.home-title {
  color: #ffffff;
  font-size: 18px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}
</style>
"""


# ══════════════════════════════════════════════════════════════════════════════
# CLASS: AdBlocker
# ══════════════════════════════════════════════════════════════════════════════
# Basit desen tabanlı reklam engelleyici.
# QWebEngineView'in istek önleme mekanizmasıyla entegre edilmemiştir;
# URL kontrolü MainWindow içinde manuel olarak yapılır.
# enabled = False yapılırsa should_block() her zaman False döndürür.
class AdBlocker:
    """Basit URL filtreleme ile reklam bloker."""
    def __init__(self):
        self.enabled = True             # Başlangıçta aktif
        self.patterns = AD_BLOCK_PATTERNS  # Engellenecek URL desenleri

    def should_block(self, url: str) -> bool:
        """
        Verilen URL'nin engellenmesi gerekip gerekmediğini kontrol eder.
        url.lower() ile büyük/küçük harf farkı gözetmeksizin karşılaştırır.
        """
        if not self.enabled:
            return False
        url_lower = url.lower()
        return any(pattern.lower() in url_lower for pattern in self.patterns)


# ══════════════════════════════════════════════════════════════════════════════
# CLASS: TabWidget
# ══════════════════════════════════════════════════════════════════════════════
# Sekme şeridindeki tek bir sekmeyi temsil eden widget.
# İçinde iki bileşen var:
#   - btn (QPushButton)       → sekme başlığı, tıklanınca sekmeye geçer
#   - close_btn (QPushButton) → ✕ butonu, sekmeyi kapatır
# on_click, on_close, on_right_click → dışarıdan (MainWindow'dan) geçirilen callback'ler
class TabWidget(QWidget):
    def __init__(self, on_click, on_close, on_right_click):
        super().__init__()
        self.setObjectName("tabWidget")
        self._color = ""  # Aktif renk grubu adı ("kırmızı", "mavi" vb.)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.btn = QPushButton("Yeni Sekme")
        self.btn.setObjectName("tabBtn")
        self.btn.setProperty("active", False)  # QSS'te [active="true"] seçici için
        self.btn.clicked.connect(on_click)
        self.btn.setContextMenuPolicy(Qt.CustomContextMenu)
        self.btn.customContextMenuRequested.connect(on_right_click)
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("tabCloseBtn")
        self.close_btn.clicked.connect(on_close)
        layout.addWidget(self.btn)
        layout.addWidget(self.close_btn)

    def set_active(self, v):
        """
        Sekmenin aktif/pasif görünümünü günceller.
        unpolish + polish → QSS'in property değişikliğini algılaması için gerekli.
        """
        self.btn.setProperty("active", v)
        self.btn.style().unpolish(self.btn)
        self.btn.style().polish(self.btn)

    def set_title(self, t):
        """
        Sekme başlığını ayarlar.
        24 karakterden uzunsa kısaltır ve '…' ekler.
        """
        self.btn.setText((t[:22] + "…") if len(t) > 24 else t or "Yeni Sekme")

    def set_color(self, color_name):
        """
        Sekmeye renk grubu uygular (sağ tık menüsünden).
        "none" seçilirse renk temizlenir ve varsayılan stil geri yüklenir.
        """
        self._color = color_name
        bg, fg = TAB_COLORS.get(color_name, ("", ""))
        if bg:
            self.btn.setStyleSheet(
                f"#tabBtn {{ background: {bg}; color: {fg}; border-radius: 6px; }}"
                f"#tabBtn:hover {{ background: {bg}; opacity: 0.8; }}"
            )
        else:
            self.btn.setStyleSheet("")
            self.btn.style().unpolish(self.btn)
            self.btn.style().polish(self.btn)


# ── Smooth Scroll CSS (sayfaya enjekte edilir) ────────────────────────────
# HTML sayfasına eklenen CSS — scroll-behavior: smooth ile yumuşak kaydırma sağlar.
# Not: Bu CSS tek başına yeterli değildir, SmoothScroller class'ı da gereklidir.
SMOOTH_SCROLL_CSS = """
html {
    scroll-behavior: smooth;
}
* {
    scroll-behavior: smooth;
}
"""

# ── Auto Dark Mode CSS (sayfaya enjekte edilir) ───────────────────────────
# prefers-color-scheme: dark media query'si ile sayfanın renk şemasını zorla karanlık yapar.
# Tüm sayfalarda çalışmaz — bazı sayfalar kendi dark mode'larını override edebilir.
AUTO_DARK_MODE_CSS = """
@media (prefers-color-scheme: dark) {
    :root {
        color-scheme: dark;
    }
    body {
        background-color: #1c1b22 !important;
        color: #fbfbfe !important;
    }
    a {
        color: #5b5bef !important;
    }
    input, textarea, select {
        background-color: #2a2930 !important;
        color: #fbfbfe !important;
        border: 1px solid #35343e !important;
    }
    button {
        background-color: #2a2930 !important;
        color: #fbfbfe !important;
        border: 1px solid #35343e !important;
    }
}
"""

# ── Klavye Scroll JavaScript (sayfaya enjekte edilir) ─────────────────────
# Space, PageUp/PageDown, yukarı/aşağı ok tuşlarına smooth scroll ekler.
# window.__swiftx_kb kontrolü → aynı script'in birden fazla enjekte edilmesini önler.
# EASE fonksiyonu → easing curve (başlangıç/bitiş yavaş, orta hızlı)
# DURATION → animasyon süresi (ms)
KEYBOARD_SCROLL_JS = """
(function() {
  if (window.__swiftx_kb) return;
  window.__swiftx_kb = true;
  const KEYS = { 32: 600, 33: -600, 34: 600, 38: -120, 40: 120 };
  const DURATION = 400;
  const EASE = t => t < 0.5 ? 2*t*t : -1+(4-2*t)*t;
  function smoothScroll(dy) {
    const el = document.scrollingElement || document.documentElement;
    const startY = el.scrollTop, start = performance.now();
    function step(now) {
      const t = Math.min((now - start) / DURATION, 1);
      el.scrollTop = startY + dy * EASE(t);
      if (t < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  window.addEventListener('keydown', function(e) {
    if (['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName)) return;
    const dy = KEYS[e.keyCode];
    if (dy === undefined) return;
    if (e.keyCode === 32) e.preventDefault();
    smoothScroll(dy);
  });
})();
"""

# ── Auto Dark Mode JavaScript (sayfaya enjekte edilir) ────────────────────
# window.matchMedia ile sistemin dark mode tercihini algılar.
# DocumentCreation aşamasında enjekte edilir → sayfa yüklenmeden önce çalışır.
# runsOnSubFrames=True → iframe içindeki sayfaları da etkiler.
AUTO_DARK_MODE_JS = """
(function() {
    if (window.__auto_dark_mode) return;
    window.__auto_dark_mode = true;
    const darkTheme = window.matchMedia('(prefers-color-scheme: dark)');
    function applyDarkMode() {
        if (darkTheme.matches) {
            document.documentElement.style.colorScheme = 'dark';
            const style = document.createElement('style');
            style.textContent = `
                :root { color-scheme: dark; }
                body { background-color: #1c1b22 !important; color: #fbfbfe !important; }
                a { color: #5b5bef !important; }
                input, textarea, select { background-color: #2a2930 !important; color: #fbfbfe !important; }
            `;
            document.head.appendChild(style);
        }
    }
    applyDarkMode();
    darkTheme.addListener(() => applyDarkMode());
})();
"""


# ══════════════════════════════════════════════════════════════════════════════
# CLASS: SmoothScroller
# ══════════════════════════════════════════════════════════════════════════════
# Fare tekerleği kaydırmasını fizik tabanlı olarak yumuşatır.
# QObject'ten türer → eventFilter kurabilmek için gerekli.
# Çalışma prensibi:
#   1. Tekerlek döndürüldüğünde _vel (hız) değeri artar
#   2. QTimer her 8ms'de bir _step() çağırır
#   3. _step(), hızla sayfayı kaydırır ve FRICTION ile hızı yavaşlatır
#   4. Hız MIN_VEL'in altına düşünce timer durur
class SmoothScroller(QObject):
    """60fps smooth scroll — QWebEngineView.scroll() ile senkron."""

    PIXELS   = 220   # Tek tekerlek adımında eklenen piksel hızı
    FRICTION = 0.82  # Her adımda hızın çarpıldığı yavaşlama katsayısı (0-1 arası)
    MIN_VEL  = 0.5   # Bu değerin altında hız sıfırlanır ve animasyon durur

    def __init__(self, view):
        super().__init__(view)
        self._view     = view
        self._vel      = 0.0   # Anlık dikey hız (piksel/adım)
        self._timer    = QTimer(self)
        self._timer.setInterval(8)  # ~120fps
        self._timer.timeout.connect(self._step)
        view.installEventFilter(self)  # View'ın tüm olaylarını dinle

    def eventFilter(self, obj, event):
        """
        QWebEngineView'dan gelen tüm olayları filtreler.
        Sadece tekerlek olaylarını yakalar, gerisini geçirir.
        Orta tuş veya Ctrl+Scroll → zoom için geçirir (smooth etmez).
        """
        if isinstance(event, QWheelEvent):
            if event.buttons() & Qt.MiddleButton or event.modifiers() & Qt.ControlModifier:
                return False
            delta = event.angleDelta().y()
            if delta == 0:
                return False
            self._vel += -(delta / 120.0) * self.PIXELS
            if not self._timer.isActive():
                self._timer.start()
            return True  # Olayı tüket — tarayıcının kendi scroll'unu engelle
        return False

    def _step(self):
        """
        Her 8ms'de çağrılır. Hızla sayfayı kaydırır, sonra hızı azaltır.
        runJavaScript → tarayıcı sayfasında JS çalıştırarak kaydırma yapar.
        """
        if abs(self._vel) < self.MIN_VEL:
            self._vel = 0.0
            self._timer.stop()
            return
        move = self._vel
        self._vel *= self.FRICTION
        self._view.page().runJavaScript(
            f"window.scrollBy(0, {move:.3f});"
        )


# ══════════════════════════════════════════════════════════════════════════════
# CLASS: BrowserPage
# ══════════════════════════════════════════════════════════════════════════════
# Her sekmenin içeriğini temsil eden widget.
# QWebEngineView'i barındırır ve üzerine script'ler enjekte eder.
# MainWindow.stack (QStackedWidget) içinde tutulur — aktif sekme görünür olur.
# smooth_scroll ve dark_mode parametreleri MainWindow'daki ayar değişkenlerinden gelir.
class BrowserPage(QWidget):
    def __init__(self, url="", smooth_scroll=True, dark_mode=True):
        super().__init__()
        l = QVBoxLayout(self)
        l.setContentsMargins(0, 0, 0, 0)

        # QWebEngineView → Chromium tabanlı web motoru
        self.view = QWebEngineView()
        s = self.view.settings()

        # LocalContentCanAccessFileUrls → file:// URL'lerinin birbirine erişmesi
        # (home.html'in bg.jpg'ye erişebilmesi için gerekli)
        s.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        s.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        s.setAttribute(QWebEngineSettings.WebAttribute.ScreenCaptureEnabled, True)
        # PlaybackRequiresUserGesture=False → otomatik video oynatmaya izin ver
        s.setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)
        s.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)

        # ── Smooth Scroll Script Enjeksiyonu ──
        # QWebEngineScript ile her yeni sayfa yüklendiğinde otomatik enjekte edilir.
        # InjectionPoint.DocumentReady → DOM hazır olduktan sonra çalışır
        if smooth_scroll:
            script = QWebEngineScript()
            script.setName("swiftx_smooth_scroll")
            script.setSourceCode(KEYBOARD_SCROLL_JS)
            script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentReady)
            script.setRunsOnSubFrames(False)
            script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
            self.view.page().scripts().insert(script)

        # ── Auto Dark Mode Script Enjeksiyonu ──
        # DocumentCreation → sayfa DOM'u oluşturulmadan önce çalışır
        # (flash of white content'i önlemek için erken enjekte edilir)
        # RunsOnSubFrames=True → iframe'ler dahil tüm çerçevelerde çalışır
        if dark_mode:
            dark_script = QWebEngineScript()
            dark_script.setName("swiftx_dark_mode")
            dark_script.setSourceCode(AUTO_DARK_MODE_JS)
            dark_script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation)
            dark_script.setRunsOnSubFrames(True)
            dark_script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
            self.view.page().scripts().insert(dark_script)

        if url:
            self.view.load(QUrl(url))
        l.addWidget(self.view)

        # SmoothScroller → fare tekerleği olaylarını yakalar ve fizik tabanlı kaydırma yapar
        if smooth_scroll:
            self.scroller = SmoothScroller(self.view)

    @property
    def title(self):
        """Sayfanın başlığını döndürür. Yoksa 'Yeni Sekme' döner."""
        return self.view.title() or "Yeni Sekme"

    @property
    def url(self):
        """Sayfanın mevcut URL'sini string olarak döndürür."""
        return self.view.url().toString()


# ══════════════════════════════════════════════════════════════════════════════
# CLASS: ExtensionStore
# ══════════════════════════════════════════════════════════════════════════════
# Eklenti merkezini gösteren modal diyalog penceresi.
# QDialog → modal pencere (ana pencereyi bloke eder)
# self.changes sözlüğü → kullanıcının değiştirdiği eklentilerin yeni durumlarını tutar
# dialog.exec() → kullanıcı "Kaydet" veya "İptal"e basana kadar bekler
# Kaydet → True döner, MainWindow changes sözlüğünü uygular
class ExtensionStore(QDialog):
    """Eklenti mağazası diyalogu"""
    def __init__(self, extensions, parent=None):
        super().__init__(parent)
        self.setWindowTitle("eklenti Merkezi")
        self.setGeometry(100, 100, 500, 600)
        self.extensions = extensions  # Mevcut eklenti listesi (referans)
        self.changes = {}             # {eklenti_id: yeni_enabled_değeri}

        layout = QVBoxLayout(self)

        title = QLabel("📦 SwiftX Eklenti Merkezi")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #fbfbfe; padding: 12px;")
        layout.addWidget(title)

        # Kaydırılabilir eklenti listesi
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            "QScrollArea { background: #1c1b22; border: none; }"
            "QScrollBar:vertical { width: 8px; background: #2a2930; }"
            "QScrollBar::handle:vertical { background: #35343e; border-radius: 4px; }"
        )

        inner = QWidget()
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(12, 12, 12, 12)
        inner_layout.setSpacing(12)

        # Her eklenti için bir satır widget oluştur
        for ext in extensions:
            ext_widget = self._create_extension_item(ext)
            inner_layout.addWidget(ext_widget)

        inner_layout.addStretch()
        scroll.setWidget(inner)
        layout.addWidget(scroll)

        # Alt butonlar
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Değişiklikleri Kaydet")
        save_btn.setStyleSheet(
            "QPushButton { background: #5b5bef; color: #fff; border: none; "
            "border-radius: 4px; padding: 8px 16px; font-weight: bold; }"
            "QPushButton:hover { background: #7575ff; }"
        )
        save_btn.clicked.connect(self.accept)  # QDialog.accept() → exec() True döndürür

        cancel_btn = QPushButton("✕ İptal")
        cancel_btn.setStyleSheet(
            "QPushButton { background: #2a2930; color: #fbfbfe; border: none; "
            "border-radius: 4px; padding: 8px 16px; }"
            "QPushButton:hover { background: #35343e; }"
        )
        cancel_btn.clicked.connect(self.reject)  # QDialog.reject() → exec() False döndürür

        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def _create_extension_item(self, ext):
        """
        Tek bir eklenti için satır widget'ı oluşturur.
        nonlocal is_enabled → closure içinde değişkeni değiştirmek için gerekli.
        self.changes[ext['id']] = is_enabled → değişikliği kayıt eder.
        """
        widget = QWidget()
        widget.setStyleSheet("background: #2a2930; border-radius: 6px; padding: 12px;")
        h_layout = QHBoxLayout(widget)

        info_layout = QVBoxLayout()
        name_label = QLabel(f"{ext['icon']}  {ext['name']}")
        name_label.setStyleSheet("font-weight: bold; color: #fbfbfe; font-size: 13px;")
        desc_label = QLabel(ext['desc'])
        desc_label.setStyleSheet("color: #9e9db5; font-size: 11px;")
        ver_label = QLabel(f"v{ext['version']}")
        ver_label.setStyleSheet("color: #6e6d85; font-size: 10px;")

        info_layout.addWidget(name_label)
        info_layout.addWidget(desc_label)
        info_layout.addWidget(ver_label)

        toggle_btn = QPushButton("Kapalı" if not ext['enabled'] else "Açık")
        toggle_btn.setMaximumWidth(70)
        is_enabled = ext['enabled']

        def update_state():
            """Toggle butonuna basıldığında durumu tersine çevirir."""
            nonlocal is_enabled
            is_enabled = not is_enabled
            toggle_btn.setText("Açık" if is_enabled else "Kapalı")
            toggle_btn.setStyleSheet(
                f"QPushButton {{ background: {'#27ae60' if is_enabled else '#e74c3c'}; "
                f"color: #fff; border: none; border-radius: 4px; padding: 6px 12px; "
                f"font-weight: bold; }}"
                f"QPushButton:hover {{ background: {'#229954' if is_enabled else '#c0392b'}; }}"
            )
            self.changes[ext['id']] = is_enabled  # Değişikliği kaydet

        toggle_btn.setStyleSheet(
            f"QPushButton {{ background: {'#27ae60' if is_enabled else '#e74c3c'}; "
            f"color: #fff; border: none; border-radius: 4px; padding: 6px 12px; "
            f"font-weight: bold; }}"
            f"QPushButton:hover {{ background: {'#229954' if is_enabled else '#c0392b'}; }}"
        )
        toggle_btn.clicked.connect(update_state)

        h_layout.addLayout(info_layout)
        h_layout.addStretch()
        h_layout.addWidget(toggle_btn)

        return widget


# ══════════════════════════════════════════════════════════════════════════════
# CLASS: MainWindow
# ══════════════════════════════════════════════════════════════════════════════
# Uygulamanın ana penceresi. Tüm bileşenleri barındırır ve koordine eder.
# QMainWindow'dan türer → status bar, menu bar desteği sağlar.
#
# Temel veri yapıları:
#   self._tabs      → [(TabWidget, BrowserPage), ...] — tüm açık sekmeler
#   self._active    → int — aktif sekmenin indeksi
#   self._bookmarks → list — yer imleri [{title, url}, ...]
#   self._history   → list — gezinti geçmişi [{title, url, time}, ...]
#   self._downloads → list — indirilen dosyalar [{name, path, time}, ...]
#   self._extensions → list — eklenti durumları
#
# Temel UI bileşenleri:
#   self._sidebar   → sol sidebar (⌕ ⌂ 🧩 ⚙)
#   self.stack      → QStackedWidget — sekme içerikleri
#   self._panel     → sağ panel (geçmiş / indirilenler / ayarlar)
#   self.url_bar    → URL girişi
#   self.progress   → sayfa yükleme progress bar'ı
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Ana sayfa HTML dosyasının yolunu belirle
        # Dosya varsa file:// URL'si, yoksa startpage.com kullan
        _here = os.path.dirname(os.path.abspath(__file__))
        _html = os.path.join(_here, "home (v6).html")
        self.HOME = ("file://" + _html) if os.path.exists(_html) else "https://www.startpage.com"

        # Verileri JSON dosyalarından yükle (dosya yoksa varsayılan değer kullan)
        self._bookmarks  = _load(BM_FILE, [])
        self._history    = _load(HIST_FILE, [])
        self._downloads  = _load(DL_FILE, [])
        self._extensions = _load(EXTENSIONS_FILE, DEFAULT_EXTENSIONS)
        self._ad_blocker = AdBlocker()

        # Ayar değişkenleri — ayarlar panelindeki toggle'lar bunları değiştirir
        self._smooth_scroll    = True   # Smooth scroll aktif mi?
        self._dark_mode        = True   # Auto dark mode aktif mi?
        self._restore_session  = True   # Oturum kurtarma aktif mi?

        # Varsayılan WebEngine profiline çerez politikası uygula
        profile = QWebEngineProfile.defaultProfile()
        profile.setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies
        )

        self.setWindowTitle("SwiftX")
        self.setWindowIcon(QIcon(os.path.join(_here, "SXBETALOGO3.png")))
        self.resize(1360, 860)
        self.setStyleSheet(STYLE)

        # Tab yönetimi
        self._tabs   = []   # [(TabWidget, BrowserPage), ...]
        self._active = -1   # Aktif sekme indeksi (-1 = henüz yok)

        # Panel/sidebar durum değişkenleri
        self._sidebar_open    = True
        self._panel_visible   = False
        self._settings_visible = False

        self._build_ui()       # Tüm arayüzü oluştur
        self._load_session()   # Son oturumu geri yükle

    def _save_session(self):
        """
        Mevcut sekmeleri session.json'a kaydeder.
        Ana sayfa (HOME) sekmelerini kaydetmez — sadece gerçek URL'leri kaydeder.
        Pencere kapatılırken self.destroyed sinyaline bağlı olarak çağrılır.
        """
        session = {
            "tabs": [
                {"url": t[1].url, "title": t[1].title}
                for t in self._tabs if t[1].url != self.HOME
            ],
            "active": self._active
        }
        _save(SESSION_FILE, session)

    def _load_session(self):
        """
        Uygulama açılırken son oturumu geri yükler.
        _restore_session=False ise sadece yeni sekme açar.
        Kayıtlı sekme yoksa da yeni sekme açar.
        """
        if not self._restore_session:
            self._new_tab()
            return

        session = _load(SESSION_FILE, None)
        if session and session.get("tabs"):
            for tab_data in session["tabs"]:
                self._new_tab(tab_data.get("url", self.HOME))
            active_idx = session.get("active", 0)
            if 0 <= active_idx < len(self._tabs):
                self._switch(active_idx)
            self.status.showMessage(f"✓ {len(session['tabs'])} sekme geri yüklendi", 3000)
        else:
            self._new_tab()

    def _build_ui(self):
        """
        Tüm arayüz bileşenlerini oluşturur ve layout'a yerleştirir.
        Çağrıldığı yer: __init__ içinde, bir kez.

        Layout yapısı:
        root (QWidget)
          └── root_h (QHBoxLayout)
                ├── _sidebar (QWidget, sabit genişlik)
                ├── mid (QWidget)
                │     └── mid_v (QVBoxLayout)
                │           ├── tab_strip  → sekmeler şeridi
                │           ├── nav_bar    → URL çubuğu ve nav butonları
                │           ├── bm_container → yer imleri çubuğu
                │           ├── progress   → yükleme çubuğu
                │           ├── stack      → sekme içerikleri (QStackedWidget)
                │           └── _dl_bar   → indirme bildirimi
                └── _panel (QWidget, sağ panel)
        """
        root = QWidget()
        root_h = QHBoxLayout(root)
        root_h.setContentsMargins(0, 0, 0, 0)
        root_h.setSpacing(0)

        # ── Sidebar ──────────────────────────────────────────────────────────
        # Sol kenar çubuğu. 4 buton içerir:
        # ⌕ Ara (bağlı değil), ⌂ Ana Sayfa, 🧩 Eklentiler, ⚙ Ayarlar
        # fn=None olan butonlar henüz işlev atanmamış
        self._sidebar = QWidget()
        self._sidebar.setObjectName("sidebar")
        self._sidebar.setFixedWidth(SIDEBAR_W)
        sb = QVBoxLayout(self._sidebar)
        sb.setContentsMargins(0, 8, 0, 8)
        sb.setSpacing(2)
        sb.setAlignment(Qt.AlignTop)
        for icon, tip, fn in [
            ("⌕", "Ara", None),
            ("⌂", "Ana Sayfa", "_go_home"),
            ("🧩", "Eklentiler", "_open_extensions"),
            ("⚙", "Ayarlar", "_toggle_settings")
        ]:
            b = QPushButton(icon)
            b.setObjectName("sideBtn")
            b.setToolTip(tip)
            if fn:
                b.clicked.connect(getattr(self, fn))
            sb.addWidget(b, alignment=Qt.AlignHCenter)
        sb.addStretch()

        # Sidebar animasyonu için timer ve değişkenler
        # _anim_timer → her 8ms'de _anim_step() çağırır
        # _anim_target → hedef genişlik (açıksa SIDEBAR_W, kapalıysa 0)
        # _anim_current → anlık genişlik (float, smooth geçiş için)
        self._anim_timer   = QTimer()
        self._anim_timer.setInterval(8)
        self._anim_timer.timeout.connect(self._anim_step)
        self._anim_target  = SIDEBAR_W
        self._anim_current = float(SIDEBAR_W)

        # ── Orta Alan ─────────────────────────────────────────────────────────
        mid = QWidget()
        mid_v = QVBoxLayout(mid)
        mid_v.setContentsMargins(0, 0, 0, 0)
        mid_v.setSpacing(0)

        # Sekme şeridi — toggle butonu + sekmeler + yeni sekme butonu
        tab_strip = QWidget()
        tab_strip.setObjectName("tabStrip")
        self._tl = QHBoxLayout(tab_strip)
        self._tl.setContentsMargins(0, 0, 6, 0)
        self._tl.setSpacing(0)
        self._toggle_btn = QPushButton("☰")
        self._toggle_btn.setObjectName("toggleBtn")
        self._toggle_btn.setToolTip("Sidebar Aç/Kapat (Ctrl+B)")
        self._toggle_btn.clicked.connect(self._toggle_sidebar)
        self._tl.addWidget(self._toggle_btn)
        self._tl.addStretch()
        ntb = QPushButton("+")
        ntb.setObjectName("newTabBtn")
        ntb.clicked.connect(self._new_tab)
        self._tl.addWidget(ntb)

        # Nav bar — geri/ileri/yenile + URL çubuğu + yıldız/geçmiş/indirme butonları
        nav_bar = QWidget()
        nav_bar.setObjectName("navBar")
        nav_h = QHBoxLayout(nav_bar)
        nav_h.setContentsMargins(8, 6, 8, 6)
        nav_h.setSpacing(4)
        self.btn_back    = self._nav("←")
        self.btn_forward = self._nav("→")
        self.btn_reload  = self._nav("↻")
        self.url_bar = QLineEdit()
        self.url_bar.setObjectName("urlBar")
        self.url_bar.setPlaceholderText("Ara veya adres gir")
        self.url_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.url_bar.returnPressed.connect(self._navigate)
        self.btn_star = self._nav("☆")
        self.btn_star.setToolTip("Yer İmine Ekle (Ctrl+D)")
        self.btn_star.clicked.connect(self._add_bookmark)
        self.btn_hist = self._nav("🕐")
        self.btn_hist.setToolTip("Geçmiş (Ctrl+H)")
        self.btn_hist.clicked.connect(self._toggle_history)
        self.btn_dl = self._nav("↓")
        self.btn_dl.setToolTip("İndirilenler (Ctrl+J)")
        self.btn_dl.clicked.connect(self._toggle_downloads)
        nav_h.addWidget(self.btn_back)
        nav_h.addWidget(self.btn_forward)
        nav_h.addWidget(self.btn_reload)
        nav_h.addSpacing(6)
        nav_h.addWidget(self.url_bar)
        nav_h.addSpacing(4)
        nav_h.addWidget(self.btn_star)
        nav_h.addWidget(self.btn_hist)
        nav_h.addWidget(self.btn_dl)

        # Yer imleri çubuğu — QScrollArea içinde yatay kaydırılabilir
        bm_container = QWidget()
        bm_container.setObjectName("bmBar")
        bm_h = QHBoxLayout(bm_container)
        bm_h.setContentsMargins(4, 0, 4, 0)
        bm_h.setSpacing(0)
        self._bm_layout = bm_h
        bm_scroll = QScrollArea()
        bm_scroll.setWidgetResizable(True)
        bm_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        bm_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        bm_scroll.setFrameShape(QFrame.NoFrame)
        bm_scroll.setFixedHeight(30)
        bm_inner = QWidget()
        self._bm_inner_layout = QHBoxLayout(bm_inner)
        self._bm_inner_layout.setContentsMargins(0, 0, 0, 0)
        self._bm_inner_layout.setSpacing(0)
        self._bm_inner_layout.addStretch()
        bm_scroll.setWidget(bm_inner)
        bm_h.addWidget(bm_scroll)
        add_bm = QPushButton("+")
        add_bm.setObjectName("bmAddBtn")
        add_bm.setToolTip("Mevcut sayfayı ekle")
        add_bm.clicked.connect(self._add_bookmark)
        bm_h.addWidget(add_bm)
        self._refresh_bookmarks()

        # Progress bar — sayfa yüklenirken üstte ince çizgi olarak görünür
        self.progress = QProgressBar()
        self.progress.setObjectName("progress")
        self.progress.setTextVisible(False)
        self.progress.setRange(0, 100)
        self.progress.setVisible(False)  # Başta gizli, yükleme başlayınca görünür

        # QStackedWidget — tüm sekme içerikleri (BrowserPage'ler) burada saklanır
        # setCurrentWidget() ile aktif sekme görünür hale getirilir
        self.stack = QStackedWidget()

        # İndirme bildirim çubuğu — indirme başlayınca altta görünür
        self._dl_bar = QWidget()
        self._dl_bar.setObjectName("dlBar")
        dl_h = QHBoxLayout(self._dl_bar)
        dl_h.setContentsMargins(12, 0, 8, 0)
        dl_h.setSpacing(8)
        self._dl_label = QLabel("")
        self._dl_label.setObjectName("dlLabel")
        dl_close = QPushButton("✕")
        dl_close.setObjectName("dlCloseBtn")
        dl_close.clicked.connect(lambda: self._dl_bar.setVisible(False))
        dl_h.addWidget(self._dl_label)
        dl_h.addStretch()
        dl_h.addWidget(dl_close)
        self._dl_bar.setVisible(False)

        mid_v.addWidget(tab_strip)
        mid_v.addWidget(nav_bar)
        mid_v.addWidget(bm_container)
        mid_v.addWidget(self.progress)
        mid_v.addWidget(self.stack)
        mid_v.addWidget(self._dl_bar)

        # ── Sağ Panel ────────────────────────────────────────────────────────
        # Geçmiş, indirilenler ve ayarlar için ortak panel.
        # İçinde iki scroll area var:
        #   _panel_scroll    → geçmiş ve indirilenler için (setWidget ile içerik değişir)
        #   _settings_scroll → ayarlar için (kalıcı, sadece setVisible ile gösterilir)
        self._panel = QWidget()
        self._panel.setObjectName("panel")
        panel_v = QVBoxLayout(self._panel)
        panel_v.setContentsMargins(0, 0, 0, 0)
        panel_v.setSpacing(0)

        # Panel başlığı (dinamik: "Geçmiş", "İndirilenler", "Ayarlar")
        panel_top = QHBoxLayout()
        panel_top.setContentsMargins(0, 0, 0, 0)
        self._panel_title = QLabel("Geçmiş")
        self._panel_title.setObjectName("panelTitle")
        panel_close = QPushButton("✕")
        panel_close.setObjectName("panelCloseBtn")
        panel_close.clicked.connect(self._close_panel)
        panel_top.addWidget(self._panel_title)
        panel_top.addStretch()
        panel_top.addWidget(panel_close)

        # Geçmiş/indirilenler scroll alanı
        self._panel_scroll = QScrollArea()
        self._panel_scroll.setWidgetResizable(True)
        self._panel_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._panel_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._panel_scroll.setFrameShape(QFrame.NoFrame)
        self._panel_scroll.setStyleSheet(
            "QScrollArea { background: #17161d; }"
            "QScrollBar:vertical { width: 8px; background: #1c1b22; }"
            "QScrollBar::handle:vertical { background: #35343e; border-radius: 4px; }"
        )

        # Geçmiş/indirilenler listesi
        self._panel_list = QListWidget()
        self._panel_list.setObjectName("panelList")
        self._panel_list.itemDoubleClicked.connect(self._panel_item_clicked)

        # Ayarlar scroll alanı (kalıcı — setWidget sadece bir kez çağrılır)
        self._settings_scroll = QScrollArea()
        self._settings_scroll.setWidgetResizable(True)
        self._settings_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._settings_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._settings_scroll.setFrameShape(QFrame.NoFrame)
        self._settings_scroll.setStyleSheet(
            "QScrollArea { background: #17161d; }"
            "QScrollBar:vertical { width: 8px; background: #1c1b22; }"
            "QScrollBar::handle:vertical { background: #35343e; border-radius: 4px; }"
        )

        panel_v.addLayout(panel_top)
        panel_v.addWidget(self._panel_scroll)     # geçmiş / indirilenler
        panel_v.addWidget(self._settings_scroll)  # ayarlar (başta gizli)
        self._panel_scroll.setVisible(True)
        self._settings_scroll.setVisible(False)
        self._panel.setVisible(False)

        # ── Ayarlar İçeriği ──────────────────────────────────────────────────
        # _settings_inner → _settings_scroll'un içindeki widget
        # Bir kez oluşturulur, asla silinmez (setWidget bir kez çağrılır)
        self._settings_inner = QWidget()
        self._settings_inner.setStyleSheet("background: #17161d;")
        self._settings_layout = QVBoxLayout(self._settings_inner)
        self._settings_layout.setContentsMargins(16, 12, 16, 12)
        self._settings_layout.setSpacing(16)

        # Ad Blocker toggle satırı
        ad_block_frame = QHBoxLayout()
        ad_block_label = QLabel("🚫 Reklam Bloker")
        ad_block_label.setStyleSheet("color: #fbfbfe; font-weight: bold; font-size: 13px;")
        self._ad_block_btn = QPushButton("Açık")
        self._ad_block_btn.setStyleSheet(
            "QPushButton { background: #27ae60; color: #fff; border: none; "
            "border-radius: 4px; padding: 6px 12px; font-weight: bold; }"
            "QPushButton:hover { background: #229954; }"
        )
        self._ad_block_btn.setMaximumWidth(80)
        self._ad_block_btn.clicked.connect(self._toggle_ad_blocker)
        ad_block_frame.addWidget(ad_block_label)
        ad_block_frame.addStretch()
        ad_block_frame.addWidget(self._ad_block_btn)
        self._settings_layout.addLayout(ad_block_frame)

        # Smooth Scroll toggle satırı
        smooth_frame = QHBoxLayout()
        smooth_label = QLabel("🎯 Smooth Scroll")
        smooth_label.setStyleSheet("color: #fbfbfe; font-weight: bold; font-size: 13px;")
        self._smooth_btn = QPushButton("Açık")
        self._smooth_btn.setStyleSheet(
            "QPushButton { background: #27ae60; color: #fff; border: none; "
            "border-radius: 4px; padding: 6px 12px; font-weight: bold; }"
            "QPushButton:hover { background: #229954; }"
        )
        self._smooth_btn.setMaximumWidth(80)
        self._smooth_btn.clicked.connect(self._toggle_smooth_scroll)
        smooth_frame.addWidget(smooth_label)
        smooth_frame.addStretch()
        smooth_frame.addWidget(self._smooth_btn)
        self._settings_layout.addLayout(smooth_frame)

        # Dark Mode toggle satırı
        dark_frame = QHBoxLayout()
        dark_label = QLabel("🌙 Auto Dark Mode")
        dark_label.setStyleSheet("color: #fbfbfe; font-weight: bold; font-size: 13px;")
        self._dark_btn = QPushButton("Açık")
        self._dark_btn.setStyleSheet(
            "QPushButton { background: #27ae60; color: #fff; border: none; "
            "border-radius: 4px; padding: 6px 12px; font-weight: bold; }"
            "QPushButton:hover { background: #229954; }"
        )
        self._dark_btn.setMaximumWidth(80)
        self._dark_btn.clicked.connect(self._toggle_dark_mode)
        dark_frame.addWidget(dark_label)
        dark_frame.addStretch()
        dark_frame.addWidget(self._dark_btn)
        self._settings_layout.addLayout(dark_frame)

        # Session Recovery toggle satırı
        session_frame = QHBoxLayout()
        session_label = QLabel("💾 Son Oturumu Geri Yükle")
        session_label.setStyleSheet("color: #fbfbfe; font-weight: bold; font-size: 13px;")
        self._session_btn = QPushButton("Açık")
        self._session_btn.setStyleSheet(
            "QPushButton { background: #27ae60; color: #fff; border: none; "
            "border-radius: 4px; padding: 6px 12px; font-weight: bold; }"
            "QPushButton:hover { background: #229954; }"
        )
        self._session_btn.setMaximumWidth(80)
        self._session_btn.clicked.connect(self._toggle_session_recovery)
        session_frame.addWidget(session_label)
        session_frame.addStretch()
        session_frame.addWidget(self._session_btn)
        self._settings_layout.addLayout(session_frame)

        # Geçmişi temizle butonu
        clear_hist = QPushButton("🗑  Tüm Geçmiş Temizle")
        clear_hist.setStyleSheet(
            "QPushButton { background: #e74c3c; color: #fff; border: none; "
            "border-radius: 4px; padding: 8px 12px; font-weight: bold; }"
            "QPushButton:hover { background: #c0392b; }"
        )
        clear_hist.clicked.connect(self._clear_all_history)
        self._settings_layout.addWidget(clear_hist)

        # Hakkında bilgisi
        about = QLabel(
            " ℹ SwiftX Browser v0.27.1-OpenAlpha\n\n"
            "   Build Date: 4.04.2026\n\n"
            "Hızlı, Güvenli ve Açık Kaynaklı Tarayıcı Denemesi\n\n"
            "✓ Reklam Engelleyici (Ad-Blocker)\n"
            "✓ Smooth Scroller\n"
            "✓ Auto Dark Mode\n"
            "✓ Session Recovery\n"
            "✓ Eklenti Merkezi\n"
            "✓ Yer İmleri & Geçmiş\n"
            "✓ Güvenli Gezinti\n\n"
            "Made with 💜 by YD Studio Team"
        )
        about.setStyleSheet("color: #9e9db5; font-size: 11px; line-height: 1.8; padding: 12px; background: #1c1b22; border-radius: 6px;")
        self._settings_layout.addWidget(about)
        self._settings_layout.addStretch()

        # settings_inner'ı settings_scroll'a bağla (sadece bir kez!)
        self._settings_scroll.setWidget(self._settings_inner)

        root_h.addWidget(self._sidebar)
        root_h.addWidget(mid)
        root_h.addWidget(self._panel)
        self.setCentralWidget(root)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        self.btn_back.clicked.connect(self._go_back)
        self.btn_forward.clicked.connect(self._go_forward)
        self.btn_reload.clicked.connect(self._reload)

        # Klavye kısayolları — QAction ile tanımlanır
        for key, fn in [
            ("Ctrl+T", self._new_tab),
            ("Ctrl+W", self._close_current),
            ("F5", self._reload),
            ("Ctrl+R", self._reload),
            ("Alt+Left", self._go_back),
            ("Alt+Right", self._go_forward),
            ("Ctrl+L", self._focus_url),
            ("Ctrl+B", self._toggle_sidebar),
            ("Ctrl+D", self._add_bookmark),
            ("Ctrl+H", self._toggle_history),
            ("Ctrl+J", self._toggle_downloads),
        ]:
            a = QAction(self)
            a.setShortcut(key)
            a.triggered.connect(fn)
            self.addAction(a)

        # Pencere kapatılırken oturumu kaydet
        self.destroyed.connect(self._save_session)

    def _nav(self, t):
        """Nav bar için standart buton oluşturucu. Kod tekrarını önler."""
        b = QPushButton(t)
        b.setObjectName("navBtn")
        return b

    # ── Sidebar Animasyonu ────────────────────────────────────────────────────

    def _toggle_sidebar(self):
        """
        Sidebar'ı açar/kapatır. Animasyonu başlatır.
        _anim_target → hedef genişlik güncellenir, timer başlar.
        """
        self._sidebar_open = not self._sidebar_open
        self._anim_target = SIDEBAR_W if self._sidebar_open else 0
        self._toggle_btn.setText("☰" if self._sidebar_open else "▶")
        self._anim_timer.start()

    def _anim_step(self):
        """
        Her 8ms'de çağrılır. Sidebar genişliğini hedefe doğru yumuşakça ilerletir.
        Fark 0.5 pikselin altına düşünce animasyon tamamlanmış sayılır.
        diff * 0.07 → easing (başlangıçta hızlı, hedefe yaklaşınca yavaş)
        """
        diff = self._anim_target - self._anim_current
        if abs(diff) < 0.5:
            self._anim_current = float(self._anim_target)
            self._anim_timer.stop()
        else:
            self._anim_current += diff * 0.07
        self._sidebar.setFixedWidth(int(self._anim_current))

    # ── Eklenti Merkezi ───────────────────────────────────────────────────────

    def _open_extensions(self):
        """
        ExtensionStore diyaloğunu açar.
        dialog.exec() → modal, kullanıcı kapatana kadar bekler.
        dialog.changes → değiştirilen eklenti ID'leri ve yeni durumları.
        """
        dialog = ExtensionStore(self._extensions, self)
        if dialog.exec():
            for ext in self._extensions:
                if ext['id'] in dialog.changes:
                    ext['enabled'] = dialog.changes[ext['id']]
            _save(EXTENSIONS_FILE, self._extensions)
            enabled_count = sum(1 for e in self._extensions if e['enabled'])
            self.status.showMessage(
                f"✓ {enabled_count} eklenti aktif, {len(self._extensions) - enabled_count} devre dışı",
                3000
            )

    # ── Yer İmleri ────────────────────────────────────────────────────────────

    def _refresh_bookmarks(self):
        """
        Yer imleri çubuğunu sıfırdan oluşturur.
        Önce mevcut butonları siler (son stretch hariç), sonra yeniden ekler.
        Sağ tıkla yer imi silinebilir (_bm_context).
        """
        while self._bm_inner_layout.count() > 1:
            item = self._bm_inner_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for bm in self._bookmarks:
            btn = QPushButton(bm["title"])
            btn.setObjectName("bmBtn")
            btn.setToolTip(bm["url"])
            url = bm["url"]
            btn.clicked.connect(lambda checked=False, u=url: self._open_url(u))
            btn.setContextMenuPolicy(Qt.CustomContextMenu)
            title = bm["title"]
            btn.customContextMenuRequested.connect(
                lambda pos, t=title: self._bm_context(pos, t)
            )
            self._bm_inner_layout.insertWidget(
                self._bm_inner_layout.count() - 1, btn
            )

    def _add_bookmark(self):
        """
        Aktif sayfayı yer imlerine ekler.
        file:// ve about:blank sayfaları eklenmez.
        Aynı URL zaten varsa uyarı gösterir.
        """
        p = self._cur()
        if not p:
            return
        url = p.url
        title = p.title or url
        if url.startswith("file://") or not url or url == "about:blank":
            return
        if any(b["url"] == url for b in self._bookmarks):
            self.status.showMessage("Bu sayfa zaten yer imlerinde.", 2000)
            return
        self._bookmarks.append({"title": title[:30], "url": url})
        _save(BM_FILE, self._bookmarks)
        self._refresh_bookmarks()
        self.btn_star.setText("★")
        QTimer.singleShot(1500, lambda: self.btn_star.setText("☆"))
        self.status.showMessage(f"'{title[:30]}' yer imlerine eklendi.", 2000)

    def _bm_context(self, pos, title):
        """Yer imi üzerine sağ tıklandığında 'Kaldır' menüsü gösterir."""
        menu = QMenu(self)
        menu.setStyleSheet("QMenu{background:#2a2930;color:#fbfbfe;border:1px solid #45445a;}"
                           "QMenu::item:selected{background:#5b5bef;}")
        rem = menu.addAction("🗑  Kaldır")
        action = menu.exec(QCursor.pos())
        if action == rem:
            self._bookmarks = [b for b in self._bookmarks if b["title"] != title]
            _save(BM_FILE, self._bookmarks)
            self._refresh_bookmarks()

    # ── Geçmiş ────────────────────────────────────────────────────────────────

    def _add_history(self, title, url):
        """
        Geçmişe yeni kayıt ekler.
        file:// ve about:blank URL'leri kaydedilmez.
        Maksimum 500 kayıt tutulur (eski kayıtlar düşer).
        """
        if not url or url.startswith("file://") or url == "about:blank":
            return
        self._history.insert(0, {
            "title": title or url,
            "url": url,
            "time": datetime.now().strftime("%d.%m.%Y %H:%M")
        })
        self._history = self._history[:500]
        _save(HIST_FILE, self._history)

    def _toggle_history(self):
        """
        Geçmiş panelini açar/kapatır.
        Panel zaten geçmiş gösteriyorsa kapatır.
        Açarken _panel_list'e geçmiş kayıtlarını doldurur.
        Container widget → _panel_scroll içine setWidget ile yerleştirilir.
        """
        if self._panel_visible and self._panel_title.text() == "Geçmiş":
            self._close_panel()
            return
        self._panel_title.setText("Geçmiş")
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self._panel_list.clear()
        for h in self._history:
            item = QListWidgetItem(f"  {h['time']}  —  {h['title'][:50]}")
            item.setData(Qt.UserRole, h["url"])  # URL'yi gizli veri olarak sakla
            self._panel_list.addItem(item)
        layout.addWidget(self._panel_list)
        clear_btn = QPushButton("Tümünü Temizle")
        clear_btn.setObjectName("clearBtn")
        clear_btn.clicked.connect(self._clear_panel)
        layout.addWidget(clear_btn)
        if self._panel_scroll.widget() is self._settings_inner:
            self._settings_inner.setParent(None)
        self._panel_scroll.setWidget(container)
        self._settings_scroll.setVisible(False)
        self._panel_scroll.setVisible(True)
        self._panel.setVisible(True)
        self._panel_visible = True

    # ── İndirilenler ──────────────────────────────────────────────────────────

    def _toggle_downloads(self):
        """
        İndirilenler panelini açar/kapatır.
        Geçmiş paneline benzer şekilde çalışır.
        item.data(Qt.UserRole) → dosyanın disk yolunu saklar.
        """
        if self._panel_visible and self._panel_title.text() == "İndirilenler":
            self._close_panel()
            return
        self._panel_title.setText("İndirilenler")
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self._panel_list.clear()
        for d in self._downloads:
            item = QListWidgetItem(f"  {d['time']}  —  {d['name']}")
            item.setData(Qt.UserRole, d.get("path", ""))
            self._panel_list.addItem(item)
        layout.addWidget(self._panel_list)
        clear_btn = QPushButton("Tümünü Temizle")
        clear_btn.setObjectName("clearBtn")
        clear_btn.clicked.connect(self._clear_panel)
        layout.addWidget(clear_btn)
        if self._panel_scroll.widget() is self._settings_inner:
            self._settings_inner.setParent(None)
        self._panel_scroll.setWidget(container)
        self._settings_scroll.setVisible(False)
        self._panel_scroll.setVisible(True)
        self._panel.setVisible(True)
        self._panel_visible = True

    # ── Ayarlar ───────────────────────────────────────────────────────────────

    def _toggle_settings(self):
        """
        Ayarlar panelini açar/kapatır.
        _settings_scroll → sadece setVisible ile gösterilir/gizlenir.
        _panel_scroll → gizlenir (geçmiş/indirilenler alanı)
        Bu yaklaşım sayesinde _settings_inner hiçbir zaman silinmez.
        """
        if self._panel_visible and self._panel_title.text() == "Ayarlar":
            self._close_panel()
            return
        self._panel_title.setText("Ayarlar")
        self._panel_scroll.setVisible(False)
        self._settings_scroll.setVisible(True)
        self._panel.setVisible(True)
        self._panel_visible = True

    def _toggle_ad_blocker(self):
        """Ad blocker'ı açar/kapatır ve buton rengini günceller."""
        self._ad_blocker.enabled = not self._ad_blocker.enabled
        state = "Açık" if self._ad_blocker.enabled else "Kapalı"
        color = "#27ae60" if self._ad_blocker.enabled else "#e74c3c"
        hover_color = "#229954" if self._ad_blocker.enabled else "#c0392b"
        self._ad_block_btn.setText(state)
        self._ad_block_btn.setStyleSheet(
            f"QPushButton {{ background: {color}; color: #fff; border: none; "
            f"border-radius: 4px; padding: 6px 12px; font-weight: bold; }}"
            f"QPushButton:hover {{ background: {hover_color}; }}"
        )
        self.status.showMessage(f"🚫 Reklam Bloker {state}", 2000)

    def _toggle_smooth_scroll(self):
        """
        Smooth scroll'u açar/kapatır.
        Not: Değişiklik yalnızca yeni açılan sekmelerde geçerli olur.
        Mevcut sekmelerin script'leri zaten enjekte edilmiştir.
        """
        self._smooth_scroll = not self._smooth_scroll
        state = "Açık" if self._smooth_scroll else "Kapalı"
        color = "#27ae60" if self._smooth_scroll else "#e74c3c"
        hover_color = "#229954" if self._smooth_scroll else "#c0392b"
        self._smooth_btn.setText(state)
        self._smooth_btn.setStyleSheet(
            f"QPushButton {{ background: {color}; color: #fff; border: none; "
            f"border-radius: 4px; padding: 6px 12px; font-weight: bold; }}"
            f"QPushButton:hover {{ background: {hover_color}; }}"
        )
        self.status.showMessage(f"🎯 Smooth Scroll {state} (Yeni sekmelerde geçerli)", 2000)

    def _toggle_dark_mode(self):
        """
        Auto dark mode'u açar/kapatır.
        Not: Değişiklik yalnızca yeni açılan sekmelerde geçerli olur.
        """
        self._dark_mode = not self._dark_mode
        state = "Açık" if self._dark_mode else "Kapalı"
        color = "#27ae60" if self._dark_mode else "#e74c3c"
        hover_color = "#229954" if self._dark_mode else "#c0392b"
        self._dark_btn.setText(state)
        self._dark_btn.setStyleSheet(
            f"QPushButton {{ background: {color}; color: #fff; border: none; "
            f"border-radius: 4px; padding: 6px 12px; font-weight: bold; }}"
            f"QPushButton:hover {{ background: {hover_color}; }}"
        )
        self.status.showMessage(f"🌙 Auto Dark Mode {state} (Yeni sekmelerde geçerli)", 2000)

    def _toggle_session_recovery(self):
        """Session recovery'yi açar/kapatır. Etki bir sonraki açılışta görülür."""
        self._restore_session = not self._restore_session
        state = "Açık" if self._restore_session else "Kapalı"
        color = "#27ae60" if self._restore_session else "#e74c3c"
        hover_color = "#229954" if self._restore_session else "#c0392b"
        self._session_btn.setText(state)
        self._session_btn.setStyleSheet(
            f"QPushButton {{ background: {color}; color: #fff; border: none; "
            f"border-radius: 4px; padding: 6px 12px; font-weight: bold; }}"
            f"QPushButton:hover {{ background: {hover_color}; }}"
        )
        self.status.showMessage(f"💾 Session Recovery {state}", 2000)

    def _clear_all_history(self):
        """Geçmişi ve indirme geçmişini hem bellekten hem JSON dosyasından siler."""
        self._history = []
        self._downloads = []
        _save(HIST_FILE, self._history)
        _save(DL_FILE, self._downloads)
        self.status.showMessage("✓ Geçmiş ve indirilenler temizlendi", 2000)

    def _handle_permission(self, permission: QWebEnginePermission):
        """
        Sayfa izin istediğinde çağrılır (kamera, mikrofon, konum, bildirim).
        granted listesindeki izin türleri otomatik kabul edilir.
        Diğerleri reddedilir.
        """
        print(f"[İZİN] type={permission.permissionType()} origin={permission.origin().toString()}")
        granted = [
            QWebEnginePermission.PermissionType.MediaAudioCapture,
            QWebEnginePermission.PermissionType.MediaVideoCapture,
            QWebEnginePermission.PermissionType.MediaAudioVideoCapture,
            QWebEnginePermission.PermissionType.Notifications,
            QWebEnginePermission.PermissionType.Geolocation,
            QWebEnginePermission.PermissionType.ClipboardReadWrite,
        ]
        names = {
            QWebEnginePermission.PermissionType.MediaAudioCapture: "Mikrofon",
            QWebEnginePermission.PermissionType.MediaVideoCapture: "Kamera",
            QWebEnginePermission.PermissionType.MediaAudioVideoCapture: "Kamera+Mikrofon",
            QWebEnginePermission.PermissionType.Notifications: "Bildirimler",
            QWebEnginePermission.PermissionType.Geolocation: "Konum",
            QWebEnginePermission.PermissionType.ClipboardReadWrite: "Pano",
        }
        ptype = permission.permissionType()
        if ptype in granted:
            permission.grant()
            label = names.get(ptype, "İzin")
            host  = permission.origin().host() or "sayfa"
            self.status.showMessage(f"✓ {host} → {label} izni verildi", 3000)
        else:
            permission.deny()

    def _handle_download(self, dl: QWebEngineDownloadRequest):
        """
        İndirme isteği geldiğinde çağrılır.
        ~/Downloads klasörü varsa oraya, yoksa ana dizine indirir.
        isFinishedChanged sinyali → indirme tamamlandığında kayıt ekler ve bildirimi günceller.
        """
        dl_dir = os.path.expanduser("~/Downloads")
        if not os.path.exists(dl_dir):
            dl_dir = os.path.expanduser("~")
        path = os.path.join(dl_dir, dl.suggestedFileName())
        dl.setDownloadDirectory(dl_dir)
        dl.setDownloadFileName(dl.suggestedFileName())
        dl.accept()
        name = dl.suggestedFileName()
        self._dl_label.setText(f"⬇  İndiriliyor: {name}")
        self._dl_bar.setVisible(True)

        def on_finish():
            record = {
                "name": name,
                "path": path,
                "time": datetime.now().strftime("%d.%m.%Y %H:%M")
            }
            self._downloads.insert(0, record)
            _save(DL_FILE, self._downloads)
            self._dl_label.setText(f"✓  İndirildi: {name}")
            QTimer.singleShot(4000, lambda: self._dl_bar.setVisible(False))

        dl.isFinishedChanged.connect(lambda: on_finish() if dl.isFinished() else None)

    def _close_panel(self):
        """Sağ paneli kapatır ve durum değişkenini günceller."""
        self._panel.setVisible(False)
        self._panel_visible = False

    def _panel_item_clicked(self, item):
        """
        Geçmiş veya indirilenler listesinde çift tıklandığında çağrılır.
        item.data(Qt.UserRole) → URL veya dosya yolu
        """
        url = item.data(Qt.UserRole)
        if url:
            self._open_url(url)

    def _clear_panel(self):
        """
        Panelin başlığına göre geçmiş veya indirmeleri temizler.
        Hem bellekten hem JSON dosyasından siler.
        """
        if self._panel_title.text() == "Geçmiş":
            self._history = []
            _save(HIST_FILE, self._history)
        elif self._panel_title.text() == "İndirilenler":
            self._downloads = []
            _save(DL_FILE, self._downloads)
        self._panel_list.clear()

    # ── Sekme Bağlam Menüsü ───────────────────────────────────────────────────

    def _tab_context_menu(self, pos, idx):
        """
        Sekme üzerine sağ tıklandığında bağlam menüsü gösterir.
        Renk grubu, sabitleme, kopyalama ve kapatma seçenekleri sunar.
        action.data() → renk adı (TAB_COLORS'dan)
        """
        menu = QMenu(self)
        menu.setStyleSheet("QMenu{background:#2a2930;color:#fbfbfe;border:1px solid #45445a;padding:4px;}"
                           "QMenu::item{padding:6px 20px;border-radius:4px;}"
                           "QMenu::item:selected{background:#5b5bef;}")
        color_menu = menu.addMenu("🎨  Grup rengi")
        color_menu.setStyleSheet(menu.styleSheet())
        for name, (bg, fg) in TAB_COLORS.items():
            label = f"{'●  ' if bg else '○  '}{name.capitalize()}"
            act = color_menu.addAction(label)
            act.setData(name)
        pin_act  = menu.addAction("📌  Sabitle")
        dup_act  = menu.addAction("⧉  Kopyala")
        menu.addSeparator()
        close_act = menu.addAction("✕  Kapat")

        action = menu.exec(QCursor.pos())
        if not action:
            return
        if action == close_act:
            self._close(idx)
        elif action == dup_act:
            url = self._tabs[idx][1].url
            self._new_tab(url)
        elif action.data() in TAB_COLORS:
            self._tabs[idx][0].set_color(action.data())

    # ── Sekme Yönetimi ────────────────────────────────────────────────────────

    def _new_tab(self, url=None):
        """
        Yeni sekme oluşturur ve sekme şeridine ekler.
        idx → yeni sekmenin indeksi (mevcut uzunluk)
        insertWidget → yeni sekme '+' butonundan önce eklenir
        Sinyal bağlantıları: titleChanged, urlChanged, loadProgress, loadFinished
        """
        idx  = len(self._tabs)
        page = BrowserPage(
            url or self.HOME,
            smooth_scroll=self._smooth_scroll,
            dark_mode=self._dark_mode
        )
        tw   = TabWidget(
            on_click=lambda chk=False, i=idx: self._switch(i),
            on_close=lambda chk=False, i=idx: self._close(i),
            on_right_click=lambda pos, i=idx: self._tab_context_menu(pos, i),
        )
        self._tl.insertWidget(self._tl.count() - 2, tw)
        self.stack.addWidget(page)
        self._tabs.append((tw, page))

        page.view.titleChanged.connect(lambda t, i=idx: self._on_title(t, i))
        page.view.urlChanged.connect(lambda u, i=idx: self._on_url(u, i))
        page.view.loadProgress.connect(self._on_progress)
        page.view.loadFinished.connect(self._on_finish)
        page.view.page().linkHovered.connect(self.status.showMessage)
        page.view.page().profile().downloadRequested.connect(self._handle_download)
        page.view.page().permissionRequested.connect(self._handle_permission)
        self._switch(idx)

    def _switch(self, idx):
        """
        İstenen sekmeye geçer.
        Önceki aktif sekmeyi pasif yapar, yenisini aktif yapar.
        stack.setCurrentWidget → görünür içeriği değiştirir.
        url_bar → yeni sekmenin URL'si ile güncellenir.
        """
        if not (0 <= idx < len(self._tabs)):
            return
        if 0 <= self._active < len(self._tabs):
            self._tabs[self._active][0].set_active(False)
        self._active = idx
        self._tabs[idx][0].set_active(True)
        self.stack.setCurrentWidget(self._tabs[idx][1])
        self.url_bar.setText(self._tabs[idx][1].url)

    def _close(self, idx):
        """
        Sekmeyi kapatır.
        Son sekme kapatılmaya çalışılırsa ana sayfaya döner (sekmeyi silmez).
        _rewire() → kalan sekmelerin indeks bağlantılarını yeniden kurar.
        """
        if len(self._tabs) <= 1:
            self._tabs[0][1].view.load(QUrl(self.HOME))
            return
        tw, page = self._tabs.pop(idx)
        self._tl.removeWidget(tw)
        tw.deleteLater()
        self.stack.removeWidget(page)
        page.deleteLater()
        self._rewire()
        self._active = -1
        self._switch(min(idx, len(self._tabs) - 1))

    def _rewire(self):
        """
        Sekme kapatıldıktan sonra kalan sekmelerin sinyal bağlantılarını günceller.
        Disconnect → önceki bağlantıyı kopar (hata verirse geç)
        Connect → yeni indeksle yeniden bağlar
        Bu olmadan yanlış sekmeye tıklanır/kapatılır.
        """
        for i, (tw, _) in enumerate(self._tabs):
            try:
                tw.btn.clicked.disconnect()
            except:
                pass
            tw.btn.clicked.connect(lambda chk=False, i=i: self._switch(i))
            try:
                tw.close_btn.clicked.disconnect()
            except:
                pass
            tw.close_btn.clicked.connect(lambda chk=False, i=i: self._close(i))
            try:
                tw.btn.customContextMenuRequested.disconnect()
            except:
                pass
            tw.btn.customContextMenuRequested.connect(
                lambda pos, i=i: self._tab_context_menu(pos, i)
            )

    def _close_current(self):
        """Aktif sekmeyi kapatır. Ctrl+W kısayoluna bağlıdır."""
        self._close(self._active)

    def _cur(self):
        """
        Aktif BrowserPage'i döndürür.
        _active geçersizse None döner.
        Pek çok fonksiyon 'if p := self._cur()' ile kullanır.
        """
        return self._tabs[self._active][1] if 0 <= self._active < len(self._tabs) else None

    # ── Sinyal İşleyicileri ───────────────────────────────────────────────────

    def _on_title(self, t, idx):
        """Sayfa başlığı değiştiğinde sekme adını ve pencere başlığını günceller."""
        if idx < len(self._tabs):
            self._tabs[idx][0].set_title(t)
        if idx == self._active:
            self.setWindowTitle(f"{t} — SwiftX")

    def _on_url(self, u, idx):
        """URL değiştiğinde (sayfa yüklenirken de) URL çubuğunu günceller."""
        if idx == self._active:
            self.url_bar.setText(u.toString())

    def _on_progress(self, v):
        """Yükleme ilerlemesini progress bar'a yansıtır. %100 olunca gizlenir."""
        self.progress.setVisible(v < 100)
        self.progress.setValue(v)

    def _on_finish(self, ok):
        """
        Sayfa yüklemesi tamamlandığında çağrılır.
        ok=False → yükleme başarısız (bağlantı yok, 404 vb.)
        Başarılıysa geçmişe ekler.
        """
        self.progress.setVisible(False)
        if not ok:
            self.status.showMessage("Sayfa yüklenemedi.", 3000)
            return
        p = self._cur()
        if p:
            self._add_history(p.title, p.url)

    # ── Gezinti ───────────────────────────────────────────────────────────────

    def _navigate(self):
        """
        URL çubuğundan gezinti yapar.
        http/https/file → direkt yükle
        Nokta içerip boşluk içermiyorsa → https:// ekleyerek yükle
        Diğer durumlarda → Google araması yap
        """
        t = self.url_bar.text().strip()
        if not t:
            return
        if t.startswith(("http://", "https://", "file://")):
            url = t
        elif "." in t and " " not in t:
            url = "https://" + t
        else:
            url = "https://www.google.com/search?q=" + t.replace(" ", "+")
        if p := self._cur():
            p.view.load(QUrl(url))

    def _open_url(self, url):
        """Verilen URL'yi aktif sekmede açar. Geçmiş/yer imi tıklamalarında kullanılır."""
        if p := self._cur():
            p.view.load(QUrl(url))

    def _go_back(self):
        """Aktif sayfada geri gider."""
        if p := self._cur():
            p.view.back()

    def _go_forward(self):
        """Aktif sayfada ileri gider."""
        if p := self._cur():
            p.view.forward()

    def _reload(self):
        """Aktif sayfayı yeniler."""
        if p := self._cur():
            p.view.reload()

    def _go_home(self):
        """Aktif sekmede ana sayfaya gider."""
        if p := self._cur():
            p.view.load(QUrl(self.HOME))

    def _focus_url(self):
        """URL çubuğuna odaklanır ve tüm metni seçer. Ctrl+L kısayoluna bağlıdır."""
        self.url_bar.setFocus()
        self.url_bar.selectAll()


# ══════════════════════════════════════════════════════════════════════════════
# UYGULAMA GİRİŞ NOKTASI
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import os

    # Chromium GPU/sandbox bayrakları
    # --disable-gpu-sandbox    → sanal makine/bazı Linux sistemlerinde GPU sandbox sorununu önler
    # --ignore-gpu-blacklist   → kara listedeki GPU'ları zorla kullan
    # --enable-features=VizDisplayCompositor → modern compositor etkinleştir
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
        "--disable-gpu-sandbox "
        "--ignore-gpu-blacklist "
        "--enable-features=VizDisplayCompositor"
    )

    # QApplication → Qt olay döngüsünün başlatıldığı yer
    # sys.argv → komut satırı argümanlarını Qt'ye iletir
    app = QApplication(sys.argv)
    app.setApplicationName("SwiftX Browser")

    # Varsayılan profil ayarları — tüm sekmelere uygulanır
    profile = QWebEngineProfile.defaultProfile()
    profile.setHttpUserAgent(
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
    )
    # AllowPersistentCookies → çerezler uygulama kapanınca silinmez
    profile.setPersistentCookiesPolicy(
        QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies
    )

    # Ana pencereyi oluştur, göster ve olay döngüsünü başlat
    # sys.exit → döngü bittiğinde programı temiz çıkış koduyla kapatır
    MainWindow().show()
    sys.exit(app.exec())
