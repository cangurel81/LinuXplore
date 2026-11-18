# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller derleme tanımı.

Kullanım: pyinstaller LinuXplore.spec --noconfirm --clean
Çıktı: dist/LinuXplore.exe
"""

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    # Veri dosyaları exe içine gömülmeli; aksi hâlde katalog boş açılır.
    datas=[
        ('linux.ico', '.'),
        ('linux.png', '.'),
        ('src/data/distros.json', 'src/data'),
        ('src/data/locales.json', 'src/data'),
    ],
    hiddenimports=['flet'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='LinuXplore',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='linux.ico',
)
