# -*- coding: utf-8 -*-

import pygame
from settings import (
    LOGICAL_WIDTH,
    LOGICAL_HEIGHT,
    WINDOW_WIDTH,
    WINDOW_HEIGHT
)

class DisplayManager:
    def __init__(self):
        self.window = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT),
            pygame.RESIZABLE
        )

        self.logical_surface = pygame.Surface(
            (LOGICAL_WIDTH, LOGICAL_HEIGHT)
        )

        self.update_scale()

    def update_scale(self):
        win_w, win_h = self.window.get_size()

        scale_x = win_w / LOGICAL_WIDTH
        scale_y = win_h / LOGICAL_HEIGHT

        self.scale = min(scale_x, scale_y)

        self.scaled_width = int(LOGICAL_WIDTH * self.scale)
        self.scaled_height = int(LOGICAL_HEIGHT * self.scale)

        self.offset_x = (win_w - self.scaled_width) // 2
        self.offset_y = (win_h - self.scaled_height) // 2

    def begin_draw(self):
        self.logical_surface.fill((0, 0, 0))

    def end_draw(self):
        scaled_surface = pygame.transform.scale(
            self.logical_surface,
            (self.scaled_width, self.scaled_height)
        )

        self.window.fill((0, 0, 0))
        self.window.blit(
            scaled_surface,
            (self.offset_x, self.offset_y)
        )
        pygame.display.flip()

    def screen_to_logical(self, pos):
        screen_x, screen_y = pos

        # Remove o offset (barras pretas)
        x = screen_x - self.offset_x
        y = screen_y - self.offset_y

        # Evita clique fora da área útil
        if x < 0 or y < 0:
            return None

        # Converte pela escala
        logical_x = x / self.scale
        logical_y = y / self.scale

        return int(logical_x), int(logical_y)
