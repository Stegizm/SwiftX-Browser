# SwiftX.spec
# PyInstaller spec dosyası — onedir modu
# Tek exe yerine klasör yapısı üretir, daha hızlı ve kararlı çalışır

a = Analysis(
    ['browser (v27).py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

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
