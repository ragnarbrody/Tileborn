# -*- coding: utf-8 -*-
from resources import ResourceType

class BuildingType:
    HOUSE = "house"
    SAWMILL = "sawmill"

BUILDING_COLORS = {
    BuildingType.HOUSE: (180, 180, 180),
}

BUILDING_DATA = {
    BuildingType.HOUSE: {
        "name": "House",
        "cost": {
            ResourceType.WOOD: 10,
            ResourceType.STONE: 5,
        },
        "unlocked": True,  # futuramente vem da pesquisa
        "description": "A home for your inhabitants.",
        "icon": "buildings/house.png"
    },
    BuildingType.SAWMILL: {
        "name": "Sawmill",
        "cost": {
            ResourceType.WOOD: 20,
            ResourceType.STONE: 10,
        },
        "unlocked": True,
        "description": "A place to get some wood.",
        "icon": "buildings/sawmill.png"
    }
}