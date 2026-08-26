# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec — SwiftX Browser v0.28.1

Kullanım:
    pyinstaller SwiftX.spec
"""
import os
import sys
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Uygulama kök dizini
a = Analysis(
    ["browser.py"],
    pathex=[os.path.abspath(".")],
    binaries=[],
    datas=[
        ("data", "data"),
    ],
    hiddenimports=[
        "core",
        "core.services",
        "core.services.bookmark_manager",
        "core.services.history_manager",
        "core.services.download_manager",
        "core.services.settings_manager",
        "engine",
        "engine.browserpage",
        "engine.scripts",
        "engine.ad_blocker",
        "ui",
        "ui.tab_bar",
        "ui.tab_widget",
        "ui.side_panel",
        "ui.sidebar",
        "ui.settings_panel",
        "ui.bookmark_bar",
        "ui.extension_store",
        "windows",
        "windows.main_window",
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
    console=False,      # GUI uygulaması — konsol gösterme
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,           # "data/SXBETALOGO3.png" (Windows .ico gerektirir)
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
