# -*- coding: utf-8 -*-

import shutil
import subprocess
import sys
from pathlib import Path

""" Este script é só para compilar os executaveis do jogo e do launcher """

# CONFIGURAÇÕES
PROJECT_NAME = "Tileborn"
LAUNCHER_NAME = "TilebornLauncher"

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
BUILD = ROOT / "build"

GAME_SPEC = ROOT / "Tileborn.spec"
LAUNCHER_SPEC = ROOT / "TilebornLauncher.spec"

# FUNÇÕES
def run(command: list[str]):
    print(f"\n▶ {' '.join(command)}")
    subprocess.check_call(command)

def clean():
    print("\n Limpando builds velhas...")
    if BUILD.exists():
        shutil.rmtree(BUILD)
    if DIST.exists():
        shutil.rmtree(DIST)

def build_game():
    print("\n🎮 Construindo executável...")
    run([
        sys.executable,
        "-m", "PyInstaller",
        str(GAME_SPEC)
    ])

def build_launcher():
    print("\n🚀 Construindo executável do launcher...")
    run([
        sys.executable,
        "-m", "PyInstaller",
        str(LAUNCHER_SPEC)
    ])

def assemble_release():
    print("\n📦 Montando pasta final de release...")

    release_dir = DIST / PROJECT_NAME
    release_dir.mkdir(parents=True, exist_ok=True)

    # Copiar executáveis
    shutil.copy(
        DIST / f"{PROJECT_NAME}.exe",
        release_dir / f"{PROJECT_NAME}.exe"
    )

    shutil.copy(
        DIST / f"{LAUNCHER_NAME}.exe",
        release_dir / f"{LAUNCHER_NAME}.exe"
    )

    # Copiar assets
    assets_src = ROOT / "assets"
    assets_dst = release_dir / "assets"

    shutil.copytree(assets_src, assets_dst, dirs_exist_ok=True)
    
    # Verificar se os arquivos de tradução foram copiados
    print("\n🔍 Verificando arquivos de tradução...")
    locales_dir = assets_dst / "locales"
    if locales_dir.exists():
        for file in locales_dir.glob("*.json"):
            print(f"  ✅ {file.name}")
    else:
        print(f"  ❌ Diretório de traduções não encontrado: {locales_dir}")

    print(f"\n✅ Release pronta em: {release_dir}")

# MAIN
if __name__ == "__main__":
    try:
        clean()
        build_game()
        build_launcher()
        assemble_release()
        print("\n🎉 BUILD Finalizada com Sucesso!")
    except subprocess.CalledProcessError as e:
        print("\n❌ Build Falhou.")
        sys.exit(1)
