# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['D:/GitHub/Bot-Galactic-Swamp/main.py'],
    pathex=['D:/GitHub/Bot-Galactic-Swamp/bot-env/Lib/site-packages'],
    binaries=[],
    datas=[('D:/GitHub/Bot-Galactic-Swamp/Models', 'Models/'), ('D:/GitHub/Bot-Galactic-Swamp/Utils', 'Utils/')],
    hiddenimports=[],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Bot-Galactic-Swamp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['D:\\GitHub\\Bot-Galactic-Swamp\\Image\\worker.ico'],
)
