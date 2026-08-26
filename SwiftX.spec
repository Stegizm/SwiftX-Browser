# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec - SwiftX Browser v0.29

Kullanım:
    pyinstaller SwiftX.spec
"""
import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

block_cipher = None

# Qt WebEngine ve PySide6 veri dosyalarını garantiye al
pyside6_datas = collect_data_files("PySide6")

a = Analysis(
    ["browser.py"],
    pathex=[os.path.abspath(".")],
    binaries=[],
    datas=[
        ("data", "data"),
    ] + pyside6_datas,
    hiddenimports=[
        # Core paketleri
        "core",
        "core.constants",
        "core.storage",
        "core.styles",
        "core.services",
        "core.services.bookmark_manager",
        "core.services.history_manager",
        "core.services.download_manager",
        "core.services.settings_manager",
        # Engine paketleri
        "engine",
        "engine.browserpage",
        "engine.scripts",
        "engine.ad_blocker",
        # UI paketleri
        "ui",
        "ui.tab_bar",
        "ui.tab_widget",
        "ui.side_panel",
        "ui.sidebar",
        "ui.settings_panel",
        "ui.bookmark_bar",
        "ui.extension_store",
        # Windows paketleri
        "windows",
        "windows.main_window",
        # PySide6 & WebEngine kritik bağımlılıkları
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "PySide6.QtWebEngineCore",
        "PySide6.QtWebEngineWidgets",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["matplotlib", "numpy", "scipy", "PIL", "tkinter"],
    noarchive=False,
)

pyz = PYZ(a.pure, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="SwiftX",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI uygulaması — konsol penceresini gizle
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="SwiftX",
)