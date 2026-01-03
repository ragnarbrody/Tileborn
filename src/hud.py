# -*- coding: utf-8 -*-

import pygame
from resources import ResourceType, RESOURCE_DATA
from buildings import BUILDING_DATA
import math
from paths import UI_ICONS, BUILDINGS_ICONS, TILES_DIR, FONTS_DIR

class HUD:
    def __init__(self):
        # popup
        self.options_popup_open = False
        self.options_popup_rect = pygame.Rect(0, 0, 300, 200)  # largura x altura do popup
        self.options_popup_alpha = 200

        self.build_menu_open = False
        self.height = 80
        self.visible = True
        self.font = pygame.font.SysFont("arial", 16)
        self.expanded = False
        self.buttons = []
        self.build_buttons = []
        self.selected_building = None
        
        self.icon_size = 48
        self.padding = 10

        self.pulse_time = 0.0

        self.build_icon = pygame.image.load(UI_ICONS / "hammer.png").convert_alpha()
        self.build_icon = pygame.transform.scale(
            self.build_icon, (self.icon_size, self.icon_size)
        )

        # Barra superior
        self.top_bar_height = 40
        self.top_bar_alpha = 180

        self.resource_icons = {}
        self.resource_icon_size = 32  # tamanho dos ícones na barra superior

        for res, data in RESOURCE_DATA.items():
            icon = pygame.image.load(data["icon"]).convert_alpha()
            icon = pygame.transform.scale(icon, (self.resource_icon_size, self.resource_icon_size))
            self.resource_icons[res] = icon

        # Animação do menu hambúrguer
        self.top_menu_width = 140
        self.top_menu_option_height = 28
        self.top_menu_options = ["Save", "Options", "Quit"]

        self.top_menu_height = len(self.top_menu_options) * self.top_menu_option_height

        self.top_menu_y = -self.top_menu_height
        self.top_menu_target_y = -self.top_menu_height
        self.top_menu_speed = 600  # px por segundo

        # Menu hamburguer
        self.menu_button_size = 26
        self.menu_button_rect = pygame.Rect(0, 0, self.menu_button_size, self.menu_button_size)

        self.menu_open = False

        self.rect = pygame.Rect(0, 0, 1, self.height)

        self.font = pygame.font.SysFont(None, 24)

        self.create_main_buttons()
        self.create_build_buttons()
        self.hover_tooltip = None
        
    def create_build_buttons(self):
        self.build_buttons.clear()
        x = 10

        for building, data in BUILDING_DATA.items():
            if not data["unlocked"]:
                continue

            icon = pygame.image.load(f"{data['icon']}").convert_alpha()
            icon = pygame.transform.scale(icon, (self.icon_size, self.icon_size))

            rect = pygame.Rect(
                x,
                self.rect.y + 16,
                self.icon_size,
                self.icon_size
            )

            self.build_buttons.append(
                HUDButton(rect, icon, action="select_build", data=building)
            )

            x += self.icon_size + self.padding

    def resize(self, width, height):
        # HUD inferior
        self.rect.x = 0
        self.rect.width = width
        self.rect.y = height - self.height

        # Botão hamburguer (barra superior)
        self.menu_button_rect.topleft = (
            width - self.menu_button_size - 10,
            (self.top_bar_height - self.menu_button_size) // 2
        )

        # Atualiza botões principais
        self.create_main_buttons()
        self.create_build_buttons()

    def is_build_mode(self):
        return self.build_menu_open

    def toggle_build_menu(self):
        self.build_menu_open = not self.build_menu_open
        return self.build_menu_open

    def update(self, input_actions, dt):
        if input_actions.get("toggle_build"):
            self.toggle_build_menu()

        self.pulse_time += dt

        # ANIMAÇÃO DO MENU HAMBURGUER
        if self.top_menu_y < self.top_menu_target_y:
            self.top_menu_y += self.top_menu_speed * dt
            if self.top_menu_y > self.top_menu_target_y:
                self.top_menu_y = self.top_menu_target_y

        elif self.top_menu_y > self.top_menu_target_y:
            self.top_menu_y -= self.top_menu_speed * dt
            if self.top_menu_y < self.top_menu_target_y:
                self.top_menu_y = self.top_menu_target_y

    def create_main_buttons(self):
        self.buttons.clear()

        rect = pygame.Rect(
            10,
            self.rect.y + 16,
            self.icon_size,
            self.icon_size
        )

        self.buttons.append(
            HUDButton(rect, self.build_icon, action="toggle_build")
        )

    def get_pulse_alpha(self):
        pulse = (math.sin(self.pulse_time * 4) + 1) / 2
        return int(0 + pulse * 100)  # 80 → 180

    def draw(self, surface, game_state):
        if not self.visible:
            return

        # fundo
        pygame.draw.rect(surface, (30, 30, 30), self.rect)

        # borda
        pygame.draw.rect(surface, (80, 80, 80), self.rect, 2)

        buttons = self.build_buttons if self.build_menu_open else self.buttons

        for button in buttons:
            is_selected = (
                self.build_menu_open
                and button.action == "select_build"
                and button.data == self.selected_building
            )

            if is_selected:
                alpha = self.get_pulse_alpha()

                data = BUILDING_DATA[self.selected_building]
                cost = data["cost"]

                has_resources = all(
                    game_state.resources.get(res, 0) >= amount
                    for res, amount in cost.items()
                )

                if has_resources:
                    color = (255, 165, 0)  # laranja
                else:
                    color = (200, 50, 50)  # vermelho

                button.draw(
                    surface,
                    highlight=True,
                    alpha=alpha,
                    highlight_color=color
                )
            else:
                button.draw(surface)
        #surface.blit(label, (10, self.rect.y + 10))

        self.draw_selected_building_info(surface, game_state)
        
        # POPUP DE OPTIONS
        self.draw_options_popup(surface)

    def handle_click(self, mouse_pos):
        if self.menu_button_rect.collidepoint(mouse_pos):
            self.menu_open = not self.menu_open

            if self.menu_open:
                self.top_menu_target_y = self.top_bar_height
            else:
                self.top_menu_target_y = -self.top_menu_height

            return "top_menu_toggled"
        
        buttons = self.build_buttons if self.build_menu_open else self.buttons

        for button in buttons:
            if button.is_clicked(mouse_pos):
                if button.action == "toggle_build":
                    self.toggle_build_menu()
                    return "build_menu_changed"

                elif button.action == "select_build":
                    self.selected_building = button.data
                    return "build_selected"

        # CLICKS NO MENU HAMBURGUE
        if self.menu_open:
            width = self.top_menu_width
            x = self.menu_button_rect.right - width
            y = int(self.top_menu_y)

            for i, option in enumerate(self.top_menu_options):
                option_rect = pygame.Rect(
                    x, y + i * self.top_menu_option_height, width, self.top_menu_option_height
                )
                if option_rect.collidepoint(mouse_pos):
                    if option == "Options":
                        self.options_popup_open = True
                    elif option == "Quit":
                        pygame.event.post(pygame.event.Event(pygame.QUIT))
                    # você pode adicionar "Save" depois
                    return f"menu_{option.lower()}_clicked"

        return None
    
    def close_top_menu(self):
        self.menu_open = False
        self.top_menu_target_y = -self.top_menu_height
    
    def is_mouse_over_ui(self, mouse_pos):
        if not mouse_pos:
            return False

        # Barra superior
        top_bar_rect = pygame.Rect(
            0,
            0,
            self.rect.width,
            self.top_bar_height
        )

        if top_bar_rect.collidepoint(mouse_pos):
            return True

        # HUD inferior
        if self.rect.collidepoint(mouse_pos):
            return True

        # Menu dropdown aberto
        if self.menu_open:
            menu_width = 140
            option_height = 28
            height = 3 * option_height

            menu_rect = pygame.Rect(
                self.menu_button_rect.right - self.top_menu_width,
                self.top_menu_y,
                self.top_menu_width,
                self.top_menu_height
            )

            if menu_rect.collidepoint(mouse_pos):
                return True

        return False
    
    def is_build_menu_open(self):
        return self.build_menu_open

    def draw_options_popup(self, surface):
        if not self.options_popup_open:
            return

        # centraliza na tela
        screen_width, screen_height = surface.get_size()
        self.options_popup_rect.center = (screen_width // 2, screen_height // 2)

        popup_surf = pygame.Surface(self.options_popup_rect.size, pygame.SRCALPHA)
        popup_surf.fill((50, 50, 50, self.options_popup_alpha))  # cinza semi-transparente

        # borda
        pygame.draw.rect(popup_surf, (200, 200, 200), popup_surf.get_rect(), 2)

        surface.blit(popup_surf, self.options_popup_rect.topleft)

    def draw_selected_building_info(self, surface, game_state):
        if not self.build_menu_open or not self.selected_building:
            return

        data = BUILDING_DATA[self.selected_building]

        padding = 8
        line_spacing = 4

        # PRÉ-RENDER DOS TEXTOS
        title_font = pygame.font.SysFont(None, 26)
        title_surf = title_font.render(data["name"], True, (255, 255, 255))

        lines = []
        for res, amount in data["cost"].items():
            current = game_state.resources.get(res, 0)

            if current >= amount:
                color = (0, 200, 0)
            else:
                color = (200, 50, 50)

            text = f"{res.capitalize()}: {amount} / {current}"
            lines.append(self.font.render(text, True, color))

        # CALCULAR TAMANHO DO FUNDO
        width = max(
            title_surf.get_width(),
            max(line.get_width() for line in lines)
        ) + padding * 2

        height = (
            title_surf.get_height()
            + line_spacing
            + sum(line.get_height() + line_spacing for line in lines)
            + padding * 2
        )

        # POSIÇÃO
        x = 10
        y = self.rect.y - height - 10  # acima do HUD

        # FUNDO TRANSLÚCIDO
        bg = pygame.Surface((width, height), pygame.SRCALPHA)
        bg.fill((60, 60, 60, 180))  # cinza com alpha

        surface.blit(bg, (x, y))

        # DESENHAR TEXTOS
        draw_y = y + padding
        surface.blit(title_surf, (x + padding, draw_y))
        draw_y += title_surf.get_height() + line_spacing

        for line in lines:
            surface.blit(line, (x + padding, draw_y))
            draw_y += line.get_height() + line_spacing

    def toggle_resources(self):
        self.expanded = not self.expanded

    def draw_top_bar(self, surface, game_state):

        # FUNDO DA BARRA
        bg = pygame.Surface((surface.get_width(), self.top_bar_height), pygame.SRCALPHA)
        bg.fill((50, 50, 50, self.top_bar_alpha))
        surface.blit(bg, (0, 0))

        # RECURSOS (ESQUERDA)
        x = 10
        self.resource_icon_offset_y = -2  # negativo = sobe, positivo = desce
        y = (self.top_bar_height - self.resource_icon_size) // 2 + self.resource_icon_offset_y

        self.resource_rects = {}  # salvar retângulos para tooltips

        resources_to_draw = [
            ResourceType.WOOD,
            ResourceType.STONE,
            ResourceType.FOOD,
            ResourceType.GOLD,
            ResourceType.POPULATION
        ]

        for res in resources_to_draw:
            icon = self.resource_icons[res]
            surface.blit(icon, (x, y))

            # quantidade ou dados da população
            if res == ResourceType.POPULATION:
                amount_text = self.font.render(
                    f"{game_state.resources[res]['with_housing']} / {game_state.resources[res]['without_housing']}",
                    True,
                    (255, 255, 255)
                )
            else:
                amount_text = self.font.render(str(game_state.resources[res]), True, (255, 255, 255))
                 
            surface.blit(amount_text, (x + self.resource_icon_size + 4, y + (self.resource_icon_size - amount_text.get_height()) // 2))

            # salvar retângulo do recurso
            rect = pygame.Rect(x, y, self.resource_icon_size + 4 + amount_text.get_width(), self.resource_icon_size)
            self.resource_rects[res] = rect

            x += rect.width + 16

        # BOTÃO HAMBURGUER (DIREITA)
        self.menu_button_rect.topleft = (
            surface.get_width() - self.menu_button_size - 10,
            (self.top_bar_height - self.menu_button_size) // 2
        )

        self.draw_hamburger_button(surface, self.menu_button_rect)

        # MENU EXPANSÍVEL
        if self.menu_open:
            self.draw_top_menu(surface)

    def draw_top_menu(self, surface):
        width = self.top_menu_width
        height = self.top_menu_height

        x = self.menu_button_rect.right - width
        y = int(self.top_menu_y)

        bg = pygame.Surface((width, height), pygame.SRCALPHA)
        bg.fill((40, 40, 40, 220))
        surface.blit(bg, (x, y))

        for i, option in enumerate(self.top_menu_options):
            text = self.font.render(option, True, (255, 255, 255))
            ty = y + i * self.top_menu_option_height + (
                self.top_menu_option_height - text.get_height()
            ) // 2
            surface.blit(text, (x + 10, ty))

    def draw_hamburger_button(self, surface, rect):
        # fundo do botão
        pygame.draw.rect(surface, (90, 90, 90), rect, border_radius=4)

        # linhas do hamburguer
        line_color = (220, 220, 220)
        line_width = 2
        spacing = 5

        cx = rect.centerx
        cy = rect.centery

        for i in [-1, 0, 1]:
            y = cy + i * spacing
            pygame.draw.line(
                surface,
                line_color,
                (rect.left + 5, y),
                (rect.right - 5, y),
                line_width
            )
    
    def update_tooltip(self, mouse_pos, game_state):
        self.hover_tooltip = None

        # check recurso na barra superior
        for res, rect in getattr(self, "resource_rects", {}).items():
            if rect.collidepoint(mouse_pos):
                data = RESOURCE_DATA[res]
                if res == ResourceType.POPULATION:
                    self.hover_tooltip = {
                        "title": data["name"],
                        "lines": [
                            data["description"],
                            f"With housing: {game_state.resources[res]['with_housing']}",
                            f"Without housing: {game_state.resources[res]['without_housing']}"
                        ]
                    }
                else:
                    self.hover_tooltip = {
                        "title": data["name"],
                        "lines": [
                            data["description"],
                            f"Production per day: {data['production']}",
                            f"Consumption per day: {data['consumption']}"
                        ]
                    }
                return

        buttons = self.build_buttons if self.build_menu_open else self.buttons

        for button in buttons:
            if button.rect.collidepoint(mouse_pos):

                # Botão do martelo
                if button.action == "toggle_build":
                    self.hover_tooltip = {
                        "title": "Build Mode",
                        "lines": ["Allows Building (Shortcut: B)"]
                    }
                    return

                # Botões de construção
                if button.action == "select_build":
                    data = BUILDING_DATA[button.data]

                    lines = [data["description"]]

                    for res, amount in data["cost"].items():
                        lines.append(f"{res.capitalize()}: {amount}")

                    self.hover_tooltip = {
                        "title": data["name"],
                        "lines": lines
                    }
                return
            
    def draw_tooltip(self, surface, mouse_pos):
        if not self.hover_tooltip:
            return

        padding = 8
        line_spacing = 4

        title_font = pygame.font.SysFont(None, 22)
        text_font = pygame.font.SysFont(None, 18)

        title_surf = title_font.render(
            self.hover_tooltip["title"], True, (255, 255, 255)
        )

        line_surfs = [
            text_font.render(line, True, (220, 220, 220))
            for line in self.hover_tooltip["lines"]
        ]

        width = max(
            title_surf.get_width(),
            *(line.get_width() for line in line_surfs)
        ) + padding * 2

        height = (
            title_surf.get_height()
            + sum(line.get_height() + line_spacing for line in line_surfs)
            + padding * 2
        )

        x, y = mouse_pos
        x += 12  # pequeno deslocamento horizontal do mouse

        # Ajuste vertical automático
        if y < self.top_bar_height + 10:
            # mouse na barra superior → desenha para baixo
            y += 20
        else:
            # mouse na barra inferior ou no mundo → desenha para cima
            y -= height + 12

        # Verifica se o tooltip sai da tela à direita
        if x + width > surface.get_width():
            x = surface.get_width() - width - 10

        # Criar fundo do tooltip
        bg = pygame.Surface((width, height), pygame.SRCALPHA)
        bg.fill((50, 50, 50, 190))
        surface.blit(bg, (x, y))

        # Desenhar textos
        draw_y = y + padding
        surface.blit(title_surf, (x + padding, draw_y))
        draw_y += title_surf.get_height() + line_spacing

        for line in line_surfs:
            surface.blit(line, (x + padding, draw_y))
            draw_y += line.get_height() + line_spacing

class HUDButton:
    def __init__(self, rect, icon, action=None, data=None):
        self.rect = rect
        self.icon = icon
        self.action = action
        self.data = data

    def draw(self, surface, highlight=False, alpha=120, highlight_color=(255, 165, 0)):
        if highlight:
            bg = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            bg.fill((*highlight_color, alpha))
            surface.blit(bg, self.rect.topleft)

        surface.blit(self.icon, self.rect.topleft)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
