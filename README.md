# SwiftX Browser

> A lightweight browser built with Python & PySide6.

> Python & PySide6 ile geliştirilmiş hafif bir tarayıcı.

---

> [!WARNING]
> **For Global Users**
> This browser was primarily developed in Turkish. The UI, menus, and settings are in Turkish. English localization is not available yet.

---

## 🇬🇧 English

### About
SwiftX is a lightweight browser project built on Qt WebEngine.

**Current version:** `v0.28`

### Features
- 🚫 Ad Blocker
- 🎯 Smooth Scroll
- 🌙 Auto Dark Mode
- 💾 Session Recovery
- 🧩 Extension Center
- ⭐ Bookmarks & History
- 🔒 Safe Browsing

### Downloads
Go to [Releases](../../releases) for pre-built binaries (Windows & Linux).

### Build from Source
```bash
pip install PySide6 pyinstaller
pyinstaller SwiftX.spec
```
The output will be in `dist/SwiftX/`.

### Project Structure
```
swiftx/
├── browser.py              ← Entry point
├── core/
│   ├── constants.py        ← App-wide constants
│   ├── storage.py          ← JSON load/save helpers
│   ├── styles.py           ← Qt stylesheets
│   └── services/           ← Business logic (v0.28)
│       ├── bookmark_manager.py
│       ├── history_manager.py
│       ├── download_manager.py
│       └── settings_manager.py
├── engine/
│   ├── scripts.py          ← JS/CSS injection strings
│   ├── ad_blocker.py       ← AdBlocker class
│   └── browserpage.py      ← BrowserPage + SmoothScroller
├── ui/
│   ├── tab_widget.py       ← Tab button widget
│   ├── sidebar.py          ← Sidebar with animation
│   ├── settings_panel.py   ← Settings panel content
│   ├── bookmark_bar.py     ← Bookmark bar widget
│   ├── extension_store.py  ← Extension store dialog
│   └── side_panel.py       ← History/Downloads/Settings panel
├── windows/
│   └── main_window.py      ← Main window (coordinator)
├── data/                   ← Home page & assets
├── .github/workflows/      ← CI/CD (auto release)
└── SwiftX.spec             ← PyInstaller build config
```

---

## 🇹🇷 Türkçe

### Hakkında
SwiftX, Qt WebEngine üzerine inşa edilmiş hafif bir tarayıcı projesidir.

**Mevcut sürüm:** `v0.28`

### Özellikler
- 🚫 Reklam Engelleyici
- 🎯 Smooth Scroll
- 🌙 Otomatik Karanlık Mod
- 💾 Oturum Kurtarma
- 🧩 Eklenti Merkezi
- ⭐ Yer İmleri & Geçmiş
- 🔒 Güvenli Gezinti

### İndirme
Hazır derlenmiş dosyalar için [Releases](../../releases) sayfasına gidin.

### Kaynaktan Derleme
```bash
pip install PySide6 pyinstaller
```
Çıktı `dist/SwiftX/` dizininde olacaktır.

### Notlar
- MIT lisansı ile açık kaynaklıdır.
- Linux ve Windows için hazır release mevcuttur.

---

<p align="center">
  Made with 💜 by YD Studio Team
</p>
