# SwiftX.spec
# Baştan yapılandırılmış, hata gidermeye odaklı onedir spec dosyası

import os
import sys
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None
proje_dizini = os.path.abspath('.')

# Tüm alt modülleri otomatik olarak topla (Manuel yazım hatasını önler)
gizli_moduller = collect_submodules('windows') + \
                 collect_submodules('ui') + \
                 collect_submodules('engine') + \
                 collect_submodules('core') + \
                 ['PySide6.QtWebEngineWidgets', 'PySide6.QtWebEngineCore']

a = Analysis(
    ['browser.py'],
    pathex=[proje_dizini],
    binaries=[],
    datas=[
        ('data', 'data'),               # data klasörünü olduğu gibi kopyalar
        ('windows', 'windows'),         # windows klasörünü ana dizine ekler
        ('ui', 'ui'),                   # ui klasörünü ana dizine ekler
        ('engine', 'engine'),           # engine klasörünü ana dizine ekler
        ('core', 'core'),               # core klasörünü ana dizine ekler
    ],
    hiddenimports=gizli_moduller,       # Otomatik toplanan modülleri ekler
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,              # onedir modu için gereklidir
    name='SwiftX',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,                      # GUI uygulaması olduğu için konsol kapalı
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='SXBETALOGO3.ico',             # İkon dosyası
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SwiftX',                      # dist/SwiftX/ altında toplanır
)
