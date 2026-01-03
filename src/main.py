# -*- coding: utf-8 -*-

import pygame

from settings import FPS, MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, MIN_HEIGHT, MIN_WIDTH
from hud import HUD
from input_actions import is_action_pressed
from input_utils import mouse_to_tile, get_line_tiles
from camera import Camera
from world import World
from display import DisplayManager
from game_mode import GameMode
from buildings import BuildingType
from game_state import GameState
from paths import UI_ICONS, BUILDINGS_ICONS, TILES_DIR, FONTS_DIR


def main():
    pygame.init()
    pygame.display.set_caption("Tileborn")

    clock = pygame.time.Clock()

    display = DisplayManager()
    world = World()
    hud = HUD()
    game_state = GameState()
    hud.resize(display.view_width, display.view_height)
    camera = Camera(
        world_width=MAP_WIDTH * TILE_SIZE,
        world_height=MAP_HEIGHT * TILE_SIZE,
        view_width=display.view_width,
        view_height=display.view_height
    )

    game_mode = GameMode.NORMAL

    # Variáveis para construção contínua
    building_continuous = False
    last_tile = None
    continuous_building_types = {BuildingType.DIRT_ROAD}
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        dt = clock.tick(FPS) / 1000

        # calcular tile atual primeiro
        tile_x, tile_y = mouse_to_tile(mouse_pos, camera)

        hud.update({}, dt)
        hud.update_tooltip(mouse_pos, game_state)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                new_width = max(event.w, 800)
                new_height = max(event.h, 600)

                display.handle_resize(new_width, new_height)

                camera.view_width = display.view_width
                camera.view_height = display.view_height
                camera.clamp()

                hud.resize(display.view_width, display.view_height)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    hud.toggle_build_menu()
                    game_mode = (
                        GameMode.BUILD if hud.is_build_mode()
                        else GameMode.NORMAL
                    )

            # sistema de zoom (desativado)
            #elif event.type == pygame.MOUSEWHEEL:
                #if not hud.is_mouse_over_ui(mouse_pos):
                    #camera.zoom_at(mouse_pos[0], mouse_pos[1], event.y)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                    # clique direito cancela construção / fecha menu
                    if event.button == 3:
                        building_continuous = False
                        last_tile = None
                        if game_mode == GameMode.BUILD:
                            hud.toggle_build_menu()
                            game_mode = GameMode.NORMAL
                        continue

                    # clique esquerdo
                    elif event.button == 1:
                        # Fecha menu hambúrguer ao clicar fora
                        if hud.menu_open and not hud.is_mouse_over_ui(mouse_pos):
                            hud.close_top_menu()
                            continue

                        # CLIQUE NO HUD (sempre)
                        if hud.is_mouse_over_ui(mouse_pos):
                            result = hud.handle_click(mouse_pos)
                            if result == "build_menu_changed":
                                game_mode = (
                                    GameMode.BUILD if hud.is_build_mode()
                                    else GameMode.NORMAL
                                )
                            continue  # não deixa passar pro mundo

                        # CLIQUE NO MUNDO
                        if game_mode == GameMode.BUILD and hud.selected_building:
                            # se é construção contínua
                            if hud.selected_building in continuous_building_types:
                                building_continuous = True
                            else:
                                # construção normal
                                world.place_building(
                                    tile_x,
                                    tile_y,
                                    hud.selected_building,
                                    game_state
                                )
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    building_continuous = False
                    last_tile = None

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

        # Construção contínua
        if building_continuous and hud.selected_building in continuous_building_types:
            if last_tile:
                line_tiles = get_line_tiles(last_tile[0], last_tile[1], tile_x, tile_y)
                for tx, ty in line_tiles:
                    world.place_building(tx, ty, hud.selected_building, game_state)
            else:
                world.place_building(tile_x, tile_y, hud.selected_building, game_state)

            last_tile = (tile_x, tile_y)

        display.begin_draw()

        tile_x, tile_y = mouse_to_tile(mouse_pos, camera)

        world.draw(display.surface, camera)
        
        if (
            game_mode == GameMode.BUILD
            and hud.selected_building
            and not hud.is_mouse_over_ui(mouse_pos)
        ):
            world.draw_build_preview(
                display.surface,
                camera,
                tile_x,
                tile_y,
                hud.selected_building,
                game_state
            )

        world.draw_highlight(display.surface, camera, tile_x, tile_y)

        hud.draw(display.surface, game_state)
        hud.draw_top_bar(display.surface, game_state)
        hud.draw_tooltip(display.surface, mouse_pos)

        display.end_draw()

    pygame.quit()

if __name__ == "__main__":
    main() 