# -*- coding: utf-8 -*-

class Camera:
    def __init__(self, world_width, world_height, view_width, view_height):
        self.x = 0
        self.y = 0

        self.world_width = world_width
        self.world_height = world_height

        self.view_width = view_width
        self.view_height = view_height

        self.speed = 300  # pixels por segundo

    def move(self, dx, dy, dt):
        self.x += dx * self.speed * dt
        self.y += dy * self.speed * dt

        self.clamp()

    def clamp(self):
        self.x = max(0, min(self.x, self.world_width - self.view_width))
        self.y = max(0, min(self.y, self.world_height - self.view_height))

    def apply(self, x, y):
        """Converte coordenadas do mundo para tela"""
        return x - self.x, y - self.y
