# -*- coding: utf-8 -*-
from resources import ResourceType
from paths import UI_ICONS, BUILDINGS_ICONS, BUILDINGS_TILES, TILES_DIR, FONTS_DIR

class BuildingType:
    HOUSE = "house"
    SAWMILL = "sawmill"

class BuildingInstance:
    def __init__(self, building_type, x, y, sprite):
        self.type = building_type
        self.x = x
        self.y = y
        self.sprite = sprite

BUILDING_COLORS = {
    BuildingType.HOUSE: (180, 180, 180),
}

BUILDING_DATA = {
    BuildingType.HOUSE: {
        "name": "House",
        "size": (4, 4),  # largura x altura em tiles
        "cost": {
            ResourceType.WOOD: 10,
            ResourceType.STONE: 5,
        },
        "unlocked": True,
        "description": "A home for your inhabitants.",
        "icon": BUILDINGS_ICONS / "house.png",
        "sprite": BUILDINGS_TILES / "house_1.png",
    },

    BuildingType.SAWMILL: {
        "name": "Sawmill",
        "size": (6, 4),
        "cost": {
            ResourceType.WOOD: 20,
            ResourceType.STONE: 10,
        },
        "unlocked": True,
        "description": "A place to get some wood.",
        "icon": BUILDINGS_ICONS / "sawmill.png",
        "sprite": BUILDINGS_TILES / "sawmill_1.png",
    }
}