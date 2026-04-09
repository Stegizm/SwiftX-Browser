# SwiftX.spec
# PyInstaller spec dosyası — onedir
# Tek exe yerine klasör yapısı üretir, daha hızlı ve kararlı çalışır

import os
block_cipher = None

a = Analysis(
    ['browser.py'],
    pathex=[os.path.abspath('.')],          # proje kök dizini her zaman aranır
    binaries=[],
    datas=[
        ('data/bg.jpg', 'data'),
        ('data/home (v6).html', 'data'),
        ('data/SXBETALOGO3.png', 'data'),
    ],
    hiddenimports=[
        'PySide6.QtWebEngineWidgets',
        'PySide6.QtWebEngineCore',
        'windows.main_window',
        'ui.tab_widget',
        'ui.extension_store',
        'ui.side_panel',
        'engine.browser_page',
        'engine.ad_blocker',
        'engine.scripts',
        'core.constants',
        'core.storage',
        'core.styles',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,   # onedir için True olmalı
    name='SwiftX',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='SXBETALOGO3.ico',
)

# COLLECT → onedir modunu etkinleştirir, tüm dosyaları dist/SwiftX/ altında toplar
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SwiftX',
)
