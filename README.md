# SwiftX Browser

> A personal experiment — a lightweight browser built with Python & PySide6.

> Kişisel bir deney — Python & PySide6 ile geliştirilmiş hafif bir tarayıcı.

---

> [!WARNING]
> **For Global Users**
> This browser was primarily developed in Turkish. The UI, menus, and settings are in Turkish. English localization is not available yet.

---

## 🇬🇧 English

### About
SwiftX is a hobby browser project built on top of Qt WebEngine. It started as a personal experiment to learn how browsers work under the hood.

**Current version:** `v0.27.2-alpha`

### Features
- 🚫 Ad Blocker
- 🎯 Smooth Scroll
- 🌙 Auto Dark Mode
- 💾 Session Recovery
- 🧩 Extension Center
- ⭐ Bookmarks & History
- 🔒 Safe Browsing
- (...)

### Requirements
- Python 3.10+
- PySide6

### Project Structure
```
swiftx/
├── browser.py              ← Entry point
├── core/
│   ├── constants.py        ← App-wide constants, file paths, colors
│   ├── storage.py          ← JSON load/save helpers
│   └── styles.py           ← Qt stylesheets
├── engine/
│   ├── scripts.py          ← JS/CSS injection strings
│   ├── ad_blocker.py       ← AdBlocker class
│   └── browser_page.py     ← BrowserPage + SmoothScroller
├── ui/
│   ├── tab_widget.py       ← Tab button widget
│   ├── extension_store.py  ← Extension store dialog
│   └── side_panel.py       ← History/Downloads/Settings panel
└── windows/
    └── main_window.py      ← Main window (coordinator)
```

### Installation (Optional / for developers)
```bash
pip install -r requirements.txt
python browser.py
```

### Notes
- This is an open alpha — expect bugs and missing features.
- Built and tested on Linux. Windows/macOS support is not guaranteed.

---

## 🇹🇷 Türkçe

### Hakkında
SwiftX, Qt WebEngine üzerine inşa edilmiş bir hobi tarayıcı projesidir. Tarayıcıların arka planda nasıl çalıştığını öğrenmek için kişisel bir deney olarak başladı.

**Mevcut sürüm:** `v0.27.2-alpha`

### Özellikler
- 🚫 Reklam Engelleyici
- 🎯 Smooth Scroll
- 🌙 Otomatik Karanlık Mod
- 💾 Oturum Kurtarma
- 🧩 Eklenti Merkezi
- ⭐ Yer İmleri & Geçmiş
- 🔒 Güvenli Gezinti
- (...)

### Gereksinimler
- Python 3.10+
- PySide6

### Proje Yapısı
```
swiftx/
├── browser.py              ← Giriş noktası
├── core/
│   ├── constants.py        ← Sabitler, dosya yolları, renkler
│   ├── storage.py          ← JSON yükleme/kaydetme yardımcıları
│   └── styles.py           ← Qt stylesheet stringleri
├── engine/
│   ├── scripts.py          ← JS/CSS injection stringleri
│   ├── ad_blocker.py       ← AdBlocker sınıfı
│   └── browser_page.py     ← BrowserPage + SmoothScroller
├── ui/
│   ├── tab_widget.py       ← Sekme butonu widget'ı
│   ├── extension_store.py  ← Eklenti merkezi diyalogu
│   └── side_panel.py       ← Geçmiş/İndirilenler/Ayarlar paneli
└── windows/
    └── main_window.py      ← Ana pencere (koordinatör)
```

### Kurulum (Opsiyonel / geliştiriciler için)
```bash
pip install -r requirements.txt
python browser.py
```

### Notlar
- Bu bir açık alfa sürümüdür — hatalar ve eksik özellikler olabilir.
- Linux üzerinde geliştirildi ve test edildi. Windows/macOS desteği garanti değildir.

---

<p align="center">
  Made with 💜 by YD Studio Team
</p>
