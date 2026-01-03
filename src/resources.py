from paths import ICONS_DIR, UI_ICONS

class ResourceType:
    WOOD = "wood"
    STONE = "stone"
    FOOD = "food"
    GOLD = "gold"
    POPULATION = "population"

RESOURCE_DATA = {
    ResourceType.WOOD: {
        "name": "Wood",
        "description": "Used for building houses and structures.",
        "icon": UI_ICONS / "wood_1.png",
        "consumption": 0,  # por dia
        "production": 0,   # por dia
    },
    ResourceType.STONE: {
        "name": "Stone",
        "description": "Used for building strong structures.",
        "icon": UI_ICONS / "stones_1.png",
        "consumption": 0,
        "production": 0,
    },
    ResourceType.FOOD: {
        "name": "Food",
        "description": "Feeds your population.",
        "icon": UI_ICONS / "food_1.png",
        "consumption": 0,
        "production": 0,
    },
    ResourceType.GOLD: {
        "name": "Gold",
        "description": "Used for trade and upgrades.",
        "icon": UI_ICONS / "gold_1.png",
        "consumption": 0,
        "production": 0,
    },
    ResourceType.POPULATION: {
        "name": "Population",
        "description": "Your citizens count.",
        "icon": UI_ICONS / "population_1.png",
        "with_housing": 0,
        "without_housing": 0,
    },
}