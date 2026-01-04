# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

project_root = Path(SPECPATH)
src_path = project_root / "src"
assets_path = project_root / "assets"

block_cipher = None

# Coletar todos os arquivos .json de tradução
locales_files = []
locales_path = assets_path / "locales"
if locales_path.exists():
    for file in locales_path.glob("*.json"):
        locales_files.append((str(file), "assets/locales"))

a = Analysis(
    [str(src_path / "main.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        (str(assets_path / "icons"), "assets/icons"),
        (str(assets_path / "tiles"), "assets/tiles"),
        (str(assets_path / "fonts"), "assets/fonts"),
    ] + locales_files,  # Adiciona arquivos de tradução
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
    name="Tileborn",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # SEM console
    icon=str(assets_path / "icons" / "ui" / "icon.ico"),
)