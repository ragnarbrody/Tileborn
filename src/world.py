# -*- coding: utf-8 -*-

import random
import pygame
import math

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
        self.time_manager = TimeManager(day_duration_seconds=300)  # 300 sec = 5 minutos por dia

        self.tile_sprites = {}
        self.tile_weights = {}

        # Dados de construções (vão ser atualizados quando o idioma mudar)
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

                    # Marca os tiles ocupados
                    for ty in range(y - (tree.height - 1), y + 1):
                        for tx in range(x, x + tree.width):
                            self.occupied_tiles.add((tx, ty))

    def get_tree_at_tile(self, tile_x, tile_y):
        """Retorna a árvore no tile especificado (se houver)"""
        for deco in self.decorations:
            if hasattr(deco, 'type') and deco.type == "tree":
                # Verifica se o tile tá dentro da área da árvore
                if (deco.x <= tile_x < deco.x + deco.width and
                    deco.y - (deco.height - 1) <= tile_y <= deco.y):
                    return deco
        return None

    def remove_cut_trees(self):
        """Remove árvores que foram completamente cortadas do mundo"""
        trees_to_remove = []
        
        for deco in self.decorations:
            if hasattr(deco, 'type') and deco.type == "tree" and deco.is_cut:
                # Marca os tiles como desocupados
                for ty in range(deco.y - (deco.height - 1), deco.y + 1):
                    for tx in range(deco.x, deco.x + deco.width):
                        if (tx, ty) in self.occupied_tiles:
                            self.occupied_tiles.remove((tx, ty))
                trees_to_remove.append(deco)
        
        # Remove as árvores
        for tree in trees_to_remove:
            self.decorations.remove(tree)
            print(f"Árvore em ({tree.x}, {tree.y}) removida do mundo")
        
        return len(trees_to_remove)

    def update(self, dt, game_state):
        """Atualiza o mundo (incluindo tempo e aldeões)"""
        # Atualiza pathfinder stats periodicamente
        if hasattr(self.pathfinder, 'print_stats'):
            self.pathfinder.print_stats()

        # Atualiza o tempo
        new_day_started = self.time_manager.update(dt)
        
        if new_day_started:
            self._process_day_cycle(game_state)
        
        # Atualiza os aldeões
        for villager in self.villagers:
            villager.update(dt, self)

        # Remove árvores cortadas
        trees_removed = self.remove_cut_trees()
        if trees_removed > 0:
            print(f"Removidas {trees_removed} árvores cortadas")
        
        # Atualiza a população no game_state a cada frame
        # meio pesado, mas garante que o HUD sempre mostre valores atualizados
        self.update_population_in_game_state(game_state)
    
    def _process_day_cycle(self, game_state):
        """Processa eventos que acontecem no início de cada dia"""
        print(f"Novo dia começou: Dia {self.time_manager.current_day}")
        
        # Produz os recursos dos prédios
        self._produce_resources(game_state)
        
        # Consome recursos
        self._consume_resources(game_state)
        
        # Atualiza a população
        self._update_population_stats(game_state)
    
    def _produce_resources(self, game_state):
        """Produz recursos de todos os prédios de produção baseado nos trabalhadores"""
        total_production = {}
        
        for building in self.buildings:
            # Calcula a produção diária do prédio
            daily_production = building.calculate_daily_production()
            
            # Somar na produção total
            for resource, amount in daily_production.items():
                if amount > 0:
                    if resource not in total_production:
                        total_production[resource] = 0
                    total_production[resource] += amount
                    
                    # Adiciona os recursos ao game_state
                    game_state.add_resource(resource, amount)
                    
                    # Log detalhado
                    print(f"{building.type} (com {len(building.workers)} trabalhadores) produziu {amount} {resource}")
        
        # Log resumido da produção total do dia
        if total_production:
            print(f"Produção total do dia: {total_production}")

    def _consume_resources(self, game_state):
        """Consome recursos (comida dos habitantes)"""
        # ainda não implementado ***

        # Consumo de comida: 1 unidade por habitante por dia (por enquanto)
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
        # Aqui futuramente eu vou adicionar mais fatores de felicidade
        # Por enquanto, eu to apenas 'logando'
        total_happiness = sum(v.happiness for v in self.villagers if hasattr(v, 'happiness'))
        avg_happiness = total_happiness / len(self.villagers) if self.villagers else 0
        
        print(f"Felicidade média dos aldeões: {avg_happiness:.1f}%")

    def _update_population_stats(self, game_state):
        """Atualiza estatísticas da população no game_state"""
        # Conta os habitantes com e sem moradia
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

        # Desenha o Terreno
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

        # Desenha as decorações (árvores etc)
        for deco in self.decorations:
            deco.draw(surface, camera)

        # Desenha as construções
        for building in self.buildings:
            world_x = building.x * TILE_SIZE
            world_y = building.y * TILE_SIZE

            screen_x, screen_y = camera.apply(world_x, world_y)

            surface.blit(building.sprite, (screen_x, screen_y))

        # Desenha os aldeões
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

        # Carrega e redimensiona o sprite
        sprite = pygame.image.load(data["sprite"]).convert_alpha()
        sprite = pygame.transform.scale(
            sprite,
            (w * TILE_SIZE, h * TILE_SIZE)
        )

        building = BuildingInstance(building_type, tile_x, tile_y, sprite)
        building.world = self
        self.buildings.append(building)

        # Marca os tiles ocupados
        for y in range(tile_y, tile_y + h):
            for x in range(tile_x, tile_x + w):
                self.occupied_tiles.add((x, y))

        # Lógica especial pra cada tipo de construção (tlvz eu mude isso depois)
        if building_type == BuildingType.TOWNHALL:
            self._spawn_townhall_villagers(building, game_state)
        elif building_type == BuildingType.HOUSE:
            self._assign_villagers_to_house(building, game_state)
            # Tenta atribuir aldeões sem casa nas casas existentes
            self.assign_homeless_to_houses()

        return True
    
    def _spawn_townhall_villagers(self, townhall, game_state):
        """Spawna 3 aldeões quando uma prefeitura é construída"""
        print(f"DEBUG: Tentando spawnar aldeões para prefeitura")
        print(f"DEBUG: Townhall type: {townhall.type}")
        print(f"DEBUG: Townhall pos: ({townhall.x}, {townhall.y})")

        # Prefeitura não é mais moradia, apenas local de trabalho
        # Mas os aldeões ainda precisam de moradia
        available_houses = []
        for building in self.buildings:
            if building.type == BuildingType.HOUSE and building.has_space_for_inhabitants:
                available_houses.append(building)
        
        print(f"DEBUG: Casas disponíveis com espaço: {len(available_houses)}")

        for i in range(3):
            # Encontra uma posição próxima à prefeitura
            spawn_x, spawn_y = self._find_nearby_empty_tile(
                townhall.x, townhall.y, townhall.size[0], townhall.size[1]
            )
            
            if spawn_x is not None and spawn_y is not None:
                # Cria aldeão com nome e sobrenome
                villager = Villager(spawn_x, spawn_y)
                self.villagers.append(villager)
                
                # Tenta atribuir à prefeitura como trabalho 
                # desativado, pq fala sério começar com trabalhador na prefeitura
                #if hasattr(townhall, 'add_worker') and hasattr(townhall, 'has_space_for_workers'):
                #    if townhall.has_space_for_workers:
                #        townhall.add_worker(villager)
                #        print(f"DEBUG: Aldeão {villager.full_name} atribuído à prefeitura como trabalhador")
                #    else:
                #        print(f"DEBUG: Prefeitura não tem espaço para mais trabalhadores")
                
                # Tenta atribuir a uma casa disponível
                if available_houses:
                    # Encontra a casa com mais espaço disponível
                    for house in available_houses:
                        if house.add_inhabitant(villager):
                            print(f"DEBUG: Aldeão {villager.full_name} atribuído à casa")
                            # Remove a casa da lista se estiver cheia
                            if not house.has_space_for_inhabitants:
                                available_houses.remove(house)
                            break
                    else:
                        print(f"DEBUG: Não foi possível alocar {villager.full_name} em uma casa")
                else:
                    print(f"DEBUG: {villager.full_name} ficou sem casa")
                
                print(f"Aldeão {villager.full_name} spawnou na prefeitura")
                self.update_population_in_game_state(game_state)
            else:
                print(f"DEBUG: Não encontrou tile vazio para spawnar aldeão")
    
    def _assign_villagers_to_house(self, house, game_state):
        """Atribui aldeões sem casa a uma nova casa"""
        print(f"DEBUG: Tentando atribuir aldeões à casa")
        
        # Procura aldeões sem casa
        homeless_villagers = []
        for v in self.villagers:
            if not hasattr(v, 'home_building') or not v.home_building:
                homeless_villagers.append(v)
        
        print(f"DEBUG: Aldeões sem casa: {len(homeless_villagers)}")
        
        # Ordena por tempo sem casa (opcional, vai ter prioridade dps)
        for villager in homeless_villagers:
            if hasattr(house, 'add_inhabitant') and hasattr(house, 'has_space_for_inhabitants'):
                if house.has_space_for_inhabitants:
                    if house.add_inhabitant(villager):
                        print(f"{villager.full_name} mudou-se para uma nova casa")
                    else:
                        print(f"DEBUG: Não foi possível adicionar {villager.full_name} à casa")
                else:
                    print(f"DEBUG: Casa não tem mais espaço")
                    break
            else:
                print(f"DEBUG: Casa não tem métodos de habitantes")
                break
        
        # Atualiza a população no game_state
        self.update_population_in_game_state(game_state)

    def assign_homeless_to_houses(self):
        """Tenta atribuir todos os aldeões sem casa às casas disponíveis"""
        # Coleta todas as casas com espaço
        available_houses = []
        for building in self.buildings:
            if building.type == BuildingType.HOUSE and building.has_space_for_inhabitants:
                available_houses.append(building)
        
        # Coleta todos os aldeões sem casa
        homeless_villagers = []
        for villager in self.villagers:
            if not hasattr(villager, 'home_building') or not villager.home_building:
                homeless_villagers.append(villager)
        
        # Tenta atribuir cada aldeão a uma casa
        for villager in homeless_villagers:
            for house in available_houses:
                if house.add_inhabitant(villager):
                    print(f"{villager.full_name} foi alocado para uma casa")
                    # Remove a casa da lista se estiver cheia
                    if not house.has_space_for_inhabitants:
                        available_houses.remove(house)
                    break
            else:
                print(f"{villager.full_name} permanece sem casa")
        
    def _find_nearby_empty_tile(self, center_x, center_y, width, height, max_radius=5):
        """Encontra um tile vazio próximo a uma construção"""
        for radius in range(1, max_radius + 1):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    x = center_x + dx
                    y = center_y + dy
                    
                    # Verifica se o tile tá livre
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
        
        # Conta habitantes com e sem moradia
        with_housing = 0
        without_housing = 0
        
        for villager in self.villagers:
            if hasattr(villager, 'home_building') and villager.home_building:
                with_housing += 1
            else:
                without_housing += 1
        
        # Atualiza o game_state
        game_state.resources["population"] = {
            "with_housing": with_housing,
            "without_housing": without_housing,
            "total": with_housing + without_housing
        }
        
        #print(f"DEBUG: População atualizada: {with_housing} com casa, {without_housing} sem casa")

    def get_unemployed_villagers(self):
        """Retorna lista de aldeões desempregados"""
        unemployed = []
        for villager in self.villagers:
            if not hasattr(villager, 'workplace') or not villager.workplace:
                unemployed.append(villager)
        return unemployed

    def get_entity_at_tile(self, tile_x, tile_y):
        """Retorna a construção que está no tile especificado"""
        for building in self.buildings:
            bx, by = building.x, building.y
            bw, bh = building.size
            
            # Verifica se o tile tá dentro dos limites da construção
            if bx <= tile_x < bx + bw and by <= tile_y < by + bh:
                return building
        
        # Não encontrou construção
        return None
    
    def draw_selected_building_highlight(self, surface, camera, tile_x, tile_y, width, height):
        """Desenha um highlight pulsante ao redor de um prédio"""
        
        # Calcula valor de pulsação baseado no tempo
        current_time = pygame.time.get_ticks() / 1000.0  # Tempo em segundos
        pulse_speed = 2.0  # Velocidade da pulsação (ciclos por segundo)
        
        # Usa seno pra criar um efeito de pulsação mais suave entre 0 e 1
        pulse = (math.sin(current_time * math.pi * pulse_speed) + 1) / 2
        
        # Interpola entre dois tons de amarelo
        dark_yellow = (200, 200, 0)    # Amarelo mais escuro
        bright_yellow = (255, 255, 100) # Amarelo mais claro/branco
        
        # Interpola as cores (dá uma suavizada)
        r = int(dark_yellow[0] + (bright_yellow[0] - dark_yellow[0]) * pulse)
        g = int(dark_yellow[1] + (bright_yellow[1] - dark_yellow[1]) * pulse)
        b = int(dark_yellow[2] + (bright_yellow[2] - dark_yellow[2]) * pulse)
        
        # Aqui é pra dar uma leve pulsada na espessura da linha
        base_thickness = 3
        pulse_thickness = int(base_thickness + pulse * 1.5)  # 3-4.5 pixels
        
        world_x = tile_x * TILE_SIZE
        world_y = tile_y * TILE_SIZE
        world_width = width * TILE_SIZE
        world_height = height * TILE_SIZE
        
        screen_x, screen_y = camera.apply(world_x, world_y)
        screen_width = int(world_width * camera.zoom)
        screen_height = int(world_height * camera.zoom)
        
        # Desenha o contorno principal pulsante
        pygame.draw.rect(
            surface,
            (r, g, b),
            (screen_x, screen_y, screen_width, screen_height),
            pulse_thickness
        )
        
        # Adiciona um contorno interno mais fino pra destacar (aqui eu fiz por preferencia, mas dá pra tirar dps)
        if pulse > 0.7:  # Só desenha quando tiver mais brilhante
            inner_thickness = 1
            inner_offset = pulse_thickness + 2
            pygame.draw.rect(
                surface,
                (255, 255, 255),  # Branco
                (screen_x + inner_offset, screen_y + inner_offset, 
                screen_width - 2*inner_offset, screen_height - 2*inner_offset),
                inner_thickness
            )
    