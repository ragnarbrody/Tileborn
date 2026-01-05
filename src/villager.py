# -*- coding: utf-8 -*-

import pygame
import random
import math
from settings import TILE_SIZE
from paths import TILES_DIR
from enum import Enum

class VillagerState(Enum):
    IDLE = "idle"
    WALKING = "walking"
    WORKING = "working"
    GOING_HOME = "going_home"
    GOING_TO_WORK = "going_to_work"

class Villager:
    def __init__(self, x, y, name="", home_building=None, workplace=None):
        self.x = x  # posição em tiles
        self.y = y
        self.world_x = x * TILE_SIZE  # posição em pixels
        self.world_y = y * TILE_SIZE
        
        self.name = name or self._generate_name()
        self.state = VillagerState.IDLE
        
        self.home_building = home_building  # BuildingInstance onde mora
        self.workplace = workplace  # BuildingInstance onde trabalha
        
        # Stats básicos
        self.speed = 1.5  # tiles por segundo
        self.hunger = 100  # 0-100
        self.happiness = 100  # 0-100
        
        # Navegação
        self.target_x = None
        self.target_y = None
        self.path = []
        self.wander_radius = 10  # tiles de raio máximo para vagar
        
        # Carregar sprite
        self.sprite = pygame.image.load(TILES_DIR / "villager_1.png").convert_alpha()
        self.sprite = pygame.transform.scale(
            self.sprite,
            (TILE_SIZE, TILE_SIZE * 2)  # 1x2 tiles
        )
        
        # Animação
        self.animation_timer = 0
        self.current_frame = 0
        self.facing_right = True
        
    def _generate_name(self):
        """Gera um nome aleatório para o aldeão"""
        first_names = ["John", "Maria", "Carlos", "Anna", "Peter", "Sophia", 
                      "Luis", "Emma", "Thomas", "Isabella", "James", "Olivia"]
        last_names = ["Smith", "Johnson", "Brown", "Davis", "Miller", "Wilson",
                     "Moore", "Taylor", "Anderson", "Thomas", "Jackson"]
        
        return f"{random.choice(first_names)} {random.choice(last_names)}"
    
    def assign_to_workplace(self, workplace):
        """Atribui este aldeão a um local de trabalho"""
        if not workplace:
            return False
        
        if self.workplace:
            # Remover do trabalho atual
            self.workplace.remove_worker(self)
        
        # Adicionar ao novo trabalho
        success = workplace.add_worker(self)
        
        if success:
            print(f"{self.name} começou a trabalhar na {workplace.type}")
            self.state = VillagerState.GOING_TO_WORK
            return True
        
        return False
    
    def update(self, dt, world):
        """Atualiza o estado do aldeão"""
        self.animation_timer += dt
        
        # Atualizar estado baseado no que está fazendo
        if self.state == VillagerState.IDLE:
            self._update_idle(dt, world)
        elif self.state == VillagerState.WALKING:
            self._update_walking(dt, world)
        elif self.state == VillagerState.GOING_HOME:
            self._go_to_home(dt, world)
        elif self.state == VillagerState.GOING_TO_WORK:
            self._go_to_work(dt, world)
        elif self.state == VillagerState.WORKING:
            self._update_working(dt, world)
    
    def _update_idle(self, dt, world):
        """Lógica para quando está parado"""
        # Chance de começar a vagar
        if random.random() < 0.01 * dt * 60:  # 1% chance por frame (ajustado por dt)
            self._start_wandering(world)
    
    def _start_wandering(self, world):
        """Inicia um movimento de vagoar"""
        if self.home_building:
            # Vaguer perto de casa
            center_x = self.home_building.x + self.home_building.size[0] // 2
            center_y = self.home_building.y + self.home_building.size[1] // 2
        else:
            # Vaguer perto da posição atual
            center_x = self.x
            center_y = self.y
        
        # Escolher um destino aleatório dentro do raio
        angle = random.random() * 2 * math.pi
        distance = random.randint(3, self.wander_radius)
        
        target_x = int(center_x + math.cos(angle) * distance)
        target_y = int(center_y + math.sin(angle) * distance)
        
        # Verificar se o destino é válido
        if (0 <= target_x < world.width and 
            0 <= target_y < world.height and
            world.grid[target_y][target_x] != "water" and
            (target_x, target_y) not in world.occupied_tiles):
            
            self.target_x = target_x
            self.target_y = target_y
            self.state = VillagerState.WALKING
            self._find_path_to_target(world)
    
    def _find_path_to_target(self, world):
        """Encontra um caminho simples para o alvo (implementação básica)"""
        self.path = []
        
        # Implementação básica de pathfinding - em linha reta
        # Futuramente pode ser substituída por A*
        
        current_x, current_y = self.x, self.y
        target_x, target_y = self.target_x, self.target_y
        
        # Direção
        dx = target_x - current_x
        dy = target_y - current_y
        
        # Normalizar
        steps = max(abs(dx), abs(dy))
        if steps > 0:
            step_x = dx / steps
            step_y = dy / steps
            
            for i in range(1, steps + 1):
                next_x = int(current_x + step_x * i)
                next_y = int(current_y + step_y * i)
                
                # Verificar se o tile é acessível
                if (0 <= next_x < world.width and 
                    0 <= next_y < world.height and
                    world.grid[next_y][next_x] != "water" and
                    (next_x, next_y) not in world.occupied_tiles):
                    
                    self.path.append((next_x, next_y))
                else:
                    break
    
    def _update_walking(self, dt, world):
        """Atualiza o movimento"""
        if not self.path:
            # Chegou ao destino
            self.state = VillagerState.IDLE
            self.target_x = None
            self.target_y = None
            return
        
        # Mover para o próximo tile no caminho
        next_tile = self.path[0]
        target_world_x = next_tile[0] * TILE_SIZE + TILE_SIZE // 2
        target_world_y = next_tile[1] * TILE_SIZE + TILE_SIZE // 2
        
        # Calcular direção
        dx = target_world_x - self.world_x
        dy = target_world_y - self.world_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < 1:  # Próximo o suficiente
            self.x, self.y = next_tile
            self.path.pop(0)
            if not self.path:
                self.state = VillagerState.IDLE
                self.target_x = None
                self.target_y = None
        else:
            # Mover na direção
            speed_px = self.speed * TILE_SIZE * dt
            move_x = (dx / distance) * speed_px if distance > 0 else 0
            move_y = (dy / distance) * speed_px if distance > 0 else 0
            
            self.world_x += move_x
            self.world_y += move_y
            
            # Atualizar posição em tiles
            self.x = int(self.world_x // TILE_SIZE)
            self.y = int(self.world_y // TILE_SIZE)
            
            # Atualizar direção do sprite
            if abs(dx) > 0:
                self.facing_right = dx > 0
    
    def _go_to_home(self, dt, world):
        """Vai para casa"""
        if self.home_building:
            home_center_x = self.home_building.x + self.home_building.size[0] // 2
            home_center_y = self.home_building.y + self.home_building.size[1] // 2
            
            if abs(self.x - home_center_x) <= 1 and abs(self.y - home_center_y) <= 1:
                self.state = VillagerState.IDLE
            else:
                self.target_x = home_center_x
                self.target_y = home_center_y
                self._find_path_to_target(world)
                self.state = VillagerState.WALKING
        else:
            self.state = VillagerState.IDLE
    
    def _go_to_work(self, dt, world):
        """Vai para o trabalho"""
        if self.workplace:
            work_center_x = self.workplace.x + self.workplace.size[0] // 2
            work_center_y = self.workplace.y + self.workplace.size[1] // 2
            
            if abs(self.x - work_center_x) <= 1 and abs(self.y - work_center_y) <= 1:
                self.state = VillagerState.WORKING
            else:
                self.target_x = work_center_x
                self.target_y = work_center_y
                self._find_path_to_target(world)
                self.state = VillagerState.WALKING
        else:
            self.state = VillagerState.IDLE
    
    def _update_working(self, dt, world):
        """Lógica para quando está trabalhando"""
        # Trabalhar por um tempo
        if random.random() < 0.005 * dt * 60:  # 0.5% chance por frame de parar
            self.state = VillagerState.GOING_HOME
    
    def draw(self, surface, camera):
        """Desenha o aldeão na tela"""
        screen_x, screen_y = camera.apply(self.world_x, self.world_y)
        
        # Ajustar para o sprite de 2 tiles de altura (desenhar a partir do "pé")
        screen_y -= TILE_SIZE  # Subir um tile para alinhar
        
        sprite_to_draw = self.sprite
        if not self.facing_right:
            sprite_to_draw = pygame.transform.flip(self.sprite, True, False)
        
        surface.blit(sprite_to_draw, (screen_x, screen_y))
        
        # Desenhar nome (debug)
        if self.name:
            font = pygame.font.SysFont(None, 12)
            name_text = font.render(self.name, True, (255, 255, 255))
            name_rect = name_text.get_rect(center=(screen_x + TILE_SIZE//2, screen_y - 10))
            surface.blit(name_text, name_rect)