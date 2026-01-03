# -*- coding: utf-8 -*-

from settings import TILE_SIZE


def mouse_to_tile(mouse_pos, camera):
    mx, my = mouse_pos

    world_x, world_y = camera.screen_to_world(mx, my)

    tile_x = int(world_x // TILE_SIZE)
    tile_y = int(world_y // TILE_SIZE)

    return tile_x, tile_y

def get_line_tiles(x0, y0, x1, y1):
    """Retorna todos os tiles entre (x0, y0) e (x1, y1) usando Bresenham"""
    tiles = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        tiles.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
    return tiles