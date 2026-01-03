from paths import ICONS_DIR, UI_ICONS
from i18n import i18n

class ResourceType:
    WOOD = "wood"
    STONE = "stone"
    FOOD = "food"
    GOLD = "gold"
    POPULATION = "population"

def get_resource_data():
    """Retorna os dados de recursos, sempre atualizados com o idioma atual"""
    return {
        ResourceType.WOOD: {
            "name": i18n.get("resources.wood", "Wood"),
            "description": i18n.get("descriptions.wood_desc", "Used for building houses and structures."),
            "icon": UI_ICONS / "wood_1.png",
            "consumption": 0,
            "production": 0,
        },
        ResourceType.STONE: {
            "name": i18n.get("resources.stone", "Stone"),
            "description": i18n.get("descriptions.stone_desc", "Used for building strong structures."),
            "icon": UI_ICONS / "stones_1.png",
            "consumption": 0,
            "production": 0,
        },
        ResourceType.FOOD: {
            "name": i18n.get("resources.food", "Food"),
            "description": i18n.get("descriptions.food_desc", "Feeds your population."),
            "icon": UI_ICONS / "food_1.png",
            "consumption": 0,
            "production": 0,
        },
        ResourceType.GOLD: {
            "name": i18n.get("resources.gold", "Gold"),
            "description": i18n.get("descriptions.gold_desc", "Used for trade and upgrades."),
            "icon": UI_ICONS / "gold_1.png",
            "consumption": 0,
            "production": 0,
        },
        ResourceType.POPULATION: {
            "name": i18n.get("resources.population", "Population"),
            "description": i18n.get("descriptions.population_desc", "Your citizens count."),
            "icon": UI_ICONS / "population_1.png",
            "with_housing": 0,
            "without_housing": 0,
        },
    }

# Mantive uma referência para compatibilidade (mas é bão usar a função)
RESOURCE_DATA = get_resource_data()