# -*- coding: utf-8 -*-

import pygame
from settings import (
    MIN_HEIGHT,
    MIN_WIDTH,
)

class DisplayManager:
    def __init__(self):
        self.window = pygame.display.set_mode(
            (1280, 720),
            pygame.RESIZABLE
        )

        self.update_viewport()

    def update_viewport(self):
        win_w, win_h = self.window.get_size()

        self.view_width = max(MIN_WIDTH, win_w)
        self.view_height = max(MIN_HEIGHT, win_h)

        # Surface onde tudo será desenhado
        self.surface = pygame.Surface(
            (self.view_width, self.view_height)
        )

    def begin_draw(self):
        self.surface.fill((0, 0, 0))

    def end_draw(self):
        # Desenha direto, sem escala
        self.window.blit(self.surface, (0, 0))
        pygame.display.flip()

    def handle_resize(self, width, height):
        self.window = pygame.display.set_mode(
            (width, height),
            pygame.RESIZABLE
        )
        self.update_viewport()  # ESSENCIAL