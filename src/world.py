# -*- coding: utf-8 -*-

import random
import pygame

from settings import MAP_WIDTH, MAP_HEIGHT, TILE_SIZE
from tiles import TileType, TILE_DATA
from buildings import get_building_data, BuildingInstance
from decorations import Tree

class World:
    def __init__(self):
        self.width = MAP_WIDTH
        self.height = MAP_HEIGHT
        self.buildings = [] # lista de BuildingInstance
        self.occupied_tiles = set()  # tiles ocupados
        self.decorations = []  # árvores, pedras etcs
        self.tile_variants = [[None for _ in range(self.width)]
                      for _ in range(self.height)]

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

        return True
    
    