import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    # Rodando como executável
    BASE_DIR = Path(sys._MEIPASS)
else:
    # Rodando em modo normal
    BASE_DIR = Path(__file__).resolve().parent.parent

ASSETS_DIR = BASE_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
TILES_DIR = ASSETS_DIR / "tiles"
FONTS_DIR = ASSETS_DIR / "fonts"
BUILDINGS_ICONS = ICONS_DIR / "buildings"
UI_ICONS = ICONS_DIR / "ui"