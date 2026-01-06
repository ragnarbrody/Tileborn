# -*- coding: utf-8 -*-
from resources import ResourceType
from paths import UI_ICONS, BUILDINGS_ICONS, BUILDINGS_TILES, TILES_DIR, FONTS_DIR
from i18n import i18n

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

        # atributos para sistema de habitantes
        self.inhabitants = []  # Lista de aldeões que moram aqui
        self.workers = []      # Lista de aldeões que trabalham aqui
        self.max_inhabitants = 0
        self.max_workers = 0
        self.production_rate = {}  # Recursos produzidos por dia
        self.consumption_rate = {} # Recursos consumidos por dia
        
        # Inicializa os atributos baseados no tipo
        self._initialize_attributes()

    def _initialize_attributes(self):
        """Inicializa os atributos do prédio baseado no tipo"""
        building_data = get_building_data().get(self.type, {})
        
        if self.type == BuildingType.HOUSE:
            self.max_inhabitants = 2  # pessoas por casa
            self.max_workers = 0
            self.base_production_per_worker = {}
            
        elif self.type == BuildingType.SAWMILL:
            self.max_inhabitants = 0
            self.max_workers = 3  # 3 trabalhadores na serraria
            self.base_production_per_worker = {ResourceType.WOOD: 2}  # 2 madeiras por trabalhador por dia
            
        elif self.type == BuildingType.TOWNHALL:
            self.max_inhabitants = 10  # A prefeitura pode abrigar alguns habitantes
            self.max_workers = 2  # Administradores da cidade (vão atrair imigrantes depois, talvez)
            self.base_production_per_worker = {}  # Prefeitura não produz nadica (ainda)
            
        elif self.type == BuildingType.DIRT_ROAD:
            self.max_inhabitants = 0
            self.max_workers = 0
            self.base_production_per_worker = {}

    def calculate_daily_production(self):
        """Calcula a produção diária baseada no número de trabalhadores"""
        daily_production = {}
        
        if not self.base_production_per_worker:
            return daily_production
        
        for resource, amount_per_worker in self.base_production_per_worker.items():
            if self.workers:
                # Produção = base por trabalhador × numero de trabalhadores × modificador
                total_amount = amount_per_worker * len(self.workers) * self.production_modifier
                daily_production[resource] = int(total_amount)
        
        return daily_production

    @property
    def size(self):
        """Retorna o tamanho do prédio em tiles"""
        building_data = get_building_data().get(self.type, {})
        return building_data.get("size", (1, 1))

    @property
    def has_space_for_inhabitants(self):
        """Verifica se tem espaço para mais moradores"""
        return len(self.inhabitants) < self.max_inhabitants

    @property
    def has_space_for_workers(self):
        """Verifica se tem espaço para mais trabalhadores"""
        return len(self.workers) < self.max_workers

    def add_inhabitant(self, villager):
        """Adiciona um morador ao prédio"""
        if self.has_space_for_inhabitants and villager not in self.inhabitants:
            self.inhabitants.append(villager)
            villager.home_building = self
            return True
        return False

    def add_worker(self, villager):
        """Adiciona um trabalhador ao prédio"""
        if self.has_space_for_workers and villager not in self.workers:
            self.workers.append(villager)
            villager.workplace = self
            return True
        return False

    def remove_inhabitant(self, villager):
        """Remove um morador do prédio"""
        if villager in self.inhabitants:
            self.inhabitants.remove(villager)
            if villager.home_building == self:
                villager.home_building = None
            return True
        return False

    def remove_worker(self, villager):
        """Remove um trabalhador do prédio"""
        if villager in self.workers:
            self.workers.remove(villager)
            if villager.workplace == self:
                villager.workplace = None
            return True
        return False

def get_building_data():
    """Retorna os dados de construções, sempre atualizados com o idioma atual"""
    return {
        BuildingType.HOUSE: {
            "name": i18n.get("buildings.house", "House"),
            "size": (4, 4),
            "cost": {
                ResourceType.WOOD: 10,
                ResourceType.STONE: 5,
            },
            "unlocked": True,
            "description": i18n.get("descriptions.house_desc", "A home for your inhabitants."),
            "icon": BUILDINGS_ICONS / "house.png",
            "sprite": BUILDINGS_TILES / "house_1.png",
        },

        BuildingType.SAWMILL: {
            "name": i18n.get("buildings.sawmill", "Sawmill"),
            "size": (6, 4),
            "cost": {
                ResourceType.WOOD: 20,
                ResourceType.STONE: 10,
            },
            "unlocked": True,
            "description": i18n.get("descriptions.sawmill_desc", "A place to get some wood."),
            "icon": BUILDINGS_ICONS / "sawmill.png",
            "sprite": BUILDINGS_TILES / "sawmill_1.png",
        },

        BuildingType.TOWNHALL: {
            "name": i18n.get("buildings.townhall", "Town Hall"),
            "size": (8, 7),
            "cost": {
                ResourceType.WOOD: 40,
                ResourceType.GOLD: 20,
                ResourceType.STONE: 20,
            },
            "unlocked": True,
            "description": i18n.get("descriptions.townhall_desc", "A place where the town is administrated."),
            "icon": BUILDINGS_ICONS / "townhall.png",
            "sprite": BUILDINGS_TILES / "townhall_1.png",
        },

        BuildingType.DIRT_ROAD: {
            "name": i18n.get("buildings.dirt_road", "Dirt Road"),
            "size": (1, 1),
            "cost": {
                ResourceType.WOOD: 0,
            },
            "unlocked": True,
            "description": i18n.get("descriptions.dirt_road_desc", "Something to your citizen walk on."),
            "icon": BUILDINGS_ICONS / "dirt_road.png",
            "sprite": BUILDINGS_TILES / "dirt_1.png",
        },
    }

# Mantive uma referência para compatibilidade
BUILDING_DATA = get_building_data()