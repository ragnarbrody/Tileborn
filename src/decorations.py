# decorations.py
# -*- coding: utf-8 -*-

import pygame
from settings import TILE_SIZE
from paths import TILES_DIR

class Tree:
    def __init__(self, tile_x, tile_y, width=1, height=2, sprite_name="tree_1.png"):
        self.x = tile_x
        self.y = tile_y
        self.width = width      # largura em tiles
        self.height = height    # altura em tiles

        self.sprite = pygame.image.load(
            TILES_DIR / sprite_name
        ).convert_alpha()

        self.sprite = pygame.transform.scale(
            self.sprite,
            (TILE_SIZE * self.width, TILE_SIZE * self.height)
        )

    def draw(self, surface, camera):
        world_x = self.x * TILE_SIZE

        # sobe (height - 1) tiles
        world_y = (self.y - (self.height - 1)) * TILE_SIZE

        screen_x, screen_y = camera.apply(world_x, world_y)
        surface.blit(self.sprite, (screen_x, screen_y))