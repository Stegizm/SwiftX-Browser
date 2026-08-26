n<div align="center">

# SwiftX Browser

**A lightweight, fast, and feature-packed web browser powered by Python & PySide6.**

*Python ve PySide6 ile geliştirilmiş; hafif, hızlı ve özellik zengini web tarayıcısı.*

[![Version](https://img.shields.io/badge/version-v0.29-purple.svg?style=for-the-badge)](../../releases)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Qt](https://img.shields.io/badge/PySide6-Qt%206-41CD52?style=for-the-badge&logo=qt&logoColor=white)](https://qt.io)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

[English](#english) • [Türkçe](#türkçe) • [Installation / Kurulum](#build-from-source--kaynaktan-derleme)

</div>

---

> [!IMPORTANT]
> **Language Support Note / Dil Desteği Notu**
> Currently, the user interface and menus are primarily available in **Turkish**. English localization is planned for upcoming releases.

---

## English

### Overview
SwiftX is a modern, lightweight desktop web browser built on top of Qt WebEngine. Designed with efficiency in mind, it provides essential browsing features out of the box without the overhead of heavy bloatware.

### Key Features
* **Built-in Ad Blocker:** Blocks unwanted ads, tracking scripts, and malicious domains.
* **Smooth Scrolling:** Enhanced scrolling experience tailored for modern displays.
* **Auto Dark Mode:** Applies dark themes to web pages for comfortable night browsing.
* **Session Recovery:** Restores your open tabs and windows after an unexpected restart.
* **Extension Center:** Manage custom browser extensions easily.
* **Bookmarks & History:** Organize your favorite pages and view browsing history.
* **Privacy & Safety:** Configured for isolated persistent data and secure browsing.

---

## Türkçe

### Genel Bakış
SwiftX, Qt WebEngine mimarisi üzerine inşa edilmiş modern ve hafif bir masaüstü web tarayıcısıdır. Sistem kaynaklarını minimum düzeyde kullanırken ihtiyaç duyduğunuz tüm temel web özelliklerini sunar.

### Öne Çıkan Özellikler
* **Dahili Reklam Engelleyici:** Reklamları, izleyicileri ve zararlı alan adlarını otomatik engeller.
* **Akıcı Kaydırma (Smooth Scroll):** Web sayfalarında takılmasız ve yumuşak gezinme deneyimi.
* **Otomatik Karanlık Mod:** Sayfaları karanlık temaya zorlayarak göz yorgunluğunu azaltır.
* **Oturum Kurtarma:** Beklenmeyen kapanmalarda sekmelerinizi otomatik geri yükler.
* **Eklenti Merkezi:** Özel eklentilerinizi kolayca yönetin.
* **Yer İmleri ve Geçmiş:** Sık ziyaret edilen siteleri depolayın ve geçmişi yönetin.
* **Gizlilik ve Güvenlik:** Çerezler ve oturum verileri için izolasyonlu güvenli veri yapısı.

---

## Project Structure

```text
swiftx/
├── browser.py              # Application entry point & Qt initialization
├── SwiftX.spec             # PyInstaller build specification
├── core/                   # Shared backend components
│   ├── constants.py        # App-wide constants & paths
│   ├── storage.py          # JSON file I/O operations
│   ├── styles.py           # Qt QSS stylesheets
│   └── services/           # Core business logic managers
│       ├── bookmark_manager.py
│       ├── download_manager.py
│       ├── history_manager.py
│       └── settings_manager.py
├── engine/                 # Web Engine layer
│   ├── ad_blocker.py       # Custom ad-blocking logic
│   ├── browserpage.py      # Custom QWebEngineView implementation
│   └── scripts.py          # JS / CSS code injections
├── ui/                     # User interface widgets
│   ├── bookmark_bar.py     # Bookmark panel widget
│   ├── extension_store.py  # Extension dialog window
│   ├── settings_panel.py   # Settings layout
│   ├── side_panel.py       # Sliding drawer side panel
│   ├── sidebar.py          # Vertical quick bar
│   ├── tab_bar.py          # Custom tab bar styling
│   └── tab_widget.py       # Tab management container
├── windows/                # Window controllers
│   └── main_window.py      # Main application window & event wiring
└── data/                   # Default start page & app assets
---

## Build from Source / Kaynaktan Derleme

### Prerequisites / Önkoşullar

* Python 3.9+
* Git

### Steps / Adımlar

1. **Clone the repository:**
```bash
git clone [https://github.com/username/swiftx-browser.git](https://github.com/username/swiftx-browser.git)
cd swiftx-browser

```


2. **Install dependencies:**
```bash
pip install PySide6 pyinstaller

```


3. **Run in development mode:**
```bash
python browser.py

```


4. **Build binary executable:**
```bash
pyinstaller SwiftX.spec

```

*The compiled standalone output will be generated inside the `dist/SwiftX/` folder.*

---

## License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

Made with 💜 by **YD Studio Team**