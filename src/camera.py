# -*- coding: utf-8 -*-

class Camera:
    def __init__(self, world_width, world_height, view_width, view_height):
        self.x = 0
        self.y = 0

        self.world_width = world_width
        self.world_height = world_height

        self.view_width = view_width
        self.view_height = view_height

        self.speed = 400

        #ZOOM
        self.zoom = 1.0
        #self.min_zoom = 0.5
        #self.max_zoom = 3.0
        #self.zoom_step = 0.1

    def move(self, dx, dy, dt):
        self.x += dx * self.speed * dt / self.zoom
        self.y += dy * self.speed * dt / self.zoom
        self.clamp()

    def clamp(self):
        max_x = self.world_width - self.view_width / self.zoom
        max_y = self.world_height - self.view_height / self.zoom

        self.x = max(0, min(self.x, max_x))
        self.y = max(0, min(self.y, max_y))

    def apply(self, x, y):
        """Mundo > Tela com zoom"""
        screen_x = (x - self.x) * self.zoom
        screen_y = (y - self.y) * self.zoom
        return screen_x, screen_y

    def screen_to_world(self, sx, sy):
        """Tela > Mundo"""
        wx = sx / self.zoom + self.x
        wy = sy / self.zoom + self.y
        return wx, wy

    def zoom_at(self, mouse_x, mouse_y, direction):
        old_zoom = self.zoom

        if direction > 0:
            self.zoom += self.zoom_step
        else:
            self.zoom -= self.zoom_step

        self.zoom = max(self.min_zoom, min(self.zoom, self.max_zoom))

        if self.zoom == old_zoom:
            return

        # Ajusta a camera pra manter o ponto do mouse fixo
        mx, my = mouse_x, mouse_y
        wx_before, wy_before = self.screen_to_world(mx, my)

        self.zoom = self.zoom
        wx_after, wy_after = self.screen_to_world(mx, my)

        self.x += wx_before - wx_after
        self.y += wy_before - wy_after

        self.clamp()