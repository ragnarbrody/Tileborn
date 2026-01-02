# -*- coding: utf-8 -*-

from settings import TILE_SIZE


def mouse_to_tile(mouse_pos, display, camera):
    mx, my = mouse_pos

    # Tela real > surface lógica
    mx = (mx - display.offset_x) / display.scale
    my = (my - display.offset_y) / display.scale

    # Surface lógica > mundo
    world_x = mx + camera.x
    world_y = my + camera.y

    tile_x = int(world_x // TILE_SIZE)
    tile_y = int(world_y // TILE_SIZE)

    return tile_x, tile_y
