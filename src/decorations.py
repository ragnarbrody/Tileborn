# decorations.py
# -*- coding: utf-8 -*-

import pygame
import random
from settings import TILE_SIZE
from paths import TILES_DIR
from resources import ResourceType

class Tree:
    def __init__(self, tile_x, tile_y, width=1, height=2, sprite_name="tree_1.png"):
        self.x = tile_x
        self.y = tile_y
        self.width = width      # largura em tiles
        self.height = height    # altura em tiles
        self.type = "tree"      # Identificador do tipo
        self.resources = {
            ResourceType.WOOD: random.randint(3, 6)  # Cada árvore dá 3-6 madeiras
        }
        self.is_cut = False     # Se já foi cortada
        self.is_cutting = False # Se está sendo cortada no momento
        self.cutting_progress = 0.0
        self.cutting_time = 5.0  # Segundos para cortar completamente

        self.cutter = None
        
        # Sprite normal
        self.sprite = pygame.image.load(
            TILES_DIR / sprite_name
        ).convert_alpha()
        self.sprite = pygame.transform.scale(
            self.sprite,
            (TILE_SIZE * self.width, TILE_SIZE * self.height)
        )
        
        # Sprite cortada (stump - toco)
        self.stump_sprite = None
        try:
            self.stump_sprite = pygame.image.load(
                TILES_DIR / "tree_stump.png"
            ).convert_alpha()
            self.stump_sprite = pygame.transform.scale(
                self.stump_sprite,
                (TILE_SIZE, TILE_SIZE)
            )
        except:
            # Se não tiver sprite de toco, usa um quadrado marrom
            self.stump_sprite = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.stump_sprite.fill((101, 67, 33))

    def cut(self, dt, cutter=None):
        """Corta a árvore"""
        if self.is_cut:
            return None
            
        if cutter and not self.cutter:
            self.cutter = cutter
            
        self.is_cutting = True
        self.cutting_progress += dt
        
        if self.cutting_progress >= self.cutting_time:
            self.is_cut = True
            self.is_cutting = False
            cutter_ref = self.cutter
            self.cutter = None  # Limpa o cortador
            return self.resources
            
        return None

    def get_cut_progress_percentage(self):
        """Retorna o progresso do corte em porcentagem"""
        return min(100, (self.cutting_progress / self.cutting_time) * 100)
    
    def is_cutting_by(self, villager):
        """Verifica se está sendo cortada por um aldeão específico"""
        # Você precisará armazenar quem está cortando a árvore
        # Vamos adicionar um atributo para isso
        if not hasattr(self, 'cutter'):
            return False
        return self.cutter == villager 

    def draw(self, surface, camera):
        world_x = self.x * TILE_SIZE
        # sobe (height - 1) tiles
        world_y = (self.y - (self.height - 1)) * TILE_SIZE

        screen_x, screen_y = camera.apply(world_x, world_y)
        
        if self.is_cut:
            # Desenha o toco (centrado na base da árvore)
            stump_x = self.x * TILE_SIZE
            stump_y = self.y * TILE_SIZE
            stump_screen_x, stump_screen_y = camera.apply(stump_x, stump_y)
            
            if self.stump_sprite:
                surface.blit(self.stump_sprite, (stump_screen_x, stump_screen_y))
            
            # Opcional: desenha indicador de árvore cortada
            if False:  # Para debug
                font = pygame.font.SysFont(None, 12)
                text = font.render("Cortada", True, (255, 0, 0))
                surface.blit(text, (stump_screen_x, stump_screen_y - 15))
        else:
            # Desenha a árvore normal
            surface.blit(self.sprite, (screen_x, screen_y))
            
            # Se está sendo cortada, desenha uma barra de progresso
            if self.is_cutting:
                progress = self.get_cut_progress_percentage()
                
                # Barra de progresso acima da árvore
                bar_width = 30
                bar_height = 5
                bar_x = screen_x + (self.width * TILE_SIZE // 2) - bar_width // 2
                bar_y = screen_y - 10
                
                # Fundo da barra
                pygame.draw.rect(surface, (50, 50, 50), 
                                (bar_x, bar_y, bar_width, bar_height))
                
                # Preenchimento
                fill_width = int(bar_width * (progress / 100))
                pygame.draw.rect(surface, (100, 200, 100), 
                                (bar_x, bar_y, fill_width, bar_height))

# Outras decorações que podem ser adicionadas futuramente
class Rock:
    def __init__(self, tile_x, tile_y, sprite_name="rock_1.png"):
        self.x = tile_x
        self.y = tile_y
        self.type = "rock"
        self.resources = {
            ResourceType.STONE: random.randint(2, 4)
        }
        self.is_mined = False
        
        self.sprite = pygame.image.load(
            TILES_DIR / sprite_name
        ).convert_alpha()
        self.sprite = pygame.transform.scale(
            self.sprite,
            (TILE_SIZE, TILE_SIZE)
        )

    def draw(self, surface, camera):
        world_x = self.x * TILE_SIZE
        world_y = self.y * TILE_SIZE
        screen_x, screen_y = camera.apply(world_x, world_y)
        surface.blit(self.sprite, (screen_x, screen_y))

class Bush:
    def __init__(self, tile_x, tile_y, sprite_name="bush_1.png"):
        self.x = tile_x
        self.y = tile_y
        self.type = "bush"
        self.resources = {
            ResourceType.FOOD: random.randint(1, 3)
        }
        self.is_harvested = False
        
        self.sprite = pygame.image.load(
            TILES_DIR / sprite_name
        ).convert_alpha()
        self.sprite = pygame.transform.scale(
            self.sprite,
            (TILE_SIZE, TILE_SIZE)
        )

    def draw(self, surface, camera):
        world_x = self.x * TILE_SIZE
        world_y = self.y * TILE_SIZE
        screen_x, screen_y = camera.apply(world_x, world_y)
        surface.blit(self.sprite, (screen_x, screen_y))