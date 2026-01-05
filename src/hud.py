# -*- coding: utf-8 -*-

import pygame
from resources import ResourceType, RESOURCE_DATA
from buildings import BUILDING_DATA
import math
from paths import UI_ICONS, BUILDINGS_ICONS, TILES_DIR, FONTS_DIR, LOCALES_DIR
from utils import reload_all_texts

class HUD:
    def __init__(self):
        from i18n import i18n
        self.i18n = i18n
        self.build_menu_open = False
        self.height = 80
        self.visible = True
        self.font = pygame.font.SysFont("arial", 16)
        self.expanded = False
        self.buttons = []
        self.build_buttons = []
        self.selected_building = None
        
        self.top_menu_hover_index = -1  # -1 significa nenhuma opção com hover

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
        self.top_menu_options = [
            self.i18n.get("menu.save", "Save"),
            self.i18n.get("menu.options", "Options"),
            self.i18n.get("menu.quit", "Quit")
        ]

        self.top_menu_height = len(self.top_menu_options) * self.top_menu_option_height

        self.top_menu_y = -self.top_menu_height
        self.top_menu_target_y = -self.top_menu_height
        self.top_menu_speed = 600  # px por segundo

        # Menu hamburguer
        self.menu_button_size = 26
        self.menu_button_rect = pygame.Rect(0, 0, self.menu_button_size, self.menu_button_size)

        self.menu_open = False
        # Popup de opções
        self.options_popup_open = False
        self.options_popup_alpha = 210

        # Sistema de abas do menu de opções
        self.options_tab_keys = ["general", "display", "audio", "controls"]
        self.current_options_tab_key = "general"  # Armazena a chave

        # Opções de idioma disponíveis
        self.available_languages = self.i18n.get_available_languages()
        self.selected_language = self.i18n.current_lang
        
        # Dados para cada aba (agora dinâmicos)
        self.tab_content = {
            self.i18n.get("options.general", "General"): [
                self.i18n.get("options.language", "Language"),
                self.i18n.get("options.auto_save", "Auto-save frequency"),
                self.i18n.get("options.game_settings", "Game settings")
            ],
            self.i18n.get("options.display", "Display"): [
                self.i18n.get("ui.resolution", "Resolution"),
                self.i18n.get("ui.fullscreen", "Fullscreen"),
                self.i18n.get("ui.vsync", "VSync")
            ],
            self.i18n.get("options.audio", "Audio"): [
                self.i18n.get("ui.master_volume", "Master volume"),
                self.i18n.get("ui.music_volume", "Music volume"),
                self.i18n.get("ui.sound_effects", "Sound effects")
            ],
            self.i18n.get("options.controls", "Controls"): [
                self.i18n.get("ui.camera_movement", "Camera movement")
            ]
        }
        
        self.tab_button_height = 30
        self.tab_button_padding = 10

        # Controla se estamos selecionando idioma
        self.selecting_language = False
        self.language_buttons = []

        self.rect = pygame.Rect(0, 0, 1, self.height)

        self.font = pygame.font.SysFont(None, 24)

        self.create_main_buttons()
        self.create_build_buttons()
        self.hover_tooltip = None

    def get_options_tabs_texts(self):
        """Retorna os textos das abas traduzidos"""
        return [
            self.i18n.get("options.general", "General"),
            self.i18n.get("options.display", "Display"),
            self.i18n.get("options.audio", "Audio"),
            self.i18n.get("options.controls", "Controls")
        ]
    
    def get_current_tab_text(self):
        """Retorna o texto da aba atual traduzido"""
        if self.current_options_tab_key == "general":
            return self.i18n.get("options.general", "General")
        elif self.current_options_tab_key == "display":
            return self.i18n.get("options.display", "Display")
        elif self.current_options_tab_key == "audio":
            return self.i18n.get("options.audio", "Audio")
        elif self.current_options_tab_key == "controls":
            return self.i18n.get("options.controls", "Controls")
        return self.i18n.get("options.general", "General")
    
    def get_tab_content(self, tab_key):
        """Retorna o conteúdo da aba traduzido"""
        if tab_key == "general":
            return [
                self.i18n.get("options.language", "Language"),
                self.i18n.get("options.auto_save", "Auto-save frequency"),
                self.i18n.get("options.game_settings", "Game settings")
            ]
        elif tab_key == "display":
            return [
                self.i18n.get("ui.resolution", "Resolution"),
                self.i18n.get("ui.fullscreen", "Fullscreen"),
                self.i18n.get("ui.vsync", "VSync")
            ]
        elif tab_key == "audio":
            return [
                self.i18n.get("ui.master_volume", "Master volume"),
                self.i18n.get("ui.music_volume", "Music volume"),
                self.i18n.get("ui.sound_effects", "Sound effects")
            ]
        elif tab_key == "controls":
            return [
                self.i18n.get("ui.camera_movement", "Camera Movement")
            ]
        return [] 
        
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

    def update(self, input_actions, dt, mouse_pos=None):
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

        # Atualiza hover do menu hambúrguer
        if mouse_pos is not None:
            self.update_top_menu_hover(mouse_pos)

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
        # SEMPRE processa popup de opções primeiro se estiver aberto
        if self.options_popup_open:
            popup_rect = self.get_options_popup_rect(pygame.display.get_surface())

            # Se estiver selecionando idioma, processa primeiro
            if self.selecting_language:
                # CALCULA DINAMICAMENTE baseado no número de idiomas
                button_height = 30
                button_spacing = 5
                padding_top = 40
                padding_bottom = 10
                
                num_languages = len(self.available_languages)
                selector_height = padding_top + (button_height * num_languages) + (button_spacing * (num_languages - 1)) + padding_bottom
                selector_width = 200
                
                selector_x = popup_rect.x + (popup_rect.width - selector_width) // 2
                selector_y = popup_rect.y + (popup_rect.height - selector_height) // 2
                
                selector_rect = pygame.Rect(selector_x, selector_y, selector_width, selector_height)
                
                # Se clicou fora do seletor, fecha o seletor
                if not selector_rect.collidepoint(mouse_pos):
                    self.selecting_language = False
                    return "language_selector_closed"
                
                # Verifica cliques nos botões de idioma
                button_y = selector_y + padding_top
                
                for i, lang_code in enumerate(self.available_languages):
                    button_rect = pygame.Rect(
                        selector_x + 20,
                        button_y + i * (button_height + button_spacing),
                        selector_width - 40,
                        button_height
                    )
                    
                    if button_rect.collidepoint(mouse_pos):
                        if lang_code != self.selected_language:
                            self.selected_language = lang_code
                            self.i18n.load_language(lang_code)
                            # IMPORTANTE: Atualiza textos do HUD antes de recarregar tudo
                            self.update_language_texts()
                            reload_all_texts(self)
                        self.selecting_language = False
                        return f"language_changed_to_{lang_code}"
                
                return "language_selector_click"
            
            # clicou fora → fecha
            if not popup_rect.collidepoint(mouse_pos):
                self.options_popup_open = False
                self.selecting_language = False
                return "options_closed"
            
            # Verifica clique nas abas
            popup_x, popup_y = popup_rect.topleft
            popup_width, popup_height = popup_rect.size
            tabs_height = 40

            # Obter textos das abas para calcular posições
            tab_texts = self.get_options_tabs_texts()
            
            # Calcular posição e tamanho das abas
            if tab_texts:
                tab_width = (popup_width - (len(tab_texts) + 1) * self.tab_button_padding) // len(tab_texts)
            else:
                tab_width = 100
            
            for i, tab_text in enumerate(tab_texts):
                x = popup_x + self.tab_button_padding + i * (tab_width + self.tab_button_padding)
                y = popup_y + 5
                tab_rect = pygame.Rect(x, y, tab_width, tabs_height - 10)
                
                if tab_rect.collidepoint(mouse_pos):
                    # Usa a chave da aba, não o texto
                    self.current_options_tab_key = self.options_tab_keys[i]
                    self.selecting_language = False
                    return f"options_tab_{self.current_options_tab_key}"
            
            # Verifica clique no botão de idioma (se estiver na aba General)
            if self.current_options_tab_key == "general" and hasattr(self, 'language_button_rect'):
                # Converter coordenadas relativas do popup para coordenadas da tela
                lang_button_rect_screen = pygame.Rect(
                    popup_x + self.language_button_rect.x,
                    popup_y + self.language_button_rect.y,
                    self.language_button_rect.width,
                    self.language_button_rect.height
                )
                
                if lang_button_rect_screen.collidepoint(mouse_pos):
                    self.selecting_language = True
                    return "open_language_selector"
            
            # clicou dentro do popup (mas não em uma aba) → bloqueia clique pro jogo
            return "options_popup_click"

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
                    if option == self.i18n.get("menu.options", "Options"):
                        self.open_options()
                        self.menu_open = False
                        self.top_menu_target_y = -self.top_menu_height
                        return "menu_options_clicked"
                    elif self.i18n.get("menu.quit", "Quit"):
                        pygame.event.post(pygame.event.Event(pygame.QUIT))
                        return "menu_quit_clicked"  
                    elif option == self.i18n.get("menu.save", "Save"):
                        #
                        return "menu_save_clicked"

        return None
    
    def open_options(self):
        self.options_popup_open = True
        self.current_options_tab_key = "general" # Reseta para aba padrão
    
    def close_top_menu(self):
        self.menu_open = False
        self.top_menu_target_y = -self.top_menu_height
    
    def is_mouse_over_ui(self, mouse_pos):
        if not mouse_pos:
            return False
        
        # Se popup de opções estiver aberto, considera TODO o clique como UI
        if self.options_popup_open:
            return True

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
    
    def update_language_texts(self):
        """Atualiza todos os textos quando o idioma muda"""
        print(f"Atualizando textos para idioma: {self.i18n.current_lang}")
        
        # Atualiza menu hamburguer
        self.top_menu_options = [
            self.i18n.get("menu.save", "Save"),
            self.i18n.get("menu.options", "Options"),
            self.i18n.get("menu.quit", "Quit")
        ]
        
        # Atualiza conteúdo das abas
        self.tab_content = {
            self.i18n.get("options.general", "General"): [
                self.i18n.get("options.language", "Language"),
                self.i18n.get("options.auto_save", "Auto-save frequency"),
                self.i18n.get("options.game_settings", "Game settings")
            ],
            self.i18n.get("options.display", "Display"): [
                self.i18n.get("ui.resolution", "Resolution"),
                self.i18n.get("ui.fullscreen", "Fullscreen"),
                self.i18n.get("ui.vsync", "VSync")
            ],
            self.i18n.get("options.audio", "Audio"): [
                self.i18n.get("ui.master_volume", "Master volume"),
                self.i18n.get("ui.music_volume", "Music volume"),
                self.i18n.get("ui.sound_effects", "Sound effects")
            ],
            self.i18n.get("options.controls", "Controls"): [
                self.i18n.get("ui.camera_movement", "Camera movement")
            ]
        }
        
        # Atualiza altura do menu baseado no novo número de opções
        self.top_menu_height = len(self.top_menu_options) * self.top_menu_option_height
        
        # Se o menu estava aberto, ajusta a posição alvo
        if self.menu_open:
            self.top_menu_target_y = self.top_bar_height
        else:
            self.top_menu_target_y = -self.top_menu_height
        
        print(f"Textos atualizados com sucesso")
    
    def is_build_menu_open(self):
        return self.build_menu_open
    
    def get_options_popup_rect(self, surface):
        screen_width, screen_height = surface.get_size()

        width = int(screen_width * 0.6)
        height = int(screen_height * 0.6)

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        return pygame.Rect(x, y, width, height)

    def draw_options_popup(self, surface):
        if not self.options_popup_open:
            return

        popup_rect = self.get_options_popup_rect(surface)
        popup_width, popup_height = popup_rect.size
        
        # Fundo principal
        popup_surf = pygame.Surface(popup_rect.size, pygame.SRCALPHA)
        popup_surf.fill((50, 50, 50, self.options_popup_alpha))

        # Área das abas (no topo do popup)
        tabs_height = 40
        tabs_area = pygame.Rect(0, 0, popup_width, tabs_height)
        
        # Desenhar fundo das abas
        pygame.draw.rect(popup_surf, (60, 60, 60, 200), tabs_area)
        pygame.draw.rect(popup_surf, (80, 80, 80), tabs_area, 1)
        
        # Calcular largura das abas
        tab_texts = self.get_options_tabs_texts()  # Obtem textos traduzidos primeiro
        if tab_texts:  # Evita divisão por zero
            tab_width = (popup_width - (len(tab_texts) + 1) * self.tab_button_padding) // len(tab_texts)
        else:
            tab_width = 100

        tab_texts = self.get_options_tabs_texts()     
        
        # Desenhar abas
        for i, tab_text  in enumerate(tab_texts):
            x = self.tab_button_padding + i * (tab_width + self.tab_button_padding)
            tab_rect = pygame.Rect(x, 5, tab_width, tabs_height - 10)

            # Usar a chave para verificar se é a aba ativa
            tab_key = self.options_tab_keys[i]
            
            # Cor da aba ativa/inativa
            if tab_key == self.current_options_tab_key:
                color = (70, 130, 180)  # Azul para aba ativa
                text_color = (255, 255, 255)
            else:
                color = (80, 80, 80)  # Cinza para aba inativa
                text_color = (200, 200, 200)
            
            # Fundo da aba
            pygame.draw.rect(popup_surf, color, tab_rect, border_radius=4)
            pygame.draw.rect(popup_surf, (100, 100, 100), tab_rect, 1, border_radius=4)
            
            # Texto da aba
            tab_font = pygame.font.SysFont(None, 20)
            tab_text = tab_font.render(tab_text, True, text_color)
            text_rect = tab_text.get_rect(center=tab_rect.center)
            popup_surf.blit(tab_text, text_rect)
        
        # Área de conteúdo (abaixo das abas)
        content_area = pygame.Rect(
            0, 
            tabs_height, 
            popup_width, 
            popup_height - tabs_height
        )
        
        # Desenhar fundo da área de conteúdo
        pygame.draw.rect(popup_surf, (40, 40, 40, 180), content_area)
        pygame.draw.rect(popup_surf, (70, 70, 70), content_area, 1)
        
        # Desenhar conteúdo da aba atual
        content_padding = 20
        current_y = tabs_height + content_padding
        
        title_font = pygame.font.SysFont(None, 24)
        option_font = pygame.font.SysFont(None, 20)
        
        # Título da aba
        current_tab_text = self.get_current_tab_text()
        if self.current_options_tab_key == "general":
            title_text = title_font.render(self.i18n.get("ui.general_settings", "General Settings"), True, (255, 255, 255))
        elif self.current_options_tab_key == "display":
            title_text = title_font.render(self.i18n.get("ui.display_settings", "Display Settings"), True, (255, 255, 255))
        elif self.current_options_tab_key == "audio":
            title_text = title_font.render(self.i18n.get("ui.audio_settings", "Audio Settings"), True, (255, 255, 255))
        elif self.current_options_tab_key == "controls":
            title_text = title_font.render(self.i18n.get("ui.controls_settings", "Controls Settings"), True, (255, 255, 255))
        else:
            title_text = title_font.render(f"{current_tab_text} Settings", True, (255, 255, 255))
        
        popup_surf.blit(title_text, (content_padding, current_y))
        current_y += title_text.get_height() + 15
        
        # Conteúdo específico da aba
        if self.current_options_tab_key == "general":
            # Desenhar opção de idioma especial
            lang_text = option_font.render(self.i18n.get("options.language", "Language") + ":", True, (220, 220, 220))
            popup_surf.blit(lang_text, (content_padding, current_y))
            
            # Botão para selecionar idioma
            lang_button_width = 100
            self.language_button_rect = pygame.Rect(  # Salva para clique
                content_padding + 150,
                current_y - 5,
                lang_button_width,
                25
            )
            
            # Exibir idioma atual (usando i18n)
            try:
                language_names = self.i18n.get_all_language_names()
                lang_name = language_names.get(self.selected_language, self.selected_language)
            except AttributeError:
                # Fallback
                lang_name = "English" if self.selected_language == "en" else "Português"
                
            lang_button_text = option_font.render(lang_name, True, (255, 255, 255))
            
            # Desenhar botão
            pygame.draw.rect(popup_surf, (80, 80, 80), self.language_button_rect, border_radius=4)
            pygame.draw.rect(popup_surf, (120, 120, 120), self.language_button_rect, 1, border_radius=4)
            text_rect = lang_button_text.get_rect(center=self.language_button_rect.center)
            popup_surf.blit(lang_button_text, text_rect)
            
            current_y += 35
            
            # Outras opções da aba General
            tab_content = self.get_tab_content("general")
            for option_text in tab_content:
                if option_text != self.i18n.get("options.language", "Language"):
                    # Checkbox/indicator (círculo simples)
                    indicator_radius = 5
                    pygame.draw.circle(
                        popup_surf, 
                        (100, 150, 200), 
                        (content_padding + 10, current_y + 10), 
                        indicator_radius
                    )
                    
                    # Texto da opção
                    option_surface = option_font.render(option_text, True, (220, 220, 220))
                    popup_surf.blit(option_surface, (content_padding + 25, current_y))
                    current_y += option_surface.get_height() + 12
        else:
            # Para outras abas, desenhar normalmente
            tab_content = self.get_tab_content(self.current_options_tab_key)
            for option_text in tab_content:
                # Checkbox/indicator (círculo simples)
                indicator_radius = 5
                pygame.draw.circle(
                    popup_surf, 
                    (100, 150, 200), 
                    (content_padding + 10, current_y + 10), 
                    indicator_radius
                )
                
                # Texto da opção
                option_surface = option_font.render(option_text, True, (220, 220, 220))
                popup_surf.blit(option_surface, (content_padding + 25, current_y))
                current_y += option_surface.get_height() + 12
        
        # Mensagem de placeholder
        placeholder_font = pygame.font.SysFont(None, 18)
        placeholder_text = self.i18n.get("ui.settings_will_be_implemented", "Settings will be implemented soon...")
        placeholder_surface = placeholder_font.render(placeholder_text, True, (150, 150, 150))
        popup_surf.blit(
            placeholder_surface, 
            (
                popup_width // 2 - placeholder_surface.get_width() // 2,
                popup_height - 30
            )
        )

        # Desenhar seletor de idioma se estiver ativo
        if self.selecting_language:
            self.draw_language_selector(popup_surf, popup_rect)
        
        # Borda externa
        pygame.draw.rect(
            popup_surf,
            (200, 200, 200),
            popup_surf.get_rect(),
            2,
            border_radius=8
        )

        surface.blit(popup_surf, popup_rect.topleft)

    def draw_language_selector(self, popup_surf, popup_rect):
        """Desenha um popup para selecionar idioma"""
        # Calcula altura dinâmica baseada no número de idiomas
        button_height = 30
        button_spacing = 5
        padding_top = 40
        padding_bottom = 10
        
        num_languages = len(self.available_languages)
        selector_height = padding_top + (button_height * num_languages) + (button_spacing * (num_languages - 1)) + padding_bottom
        selector_width = 200

        selector_x = (popup_rect.width - selector_width) // 2
        selector_y = (popup_rect.height - selector_height) // 2
        
        # Fundo do seletor
        selector_rect = pygame.Rect(selector_x, selector_y, selector_width, selector_height)
        pygame.draw.rect(popup_surf, (30, 30, 40, 240), selector_rect, border_radius=8)
        pygame.draw.rect(popup_surf, (100, 100, 150), selector_rect, 2, border_radius=8)
        
        # Título
        title_font = pygame.font.SysFont(None, 22)
        title_popup_selector = self.i18n.get("ui.select_language", "Select Language")
        title = title_font.render(title_popup_selector, True, (255, 255, 255))
        popup_surf.blit(title, (selector_x + 10, selector_y + 10))
        
        # Botões de idioma
        button_font = pygame.font.SysFont(None, 18)
        button_y = selector_y + padding_top
        
        # Obtém todos os nomes dos idiomas da classe i18n
        try:
            language_names = self.i18n.get_all_language_names()
        except AttributeError:
            # Fallback se o método não existir
            language_names = {
                "en": "English",
                "pt": "Português",
                "de": "Deutsch",
                "es": "Español",
                "fr": "Français"
            }

        for i, lang_code in enumerate(self.available_languages):
            # Obtém o nome do idioma
            lang_name = language_names.get(lang_code, lang_code)

            button_rect = pygame.Rect(
                selector_x + 20,
                button_y + i * (button_height + 5),
                selector_width - 40,
                button_height
            )
            
            # Cor do botão
            if lang_code == self.selected_language:
                color = (70, 130, 180)  # Azul para idioma selecionado
                text_color = (255, 255, 255)
            else:
                color = (60, 60, 70)    # Cinza para outros
                text_color = (200, 200, 200)
            
            # Fundo do botão
            pygame.draw.rect(popup_surf, color, button_rect, border_radius=4)
            pygame.draw.rect(popup_surf, (100, 100, 150), button_rect, 1, border_radius=4)
            
            # Texto do botão
            lang_text = button_font.render(lang_name, True, text_color)
            text_rect = lang_text.get_rect(center=button_rect.center)
            popup_surf.blit(lang_text, text_rect)

    def draw_selected_building_info(self, surface, game_state):
        if not self.build_menu_open or not self.selected_building:
            return

        # Obtem dados atualizados de construções e recursos
        from buildings import get_building_data
        from resources import get_resource_data
        
        building_data = get_building_data()
        resource_data = get_resource_data()
        
        data = building_data[self.selected_building]

        padding = 8
        line_spacing = 4

        # PRÉ-RENDER DOS TEXTOS
        title_font = pygame.font.SysFont(None, 26)
        title_surf = title_font.render(data["name"], True, (255, 255, 255))

        lines = []
        for res, amount in data["cost"].items():
            current = game_state.resources.get(res, 0)

            # Obtem nome traduzido do recurso
            res_name = resource_data.get(res, {}).get("name", res.capitalize())

            if current >= amount:
                color = (0, 200, 0)
            else:
                color = (200, 50, 50)

            text = f"{res_name}: {amount} / {current}"
            lines.append(self.font.render(text, True, color))

        # CALCULA o TAMANHO DO FUNDO
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

        # Fundo do menu
        bg = pygame.Surface((width, height), pygame.SRCALPHA)
        bg.fill((40, 40, 40, 220))
        surface.blit(bg, (x, y))

        # Borda do menu
        pygame.draw.rect(surface, (80, 80, 80), (x, y, width, height), 1)

        for i, option in enumerate(self.top_menu_options):
            option_rect = pygame.Rect(
                x, 
                y + i * self.top_menu_option_height, 
                width, 
                self.top_menu_option_height
            )

            # Se essa opção tá com hover, desenha ofundo
            if i == self.top_menu_hover_index:
                # Fundo laranja mei transparente para hover
                hover_bg = pygame.Surface((option_rect.width, option_rect.height), pygame.SRCALPHA)
                hover_bg.fill((255, 165, 0, 80))  # Laranja com transparência
                surface.blit(hover_bg, option_rect.topleft)
                
                # Borda da opção com hover
                pygame.draw.rect(surface, (255, 200, 100, 150), option_rect, 1)

            # Texto da opção
            text = self.font.render(option, True, (255, 255, 255))
            ty = y + i * self.top_menu_option_height + (
                self.top_menu_option_height - text.get_height()
            ) // 2
            surface.blit(text, (x + 10, ty))

    def update_top_menu_hover(self, mouse_pos):
        """Atualiza qual opção do menu hambúrguer está com hover"""
        self.top_menu_hover_index = -1  # Reset
        
        if not self.menu_open:
            return
        
        # Verifica se o mouse tá em cima de alguma opção
        width = self.top_menu_width
        x = self.menu_button_rect.right - width
        y = int(self.top_menu_y)
        
        for i, option in enumerate(self.top_menu_options):
            option_rect = pygame.Rect(
                x, 
                y + i * self.top_menu_option_height, 
                width, 
                self.top_menu_option_height
            )
            if option_rect.collidepoint(mouse_pos):
                self.top_menu_hover_index = i
                break

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
        # Não mostra tooltips se popup de opções estiver aberto
        if self.options_popup_open:
            self.hover_tooltip = None
            return

        self.hover_tooltip = None

        # check recurso na barra superior
        for res, rect in getattr(self, "resource_rects", {}).items():
            if rect.collidepoint(mouse_pos):
                # Obter dados atualizados de recursos
                from resources import get_resource_data
                resource_data = get_resource_data()
                data = resource_data[res]
                
                if res == ResourceType.POPULATION:
                    self.hover_tooltip = {
                        "title": data["name"],
                        "lines": [
                            data["description"],
                            f"{self.i18n.get('ui.with_housing', 'With housing')}: {game_state.resources[res]['with_housing']}",
                            f"{self.i18n.get('ui.without_housing', 'Without housing')}: {game_state.resources[res]['without_housing']}"
                        ]
                    }
                else:
                    self.hover_tooltip = {
                        "title": data["name"],
                        "lines": [
                            data["description"],
                            f"{self.i18n.get('ui.production_per_day', 'Production per day')}: {data['production']}",
                            f"{self.i18n.get('ui.consumption_per_day', 'Consumption per day')}: {data['consumption']}"
                        ]
                    }
                return

        buttons = self.build_buttons if self.build_menu_open else self.buttons

        for button in buttons:
            if button.rect.collidepoint(mouse_pos):

                # Botão do martelo
                if button.action == "toggle_build":
                    self.hover_tooltip = {
                        "title": self.i18n.get("ui.build_mode", "Build Mode"),
                        "lines": [self.i18n.get("descriptions.build_mode", "Allows Building (Shortcut: B)")]
                    }
                    return

                # Botões de construção
                if button.action == "select_build":
                    # Obter dados atualizados de construções
                    from buildings import get_building_data
                    building_data = get_building_data()
                    data = building_data[button.data]

                    lines = [data["description"]]

                    for res, amount in data["cost"].items():
                        # Obter nome do recurso traduzido
                        from resources import get_resource_data
                        res_data = get_resource_data()
                        res_name = res_data.get(res, {}).get("name", res.capitalize())
                        lines.append(f"{res_name}: {amount}")

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
