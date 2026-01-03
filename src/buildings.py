# -*- coding: utf-8 -*-
from resources import ResourceType
from paths import UI_ICONS, BUILDINGS_ICONS, BUILDINGS_TILES, TILES_DIR, FONTS_DIR

class BuildingType:
    HOUSE = "house"
    SAWMILL = "sawmill"
    TOWNHALL = "townhall"
    DIRT_ROAD = "dirt road"

class BuildingInstance:
    def __init__(self, building_type, x, y, sprite):
        self.type = building_type
        self.x = x
        self.y = y
        self.sprite = sprite

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
    },

    BuildingType.TOWNHALL: {
        "name": "Town Hall",
        "size": (8, 6),
        "cost": {
            ResourceType.WOOD: 40,
            ResourceType.GOLD: 20,
            ResourceType.STONE: 20,
        },
        "unlocked": True,
        "description": "A place where the town is administrated.",
        "icon": BUILDINGS_ICONS / "townhall.png",
        "sprite": BUILDINGS_TILES / "townhall_1.png",
    },

    BuildingType.DIRT_ROAD: {
        "name": "Dirt Road",
        "size": (1, 1),
        "cost": {
            ResourceType.WOOD: 0,
        },
        "unlocked": True,
        "description": "Something to your citizen walk on.",
        "icon": BUILDINGS_ICONS / "dirt_road.png",
        "sprite": BUILDINGS_TILES / "dirt_1.png",
    },
}