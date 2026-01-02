# -*- coding: utf-8 -*-

import pygame
from paths import UI_ICONS, BUILDINGS_ICONS, TILES_DIR, FONTS_DIR

class TileType:
    GRASS = "grass"
    WATER = "water"
    SAND = "sand"   # futuro
    SNOW = "snow"   # futuro


TILE_DATA = {
    TileType.GRASS: {
        "walkable": True,
        "sprites": [
            TILES_DIR / "grass_1.png",
            TILES_DIR / "grass_2.png"
        ]
    },
    TileType.WATER: {
        "walkable": False,
        "sprites": [
            TILES_DIR / "water_1.png",
        ]
    },
}
