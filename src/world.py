# -*- coding: utf-8 -*-

import random
import pygame

from settings import MAP_WIDTH, MAP_HEIGHT, TILE_SIZE
from tiles import TileType, TILE_DATA
from buildings import get_building_data, BuildingInstance, BuildingType
from decorations import Tree
from villager import Villager
from time_manager import TimeManager 

class World:
    def __init__(self):
        self.width = MAP_WIDTH
        self.height = MAP_HEIGHT
        self.buildings = [] # lista de BuildingInstance
        self.occupied_tiles = set()  # tiles ocupados
        self.decorations = []  # árvores, pedras etcs
        self.villagers = []
        self.tile_variants = [[None for _ in range(self.width)]
                      for _ in range(self.height)]
        
        # Gerenciador de tempo
        self.time_manager = TimeManager(day_duration_seconds=300)  # 5 minutos por dia

        self.tile_sprites = {}
        self.tile_weights = {}

        # Dados de construções (serão atualizados quando o idioma mudar)
        self._building_data = None

        for tile, data in TILE_DATA.items():
            self.tile_sprites[tile] = []
            self.tile_weights[tile] = []

            for variant in data["variants"]:
                img = pygame.image.load(variant["sprite"]).convert_alpha()
                img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))

                self.tile_sprites[tile].append(img)
                self.tile_weights[tile].append(variant["weight"])
                
        self.grid = [[TileType.GRASS for _ in range(self.width)]
                     for _ in range(self.height)]

        self.generate()

    @property
    def building_data(self):
        """Retorna os dados de construções sempre atualizados"""
        if self._building_data is None:
            self._building_data = get_building_data()
        return self._building_data
    
    @building_data.setter
    def building_data(self, value):
        self._building_data = value
        
    def update_building_data(self):
        """Força a atualização dos dados de construções"""
        self._building_data = get_building_data()

    # GERAÇÃO do mundo
    def generate(self):
        self.generate_river()
        self.generate_forests()
        self.assign_tile_variants()

    def assign_tile_variants(self):
        for y in range(self.height):
            for x in range(self.width):
                tile = self.grid[y][x]

                weights = self.tile_weights[tile]
                variants_count = len(weights)

                index = random.choices(
                    range(variants_count),
                    weights=weights,
                    k=1
                )[0]

                self.tile_variants[y][x] = index

    def generate_river(self):
        x = random.randint(0, self.width - 1)

        for y in range(self.height):
            self.grid[y][x] = TileType.WATER
            x += random.choice([-1, 0, 1])
            x = max(0, min(self.width - 1, x))

    def generate_forests(self, patches=15):
        for _ in range(patches):
            cx = random.randint(0, self.width - 1)
            cy = random.randint(0, self.height - 1)
            radius = random.randint(4, 10)

            for y in range(cy - radius, cy + radius):
                for x in range(cx - radius, cx + radius):
                    if not (0 <= x < self.width and 0 <= y < self.height):
                        continue

                    if self.grid[y][x] != TileType.GRASS:
                        continue

                    if random.random() > 0.15:
                        continue

                    # Parâmetros da árvore
                    tree_width = 3
                    tree_height = 5

                    # Cabe no mapa?
                    if y - (tree_height - 1) < 0:
                        continue
                    if x + tree_width > self.width:
                        continue

                    tree = Tree(
                        x, y,
                        width=tree_width,
                        height=tree_height,
                        sprite_name="tree_1.png"
                    )

                    self.decorations.append(tree)

                    # Marcar tiles ocupados
                    for ty in range(y - (tree.height - 1), y + 1):
                        for tx in range(x, x + tree.width):
                            self.occupied_tiles.add((tx, ty))

    def update(self, dt, game_state):
        """Atualiza o mundo (incluindo tempo e aldeões)"""
        # Atualizar tempo
        new_day_started = self.time_manager.update(dt)
        
        if new_day_started:
            self._process_day_cycle(game_state)
        
        # Atualizar aldeões
        for villager in self.villagers:
            villager.update(dt, self)
        
        # ATUALIZAR POPULAÇÃO NO GAME_STATE A CADA FRAME
        # Isso garante que o HUD sempre mostre valores atualizados
        self.update_population_in_game_state(game_state)
    
    def _process_day_cycle(self, game_state):
        """Processa eventos que acontecem no início de cada dia"""
        print(f"Novo dia começou: Dia {self.time_manager.current_day}")
        
        # Produzir recursos dos prédios
        self._produce_resources(game_state)
        
        # Consumir recursos
        self._consume_resources(game_state)
        
        # Atualizar população
        self._update_population_stats(game_state)
    
    def _produce_resources(self, game_state):
        """Produz recursos de todos os prédios de produção baseado nos trabalhadores"""
        total_production = {}
        
        for building in self.buildings:
            # Calcular produção diária do prédio
            daily_production = building.calculate_daily_production()
            
            # Somar à produção total
            for resource, amount in daily_production.items():
                if amount > 0:
                    if resource not in total_production:
                        total_production[resource] = 0
                    total_production[resource] += amount
                    
                    # Adicionar recursos ao game_state
                    game_state.add_resource(resource, amount)
                    
                    # Log detalhado
                    print(f"{building.type} (com {len(building.workers)} trabalhadores) produziu {amount} {resource}")
        
        # Log resumido da produção total do dia
        if total_production:
            print(f"Produção total do dia: {total_production}")

    def _consume_resources(self, game_state):
        """Consome recursos (comida dos habitantes)"""
        # Consumo de comida: 1 unidade por habitante por dia
        total_consumption = len(self.villagers)
        
        # Consumir recursos
        if game_state.resources.get("food", 0) >= total_consumption:
            game_state.resources["food"] -= total_consumption
            print(f"Consumo diário: {total_consumption} comida (para {len(self.villagers)} habitantes)")
        else:
            # Fome - reduz felicidade dos aldeões
            shortage = total_consumption - game_state.resources.get("food", 0)
            game_state.resources["food"] = 0
            
            for villager in self.villagers:
                if hasattr(villager, 'happiness'):
                    # Quanto mais falta de comida, maior a redução de felicidade
                    happiness_reduction = min(30, shortage * 2)
                    villager.happiness = max(0, villager.happiness - happiness_reduction)
            
            print(f"FOME! Falta {shortage} comida. Felicidade dos aldeões reduzida.")
    
    def _update_happiness(self, game_state):
        """Atualiza felicidade baseada em condições"""
        # Aqui futuramente podemos adicionar mais fatores de felicidade
        # Por enquanto, apenas logamos
        total_happiness = sum(v.happiness for v in self.villagers if hasattr(v, 'happiness'))
        avg_happiness = total_happiness / len(self.villagers) if self.villagers else 0
        
        print(f"Felicidade média dos aldeões: {avg_happiness:.1f}%")

    def _update_population_stats(self, game_state):
        """Atualiza estatísticas da população no game_state"""
        # Contar habitantes com e sem moradia
        with_housing = 0
        without_housing = 0
        
        for villager in self.villagers:
            if villager.home_building:
                with_housing += 1
            else:
                without_housing += 1
        
        game_state.resources["population"] = {
            "with_housing": with_housing,
            "without_housing": without_housing
        }

    # RENDER
    def draw(self, surface, camera):
        start_x = int(camera.x // TILE_SIZE)
        start_y = int(camera.y // TILE_SIZE)

        tiles_x = int(surface.get_width() / (TILE_SIZE * camera.zoom)) + 2
        tiles_y = int(surface.get_height() / (TILE_SIZE * camera.zoom)) + 2

        end_x = start_x + tiles_x
        end_y = start_y + tiles_y

        # --- DESENHAR TERRENO ---
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                if 0 <= x < self.width and 0 <= y < self.height:
                    tile = self.grid[y][x]

                    world_x = x * TILE_SIZE
                    world_y = y * TILE_SIZE
                    screen_x, screen_y = camera.apply(world_x, world_y)

                    index = self.tile_variants[y][x]
                    sprite = self.tile_sprites[tile][index]

                    surface.blit(sprite, (screen_x, screen_y))

        # --- DESENHAR DECORAÇÕES (árvores etc) ---
        for deco in self.decorations:
            deco.draw(surface, camera)

        # Desenhar construções
        for building in self.buildings:
            world_x = building.x * TILE_SIZE
            world_y = building.y * TILE_SIZE

            screen_x, screen_y = camera.apply(world_x, world_y)

            surface.blit(building.sprite, (screen_x, screen_y))

        # Desenhar aldeões
        for villager in self.villagers:
            villager.draw(surface, camera)

    def draw_highlight(self, surface, camera, tile_x, tile_y):
        if not (0 <= tile_x < self.width and 0 <= tile_y < self.height):
            return

        world_x = tile_x * TILE_SIZE
        world_y = tile_y * TILE_SIZE

        screen_x, screen_y = camera.apply(world_x, world_y)

        pygame.draw.rect(
            surface,
            (255, 255, 0),
            (screen_x, screen_y, TILE_SIZE, TILE_SIZE),
            1  # espessura (contorno)
        )

    def draw_build_preview(self, surface, camera, tile_x, tile_y, building_type, game_state):
        data = self.building_data[building_type]
        w, h = data["size"]

        can_place = self.can_place_building(tile_x, tile_y, building_type)
        has_resources = game_state.has_resources(data["cost"])

        if not can_place:
            color = (255, 0, 0, 100)
        elif not has_resources:
            color = (255, 165, 0, 100)
        else:
            color = (0, 255, 0, 100)

        world_x = tile_x * TILE_SIZE
        world_y = tile_y * TILE_SIZE
        screen_x, screen_y = camera.apply(world_x, world_y)

        preview = pygame.Surface(
            (w * TILE_SIZE, h * TILE_SIZE),
            pygame.SRCALPHA
        )
        preview.fill(color)

        surface.blit(preview, (screen_x, screen_y))

        pygame.draw.rect(
            surface,
            (255, 255, 255),
            (screen_x, screen_y, w * TILE_SIZE, h * TILE_SIZE),
            1
        )


    def can_place_building(self, tile_x, tile_y, building_type):
        data = self.building_data[building_type]
        w, h = data["size"]

        for y in range(tile_y, tile_y + h):
            for x in range(tile_x, tile_x + w):
                if not (0 <= x < self.width and 0 <= y < self.height):
                    return False

                if self.grid[y][x] == TileType.WATER:
                    return False

                if (x, y) in self.occupied_tiles:
                    return False

        return True
    
    def place_building(self, tile_x, tile_y, building_type, game_state):
        if not self.can_place_building(tile_x, tile_y, building_type):
            return False

        data = self.building_data[building_type]
        cost = data["cost"]

        if not game_state.has_resources(cost):
            return False

        game_state.consume_resources(cost)

        w, h = data["size"]

        # Carregar e redimensionar sprite
        sprite = pygame.image.load(data["sprite"]).convert_alpha()
        sprite = pygame.transform.scale(
            sprite,
            (w * TILE_SIZE, h * TILE_SIZE)
        )

        building = BuildingInstance(building_type, tile_x, tile_y, sprite)
        self.buildings.append(building)

        # Marcar tiles ocupados
        for y in range(tile_y, tile_y + h):
            for x in range(tile_x, tile_x + w):
                self.occupied_tiles.add((x, y))

        # Lógica especial para cada tipo de construção
        if building_type == BuildingType.TOWNHALL:
            self._spawn_townhall_villagers(building, game_state)
        elif building_type == BuildingType.HOUSE:
            self._assign_villagers_to_house(building, game_state)

        return True
    
    def _spawn_townhall_villagers(self, townhall, game_state):
        """Spawna 3 aldeões quando uma prefeitura é construída"""

        print(f"DEBUG: Tentando spawnar aldeões para prefeitura")
        print(f"DEBUG: Townhall type: {townhall.type}")
        print(f"DEBUG: Townhall pos: ({townhall.x}, {townhall.y})")

        # Verificar se o building tem os atributos necessários
        if not hasattr(townhall, 'size'):
            print(f"DEBUG: Townhall não tem atributo 'size'")
            # Usar tamanho padrão da prefeitura
            building_data = self.building_data.get(townhall.type, {})
            building_size = building_data.get("size", (8, 6))
        else:
            building_size = townhall.size
            
        print(f"DEBUG: Townhall size: {building_size}")

        for i in range(3):
            # Encontrar posição próxima à prefeitura
            spawn_x, spawn_y = self._find_nearby_empty_tile(
                townhall.x, townhall.y, townhall.size[0], townhall.size[1]
            )
            
            if spawn_x is not None and spawn_y is not None:
                # Criar aldeão
                villager = Villager(spawn_x, spawn_y, home_building=townhall)
                self.villagers.append(villager)
                
                # Tentar atribuir à prefeitura como moradia (se tiver espaço)
                if hasattr(townhall, 'add_inhabitant') and hasattr(townhall, 'has_space_for_inhabitants'):
                    if townhall.has_space_for_inhabitants:
                        townhall.add_inhabitant(villager)
                        print(f"DEBUG: Aldeão {villager.name} atribuído à prefeitura")
                    else:
                        print(f"DEBUG: Prefeitura não tem espaço para mais habitantes")
                else:
                    print(f"DEBUG: Townhall não tem métodos de habitantes")

                print(f"Aldeão {villager.name} spawnou na prefeitura")
                self.update_population_in_game_state(game_state)
            else:
                print(f"DEBUG: Não encontrou tile vazio para spawnar aldeão")
    
    def _assign_villagers_to_house(self, house, game_state):
        """Atribui aldeões sem casa a uma nova casa"""
        print(f"DEBUG: Tentando atribuir aldeões à casa")
        
        # Procurar aldeões sem casa
        homeless_villagers = []
        for v in self.villagers:
            if not hasattr(v, 'home_building') or not v.home_building:
                homeless_villagers.append(v)
        
        print(f"DEBUG: Aldeões sem casa: {len(homeless_villagers)}")
        
        for villager in homeless_villagers:
            if hasattr(house, 'add_inhabitant') and hasattr(house, 'has_space_for_inhabitants'):
                if house.has_space_for_inhabitants:
                    house.add_inhabitant(villager)
                    print(f"{villager.name} mudou-se para uma nova casa")
                else:
                    print(f"DEBUG: Casa não tem mais espaço")
                    break
            else:
                print(f"DEBUG: Casa não tem métodos de habitantes")
                break
        
        # Atualizar população no game_state
        self.update_population_in_game_state(game_state)
    
    def _find_nearby_empty_tile(self, center_x, center_y, width, height, max_radius=5):
        """Encontra um tile vazio próximo a uma construção"""
        for radius in range(1, max_radius + 1):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    x = center_x + dx
                    y = center_y + dy
                    
                    # Verificar se o tile está livre
                    if (0 <= x < self.width and 
                        0 <= y < self.height and
                        self.grid[y][x] != TileType.WATER and
                        (x, y) not in self.occupied_tiles):
                        return x, y
        return None, None
    
    def update_population_in_game_state(self, game_state):
        """Atualiza as estatísticas de população no game_state"""
        if not game_state:
            return
        
        # Contar habitantes com e sem moradia
        with_housing = 0
        without_housing = 0
        
        for villager in self.villagers:
            if hasattr(villager, 'home_building') and villager.home_building:
                with_housing += 1
            else:
                without_housing += 1
        
        # Atualizar o game_state
        game_state.resources["population"] = {
            "with_housing": with_housing,
            "without_housing": without_housing,
            "total": with_housing + without_housing
        }
        
        print(f"DEBUG: População atualizada: {with_housing} com casa, {without_housing} sem casa")
    
    