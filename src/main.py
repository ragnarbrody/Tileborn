# -*- coding: utf-8 -*-

import pygame

from settings import FPS, LOGICAL_WIDTH, LOGICAL_HEIGHT, MAP_WIDTH, MAP_HEIGHT, TILE_SIZE
from hud import HUD
from input_actions import is_action_pressed
from input_utils import mouse_to_tile
from camera import Camera
from world import World
from display import DisplayManager
from game_mode import GameMode
from buildings import BuildingType
from game_state import GameState
from paths import UI_ICONS, BUILDINGS_ICONS, TILES_DIR, FONTS_DIR


def main():
    pygame.init()
    pygame.display.set_caption("Py_nished")

    clock = pygame.time.Clock()

    display = DisplayManager()
    world = World()
    hud = HUD()
    game_mode = GameMode.NORMAL
    game_state = GameState()

    camera = Camera(
        world_width=MAP_WIDTH * TILE_SIZE,
        world_height=MAP_HEIGHT * TILE_SIZE,
        view_width=LOGICAL_WIDTH,
        view_height=LOGICAL_HEIGHT
    )
    
    running = True
    while running:
        dt = clock.tick(FPS) / 1000
        hud.update({}, dt)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                display.update_scale()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    hud.toggle_build_menu()
                    game_mode = (
                        GameMode.BUILD if hud.is_build_mode()
                        else GameMode.NORMAL
                    )

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not logical_mouse:
                    continue

                # Fecha menu hambúrguer ao clicar fora
                if hud.menu_open and not hud.is_mouse_over_ui(logical_mouse):
                    hud.close_top_menu()
                    continue

                # CLIQUE NO HUD (sempre)
                if hud.is_mouse_over_ui(logical_mouse):
                    result = hud.handle_click(logical_mouse)

                    if result == "build_menu_changed":
                        game_mode = (
                            GameMode.BUILD if hud.is_build_mode()
                            else GameMode.NORMAL
                        )
                    continue  # IMPORTANTE: não deixa passar pro mundo

                # CLIQUE NO MUNDO
                if game_mode == GameMode.BUILD:
                    if event.button == 1 and hud.selected_building:
                        world.place_building(
                            tile_x,
                            tile_y,
                            hud.selected_building,
                            game_state
                        )

                    elif event.button == 3:
                        hud.toggle_build_menu()
                        game_mode = GameMode.NORMAL

        keys = pygame.key.get_pressed()

        dx = dy = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = 1
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = 1

        camera.move(dx, dy, dt)

        display.begin_draw()

        screen_mouse = pygame.mouse.get_pos()
        logical_mouse = display.screen_to_logical(screen_mouse)

        if logical_mouse:
            hud.update_tooltip(logical_mouse)
            tile_x, tile_y = mouse_to_tile(screen_mouse, display, camera)
        else:
            hud.hover_tooltip = None
            tile_x = tile_y = -1

        world.draw(display.logical_surface, camera)

        if (
            game_mode == GameMode.BUILD
            and hud.selected_building
            and logical_mouse
            and not hud.is_mouse_over_ui(logical_mouse)
        ):
            world.draw_build_preview(
                display.logical_surface,
                camera,
                tile_x,
                tile_y,
                hud.selected_building,
                game_state
            )

        if logical_mouse and not hud.is_mouse_over_ui(logical_mouse):
            world.draw_highlight(display.logical_surface, camera, tile_x, tile_y)
        hud.draw(display.logical_surface, game_state)
        hud.draw_top_bar(display.logical_surface, game_state)

        if logical_mouse:
            hud.draw_tooltip(display.logical_surface, logical_mouse)

        display.end_draw()

    pygame.quit()

if __name__ == "__main__":
    main() 