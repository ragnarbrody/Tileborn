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
        "variants": [
            {"sprite": TILES_DIR / "grass_1.png", "weight": 30},
            {"sprite": TILES_DIR / "grass_2.png", "weight": 70},
        ]
    },
    TileType.WATER: {
        "walkable": False,
        "variants": [
            {"sprite": TILES_DIR / "water_2.png", "weight": 100}
        ]
    }
}
