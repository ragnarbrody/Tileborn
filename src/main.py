# -*- coding: utf-8 -*-

import pygame

from settings import FPS, MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, MIN_HEIGHT, MIN_WIDTH
from hud import HUD
from input_actions import is_action_pressed
from input_utils import mouse_to_tile, get_line_tiles
from utils  import reload_all_texts
from camera import Camera
from world import World
from display import DisplayManager
from game_mode import GameMode
from buildings import BuildingType
from game_state import GameState
from paths import UI_ICONS, BUILDINGS_ICONS, TILES_DIR, FONTS_DIR
from i18n import i18n
from time_manager import TimeManager

def main():
    pygame.init()
    pygame.display.set_caption("Tileborn")

    clock = pygame.time.Clock()

    display = DisplayManager()
    world = World()
    hud = HUD()
    game_state = GameState()
    time_manager = TimeManager(day_duration_seconds=300)
    hud.resize(display.view_width, display.view_height)
    camera = Camera(
        world_width=MAP_WIDTH * TILE_SIZE,
        world_height=MAP_HEIGHT * TILE_SIZE,
        view_width=display.view_width,
        view_height=display.view_height
    )

    game_mode = GameMode.NORMAL

    # Variáveis pra construção contínua
    building_continuous = False
    last_tile = None
    continuous_building_types = {BuildingType.DIRT_ROAD}
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        dt = clock.tick(FPS) / 1000
        time_manager.update(dt)

        # calcula o tile atual primeiro
        tile_x, tile_y = mouse_to_tile(mouse_pos, camera)

        hud.update({}, dt, mouse_pos)
        hud.update_tooltip(mouse_pos, game_state)

        # atualiza o mundo (incluindo tempo e aldeões)
        world.update(dt, game_state)
        
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
                    # Só permite alternar modo de construção se não houver popup aberto
                    if not hud.selected_building_popup_open:
                        hud.toggle_build_menu()
                        game_mode = (
                            GameMode.BUILD if hud.is_build_mode()
                            else GameMode.NORMAL
                        )

                # ESC fecha popups
                if event.key == pygame.K_ESCAPE:
                    if hud.selected_building_popup_open:
                        hud.close_building_popup()
                        game_mode = GameMode.NORMAL
                    elif hud.options_popup_open:
                        hud.options_popup_open = False
                        hud.selecting_language = False
                    elif hud.is_build_menu_open():
                        hud.toggle_build_menu()
                        game_mode = GameMode.NORMAL

            # sistema de zoom (desativado)
            #elif event.type == pygame.MOUSEWHEEL:
                #if not hud.is_mouse_over_ui(mouse_pos):
                    #camera.zoom_at(mouse_pos[0], mouse_pos[1], event.y)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                    # clique direito cancela construção / fecha menu / fecha popup
                    if event.button == 3:
                        building_continuous = False
                        last_tile = None

                        # Fecha popup de construção se estiver aberto
                        if hud.selected_building_popup_open:
                            hud.close_building_popup()
                            game_mode = GameMode.NORMAL
                         
                        # Cancela modo de construção
                        if game_mode == GameMode.BUILD:
                            hud.toggle_build_menu()
                            game_mode = GameMode.NORMAL

                        continue

                    # clique esquerdo
                    elif event.button == 1:
                        # PRIMEIRO: Processa popup de construção se tiver aberto
                        if hud.selected_building_popup_open:
                            result = hud.handle_building_popup_click(mouse_pos)
                            if result == "building_popup_closed":
                                game_mode = GameMode.NORMAL
                                continue
                            elif result and result.startswith("add_inhabitant_slot_"):
                                # TODO: Implementar lógica para adicionar morador
                                print(f"Adicionar morador no slot {result.split('_')[-1]}")
                                continue
                            elif result == "building_popup_clicked_inside":
                                # Clicou dentro do popup, não faz mais nada
                                continue

                        # SEGUNDO: Processa popup de opções se estiver abertoo
                        if hud.options_popup_open:
                            result = hud.handle_click(mouse_pos)
                            # Se o clique fechou o popup ou foi dentro dele, não passa para o mundo
                            if result in ["options_closed", "options_popup_click", 
                                          "open_language_selector", "language_selector_closed",
                                          "language_selector_click"]:
                                
                                # Verifica se mudou o idioma
                                if result and result.startswith("language_changed_to_"):
                                    #
                                    reload_all_texts(hud)
                                    world.update_building_data()
                                    continue

                                continue

                        # TERCEIRO: Fecha menu hambúrguer ao clicar fora
                        if hud.menu_open and not hud.is_mouse_over_ui(mouse_pos):
                            hud.close_top_menu()
                            continue

                        # QUARTO: Clique no hud (sempre)
                        if hud.is_mouse_over_ui(mouse_pos):
                            result = hud.handle_click(mouse_pos)
                            if result == "build_menu_changed":
                                game_mode = (
                                    GameMode.BUILD if hud.is_build_mode()
                                    else GameMode.NORMAL
                                )
                            continue  # não deixa passar pro mundo
                        
                        # QUINTO: CLIQUE NO MUNDO
                        if game_mode == GameMode.NORMAL or game_mode == GameMode.SELECTED:
                            # Tenta selecionar uma construção
                            entity = world.get_entity_at_tile(tile_x, tile_y)
                            if entity and hasattr(entity, 'type'):
                                # É uma construção - fecha popup atual se existir e abre novo
                                if hud.selected_building_popup_open:
                                    hud.close_building_popup()
                                
                                # Abre o popup da nova construção
                                hud.open_building_popup(entity, entity.type, game_state)
                                game_mode = GameMode.SELECTED
                                continue
                        
                        # CLIQUE NO MUNDO
                        if (game_mode == GameMode.BUILD and 
                            hud.selected_building and 
                            not hud.selected_building_popup_open):

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
        
        # Desenha preview de construção (apenas se não existir nenhum popup aberto)
        if (game_mode == GameMode.BUILD
            and hud.selected_building
            and not hud.is_mouse_over_ui(mouse_pos)
            and hud.can_build()):
            
            world.draw_build_preview(
                display.surface,
                camera,
                tile_x,
                tile_y,
                hud.selected_building,
                game_state
            )

        world.draw_highlight(display.surface, camera, tile_x, tile_y)

        # Se tiver um prédio selecionado no popup, desenha o highlight
        if hud.selected_building_popup_open and hud.selected_building_data:
            tile_x, tile_y = hud.selected_building_data["position"]
            size_x, size_y = hud.selected_building_data.get("size", (1, 1))
            world.draw_selected_building_highlight(display.surface, camera, tile_x, tile_y, size_x, size_y)

        hud.draw_top_bar(display.surface, game_state, time_manager)
        hud.draw(display.surface, game_state) 

        # Desenha o popup da construção selecionada
        if hud.selected_building_popup_open:
            hud.draw_selected_building_popup(display.surface)

        hud.draw_tooltip(display.surface, mouse_pos)

        display.end_draw()

    pygame.quit()

if __name__ == "__main__":
    main() 