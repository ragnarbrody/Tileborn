# -*- coding: utf-8 -*-

import random
import pygame

from settings import MAP_WIDTH, MAP_HEIGHT, TILE_SIZE
from tiles import TileType, TILE_COLORS
from buildings import BUILDING_DATA



class World:
    def __init__(self):
        self.buildings = {}  # (x, y) -> tipo de construção
        self.width = MAP_WIDTH
        self.height = MAP_HEIGHT
        self.grid = [[TileType.GRASS for _ in range(self.width)]
                     for _ in range(self.height)]

        self.generate()

    # ======================
    # GERAÇÃO
    # ======================
    def generate(self):
        self.generate_river()
        self.generate_forests()

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
                    if 0 <= x < self.width and 0 <= y < self.height:
                        if random.random() < 0.6 and self.grid[y][x] == TileType.GRASS:
                            self.grid[y][x] = TileType.FOREST

    # ======================
    # RENDER
    # ======================
    def draw(self, surface, camera):
        start_x = int(camera.x // TILE_SIZE)
        start_y = int(camera.y // TILE_SIZE)

        end_x = start_x + (surface.get_width() // TILE_SIZE) + 1
        end_y = start_y + (surface.get_height() // TILE_SIZE) + 1

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                if 0 <= x < self.width and 0 <= y < self.height:
                    tile = self.grid[y][x]
                    color = TILE_COLORS[tile]

                    world_x = x * TILE_SIZE
                    world_y = y * TILE_SIZE

                    screen_x, screen_y = camera.apply(world_x, world_y)

                    pygame.draw.rect(
                        surface,
                        color,
                        (screen_x, screen_y, TILE_SIZE, TILE_SIZE)
                    )
        # Desenhar construções
        for (bx, by), building in self.buildings.items():
            world_x = bx * TILE_SIZE
            world_y = by * TILE_SIZE
            screen_x, screen_y = camera.apply(world_x, world_y)

            pygame.draw.rect(
                surface,
                (160, 160, 160),
                (screen_x, screen_y, TILE_SIZE, TILE_SIZE)
            )

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
        # Verificação de tile
        can_place = self.can_place_building(tile_x, tile_y)

        # Verificação de recursos
        building_data = BUILDING_DATA.get(building_type)
        if not building_data:
            return False

        cost = building_data["cost"]
        has_resources = game_state.has_resources(cost)

        valid = can_place and has_resources

        if not can_place:
            color = (255, 0, 0, 120)       # tile inválido
        elif not has_resources:
            color = (255, 165, 0, 120)     # sem recursos
        else:
            color = (0, 255, 0, 120)       # válido

        world_x = tile_x * TILE_SIZE
        world_y = tile_y * TILE_SIZE
        screen_x, screen_y = camera.apply(world_x, world_y)

        preview = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        preview.fill(color)
        surface.blit(preview, (screen_x, screen_y))

        pygame.draw.rect(
            surface,
            (255, 255, 255),
            (screen_x, screen_y, TILE_SIZE, TILE_SIZE),
            1
        )


    def can_place_building(self, tile_x, tile_y):
        # Dentro do mapa
        if not (0 <= tile_x < self.width and 0 <= tile_y < self.height):
            return False

        # Não pode colocar em água
        if self.grid[tile_y][tile_x] == TileType.WATER:
            return False

        # Tile já ocupado
        if (tile_x, tile_y) in self.buildings:
            return False

        return True
    
    def place_building(self, tile_x, tile_y, building_type, game_state):
        if not self.can_place_building(tile_x, tile_y):
            return False

        building_data = BUILDING_DATA.get(building_type)
        if not building_data:
            return False

        cost = building_data["cost"]
        if not game_state.has_resources(cost):
            return False

        game_state.consume_resources(cost)
        self.buildings[(tile_x, tile_y)] = building_type
        return True
    
    