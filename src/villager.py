# -*- coding: utf-8 -*-

import pygame
import random
import math
from settings import TILE_SIZE
from paths import TILES_DIR
from enum import Enum
from resources import ResourceType


class VillagerState(Enum):
    IDLE = "idle"
    WALKING = "walking"
    WORKING = "working"
    GATHERING = "gathering"
    DELIVERING = "delivering" 
    GOING_HOME = "going_home"
    GOING_TO_WORK = "going_to_work"

class Villager:
    def __init__(self, x, y, first_name="", last_name="", home_building=None, workplace=None):
        self.x = x  # posição em tiles
        self.y = y
        self.world_x = x * TILE_SIZE  # posição em pixels
        self.world_y = y * TILE_SIZE
        
        # Nome e identidade
        self.first_name = first_name or self._generate_first_name()
        self.last_name = last_name or self._generate_last_name()
        self.full_name = f"{self.first_name} {self.last_name}"
        
        # Inventário
        self.inventory = {
            ResourceType.WOOD: 0,
            ResourceType.STONE: 0,
            ResourceType.FOOD: 0,
            ResourceType.GOLD: 0
        }
        self.inventory_capacity = 10  # Capacidade total de slots
        self.inventory_used = 0

        self.state = VillagerState.IDLE
        
        self.home_building = home_building  # BuildingInstance onde mora
        self.workplace = workplace  # BuildingInstance onde trabalha
        
        # Stats básicos
        self.speed = 1.5  # tiles por segundo
        self.hunger = 100  # 0-100
        self.happiness = 100  # 0-100
        self.stamina = 100  # 0-100 (pra trabalho)
        self.skill_level = 1  # Nível de habilidade (afeta eficiência)
        
        # Navegação
        self.target_x = None
        self.target_y = None
        self.path = []
        self.wander_radius = 10  # tiles de raio máximo para vagar

        # Trabalho específico
        self.current_task = None  # Tipo de recurso que está coletando
        self.task_progress = 0  # Progresso na tarefa atual
        self.task_duration = 5.0  # Segundos para completar uma tarefa
        
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

        # Controle para arvores
        self.stuck_timer = 0  # Tempo tentando chegar na mesma árvore
        self.max_stuck_time = 5.0  # segundos antes de desistir
        self.trees_tried = []  # Lista de arvores já tentadas
        
    def _generate_first_name(self):
        """Gera um primeiro nome aleatório para o aldeão"""
        first_names = ["John", "Maria", "Carlos", "Anna", "Peter", "Sophia", 
                      "Luis", "Emma", "Thomas", "Isabella", "James", "Olivia",
                      "William", "Charlotte", "Henry", "Amelia", "George", "Mia",
                      "Jack", "Harper", "Leo", "Evelyn", "Arthur", "Abigail", "Lucas",
                      "Vicente", "Valéria", "Carolina", "Amanda", "Gustavo", "Pedro",
                      "Luciano", "Pablo", "Lorrainy", "Isabelle", "Vicky", "Kadu", "Italo",
                      "Mandy"]
        return random.choice(first_names)
    
    def _generate_last_name(self):
        """Gera um sobrenome aleatório para o aldeão"""
        last_names = ["Smith", "Johnson", "Brown", "Davis", "Miller", "Wilson",
                     "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White",
                     "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson",
                     "Clark", "Rodriguez", "Lewis", "Lee", "Walker", "Hall", "Lima", "Dias",
                     "Pais", "Araújo", "Ramon"]
        return random.choice(last_names)
    
    @property
    def name(self):
        """Retorna o nome completo (pra compatibilidade)"""
        return self.full_name
    
    def can_pickup_resource(self, resource_type, amount=1):
        """Verifica se pode pegar um recurso"""
        return self.inventory_used + amount <= self.inventory_capacity
    
    def add_to_inventory(self, resource_type, amount=1):
        """Adiciona recurso ao inventário"""
        if self.can_pickup_resource(resource_type, amount):
            self.inventory[resource_type] += amount
            self.inventory_used += amount
            return True
        return False
    
    def remove_from_inventory(self, resource_type, amount=1):
        """Remove recurso do inventário"""
        if self.inventory.get(resource_type, 0) >= amount:
            self.inventory[resource_type] -= amount
            self.inventory_used -= amount
            return True
        return False
    
    def get_inventory_total(self):
        """Retorna o total de itens no inventário"""
        return self.inventory_used
    
    def get_inventory_space(self):
        """Retorna espaço restante no inventário"""
        return self.inventory_capacity - self.inventory_used
    
    def assign_to_workplace(self, workplace):
        """Atribui essee aldeão a um local de trabalho"""
        if not workplace:
            return False
        
        if self.workplace:
            # Remove do trabalho atual
            self.workplace.remove_worker(self)
        
        # Adiciona ao novo trabalho
        success = workplace.add_worker(self)
        
        if success:
            print(f"{self.name} começou a trabalhar na {workplace.type}")
            self.state = VillagerState.GOING_TO_WORK
            return True
        
        return False
    
    def assign_to_home(self, home):
        """Atribui esse aldeão a uma casa"""
        if not home:
            return False
        
        if self.home_building:
            # Remove da casa atual
            self.home_building.remove_inhabitant(self)
        
        # Adiciona à nova casa
        success = home.add_inhabitant(self)
        
        if success:
            print(f"{self.full_name} mudou-se para uma casa")
            return True
        
        return False
    
    def update(self, dt, world):
        """Atualiza o estado do aldeão"""
        self.animation_timer += dt

        # Verificação geral de travamento
        if self.stuck_timer > 15.0:  # 15 segundos travado
            print(f"{self.full_name}: RESETADO por travamento (stuck_timer={self.stuck_timer})")
            self._reset_state()
            
        # Atualiza o estado baseado no que tá fazendo
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
        elif self.state == VillagerState.GATHERING:
            self._update_gathering(dt, world)
        elif self.state == VillagerState.DELIVERING:
            self._update_delivering(dt, world)

    def _move_to_clear_area(self, world):
        """Move o aldeão para uma área mais aberta"""
        # Procura um tile vazio próximo
        for radius in range(1, 10):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if abs(dx) != radius and abs(dy) != radius:
                        continue
                    
                    new_x = self.x + dx
                    new_y = self.y + dy
                    
                    if (0 <= new_x < world.width and 
                        0 <= new_y < world.height and
                        world.grid[new_y][new_x] != "water" and
                        (new_x, new_y) not in world.occupied_tiles):
                        
                        self.x = new_x
                        self.y = new_y
                        self.world_x = new_x * TILE_SIZE + TILE_SIZE // 2
                        self.world_y = new_y * TILE_SIZE + TILE_SIZE // 2
                        print(f"{self.full_name} movido para área mais aberta ({new_x}, {new_y})")
                        return True
        
        return False

    def _reset_state(self):
        """Reseta o estado do aldeão para evitar travamentos"""
        self.state = VillagerState.IDLE
        self.target_x = None
        self.target_y = None
        self.path = []
        self.current_tree = None
        self.stuck_timer = 0
        self.trees_tried = []

        # Tenta se mover para uma área mais aberta
        if hasattr(self, 'world'):
            self._move_to_clear_area(self.world)
    
    def _update_idle(self, dt, world):
        """Lógica para quando está parado"""
        # Se tem trabalho e inventário vazio, começa a trabalhar
        if self.workplace and self.get_inventory_total() == 0:
            if self.workplace.type == "sawmill":
                self.current_task = ResourceType.WOOD
                self.state = VillagerState.GATHERING
                self._find_tree_to_cut(world)
                return
        
        # Chance de começar a vagar
        if random.random() < 0.01 * dt * 60:
            self._start_wandering(world)

    def _find_tree_to_cut(self, world):
        """Encontra uma árvore próxima para cortar"""
        # Procura árvores próximas
        trees = []
        for deco in world.decorations:
            if (hasattr(deco, 'type') and deco.type == "tree" and 
                not deco.is_cut and deco not in self.trees_tried and
                not (hasattr(deco, 'is_cutting') and deco.is_cutting)):
                # Verifica se outro trabalhador já está cortando
                is_being_cut_by_other = False
                for villager in world.villagers:
                    if villager != self and hasattr(villager, 'current_tree') and villager.current_tree == deco:
                        is_being_cut_by_other = True
                        break
                
                if not is_being_cut_by_other:
                    # Calcula distância até a base da arvore
                    dist = math.sqrt((self.x - deco.x)**2 + (self.y - deco.y)**2)
                    if dist < 25:  # o raio de busca
                        trees.append((deco, dist))
        
        if trees:
            # Ordena pela distancia
            trees.sort(key=lambda x: x[1])
            nearest_tree, _ = trees[0]
            self.current_tree = nearest_tree
            
            # Se já tá perto o suficiente, começa a cortar
            if self._is_near_tree(nearest_tree):
                self.state = VillagerState.GATHERING
                self.stuck_timer = 0
                return
            
            # Se não ta perto, tenta caminhar até ela
            self.target_x = nearest_tree.x + nearest_tree.width // 2
            self.target_y = nearest_tree.y
            self._find_path_to_target(world)
            self.state = VillagerState.WALKING
            self.stuck_timer = 0  # Reseta o timer
        else:
            # Não encontrou arvores, volta ao trabalho
            self.state = VillagerState.WORKING
            self.stuck_timer = 0
            self.trees_tried = []  # Limpa lista de arvores tentadas
            print(f"{self.full_name}: Nenhuma árvore disponível para cortar")

    def _update_gathering(self, dt, world):
        """Atualiza o estado de coleta"""
        if not hasattr(self, 'current_tree') or not self.current_tree:
            self.state = VillagerState.WORKING
            self.stuck_timer = 0
            return
        
        tree = self.current_tree
        
        # VERIFICAÇÃO CRÍTICA: A árvore ainda existe e não foi cortada?
        if tree.is_cut:
            print(f"{self.full_name}: A árvore já foi cortada, procurando outra")
            self.current_tree = None
            self.state = VillagerState.GATHERING
            return
        
        # Verifica se está perto o suficiente da arvore
        if self._is_near_tree(tree):
            # VERIFICA se outro trabalhador já está cortando esta árvore
            other_villager_cutting = False
            for villager in world.villagers:
                if (villager != self and 
                    hasattr(villager, 'current_tree') and 
                    villager.current_tree == tree):
                    other_villager_cutting = True
                    break

            if tree.is_cutting and other_villager_cutting:
                print(f"{self.full_name}: Outro trabalhador já está cortando esta árvore, procurando outra")
                if tree not in self.trees_tried:
                    self.trees_tried.append(tree)
                self.current_tree = None
                self.state = VillagerState.GATHERING
                return
            
            # Corta a arvre
            tree.is_cutting = True
            resources = tree.cut(dt)
            
            if resources:
                # Arvore cortada completamente
                wood_amount = resources.get(ResourceType.WOOD, 0)
                if wood_amount > 0:
                    if self.can_pickup_resource(ResourceType.WOOD, wood_amount):
                        if self.add_to_inventory(ResourceType.WOOD, wood_amount):
                            print(f"{self.full_name} coletou {wood_amount} {ResourceType.WOOD}")
                    else:
                        print(f"{self.full_name}: Inventário cheio, não pode coletar {wood_amount} madeira")
                else:
                    print(f"{self.full_name}: Árvore cortada mas não deu madeira (wood_amount=0)")
                
                # Limpa referência da árvore
                self.current_tree = None
                tree.is_cutting = False
                
                # Verifica se o inventário tá cheio
                if self.get_inventory_total() >= self.inventory_capacity:
                    # Vai entregar os recursos
                    self.state = VillagerState.DELIVERING
                    self._go_to_deliver(world)
                else:
                    # Continua coletando
                    self._find_tree_to_cut(world)
            else:
                # Ainda cortando a arvore
                #print(f"{self.full_name} cortando árvore...")
                pass
        else:
            # Ainda tentando chegar na arvore
            self.state = VillagerState.WALKING
            self.stuck_timer += dt
            
            # Se ficou preso por muito tempo, desiste dessa arvore
            if self.stuck_timer > self.max_stuck_time:
                print(f"{self.full_name} desistiu da árvore (muito tempo tentando)")
                
                # Marca a árvore como "tentada"
                if self.current_tree and self.current_tree not in self.trees_tried:
                    self.trees_tried.append(self.current_tree)
                
                self.current_tree = None
                self.stuck_timer = 0
                self.state = VillagerState.GATHERING  # Tenta encontrar outra

    def _go_to_deliver(self, world):
        """Vai entregar recursos no local de trabalho"""
        if self.workplace:
            work_center_x = self.workplace.x + self.workplace.size[0] // 2
            work_center_y = self.workplace.y + self.workplace.size[1] // 2
            
            self.target_x = work_center_x
            self.target_y = work_center_y
            self._find_path_to_target(world)
            self.state = VillagerState.WALKING

    def _update_delivering(self, dt, world):
        """Atualiza o estado de entrega"""
        if not self.workplace:
            self.state = VillagerState.IDLE
            return
        
        work_center_x = self.workplace.x + self.workplace.size[0] // 2
        work_center_y = self.workplace.y + self.workplace.size[1] // 2
        
        if abs(self.x - work_center_x) <= 1 and abs(self.y - work_center_y) <= 1:
            # Entrega os recursos
            for resource_type, amount in self.inventory.items():
                if amount > 0:
                    # Adiciona ao armazenamento do prédio (ou diretamente ao game_state)
                    if hasattr(self.workplace, 'add_resource'):
                        self.workplace.add_resource(resource_type, amount)
                    else:
                        # Fallback: adiciona diretamente ao mundo (vai ser implementado depois)
                        pass
                    
                    self.inventory[resource_type] = 0
            
            self.inventory_used = 0
            print(f"{self.full_name} entregou recursos na {self.workplace.type}")
            
            # Volta a coletar
            self.state = VillagerState.GATHERING
            self._find_tree_to_cut(world)
    
    def _start_wandering(self, world):
        """Inicia um movimento de vagar"""
        if self.home_building:
            # Vagar perto de casa
            center_x = self.home_building.x + self.home_building.size[0] // 2
            center_y = self.home_building.y + self.home_building.size[1] // 2
        else:
            # Vagar perto da posição atual
            center_x = self.x
            center_y = self.y
        
        # Escolhe um destino aleatório dentro do raio
        angle = random.random() * 2 * math.pi
        distance = random.randint(3, self.wander_radius)
        
        target_x = int(center_x + math.cos(angle) * distance)
        target_y = int(center_y + math.sin(angle) * distance)
        
        # Verifica se o destino é válido
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
                
                # Verifica se o tile é acessível
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
            if self.state == VillagerState.WALKING:
                # Verifica qual era o estado original
                if self.current_task == ResourceType.WOOD:
                    self.state = VillagerState.GATHERING
                elif self.state == VillagerState.GOING_TO_WORK:
                    self.state = VillagerState.WORKING
                elif self.state == VillagerState.GOING_HOME:
                    self.state = VillagerState.IDLE
                elif self.state == VillagerState.DELIVERING:
                    self.state = VillagerState.DELIVERING
                else:
                    self.state = VillagerState.IDLE
            
            self.target_x = None
            self.target_y = None
            self.stuck_timer = 0
            return
        
        # Move para o próximo tile no caminho
        next_tile = self.path[0]
        target_world_x = next_tile[0] * TILE_SIZE + TILE_SIZE // 2
        target_world_y = next_tile[1] * TILE_SIZE + TILE_SIZE // 2
        
        # Calcula a direção
        dx = target_world_x - self.world_x
        dy = target_world_y - self.world_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < 1:  # Próximo o suficiente
            self.x, self.y = next_tile
            self.world_x = next_tile[0] * TILE_SIZE + TILE_SIZE // 2
            self.world_y = next_tile[1] * TILE_SIZE + TILE_SIZE // 2
            self.path.pop(0)
            
            if not self.path:
                # Atualiza estado baseado no objetivo
                if self.current_task == ResourceType.WOOD:
                    self.state = VillagerState.GATHERING
                elif self.state == VillagerState.GOING_TO_WORK:
                    self.state = VillagerState.WORKING
                elif self.state == VillagerState.GOING_HOME:
                    self.state = VillagerState.IDLE
                elif self.state == VillagerState.DELIVERING:
                    self.state = VillagerState.DELIVERING
                else:
                    self.state = VillagerState.IDLE
        else:
            # Move na direção
            speed_px = self.speed * TILE_SIZE * dt
            move_x = (dx / distance) * speed_px if distance > 0 else 0
            move_y = (dy / distance) * speed_px if distance > 0 else 0
            
            old_x, old_y = self.world_x, self.world_y
            self.world_x += move_x
            self.world_y += move_y

            # Verifica se realmente se moveu
            moved_distance = math.sqrt((self.world_x - old_x)**2 + (self.world_y - old_y)**2)
            
            # Atualiza a posição em tiles
            self.x = int(self.world_x // TILE_SIZE)
            self.y = int(self.world_y // TILE_SIZE)
            
            # Atualiza direção do sprite
            if abs(dx) > 0:
                self.facing_right = dx > 0

            # Incrementa o stuck_timer se não está se movendo bem
            if moved_distance < 0.1:  # Quase não se moveu
                self.stuck_timer += dt
            else:
                self.stuck_timer = max(0, self.stuck_timer - dt * 2)
    
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
        # Se está em uma serraria e tem inventário vazio, começa a coletar
        if self.workplace and self.workplace.type == "sawmill":
            if self.get_inventory_total() == 0:
                self.current_task = ResourceType.WOOD
                self.state = VillagerState.GATHERING
                self._find_tree_to_cut(world)
        
        # Trabalha por um tempo
        if random.random() < 0.005 * dt * 60:  # 0.5% chance por frame de parar
            self.state = VillagerState.GOING_HOME

    def _is_near_tree(self, tree):
        """Verifica se está perto o suficiente para cortar a árvore"""
        if not tree:
            return False
        
        # Distância em tiles (usando distância de Chebyshev para grid, vi num fórum que é melhor pra esse cenário)
        dist_x = abs(self.x - (tree.x + tree.width // 2))
        dist_y = abs(self.y - tree.y)
        
        # Pode cortar se estiver a até 2 tiles de distância
        return dist_x <= 2 and dist_y <= 2
    
    def draw(self, surface, camera):
        """Desenha o aldeão na tela"""
        screen_x, screen_y = camera.apply(self.world_x, self.world_y)
        
        # Ajusta para o sprite de 2 tiles de altura (desenha a partir do "pé")
        screen_y -= TILE_SIZE  # Sobe um tile para alinhar
        
        sprite_to_draw = self.sprite
        if not self.facing_right:
            sprite_to_draw = pygame.transform.flip(self.sprite, True, False)
        
        surface.blit(sprite_to_draw, (screen_x, screen_y))
        
        # Desenha o nome (debug)
        if self.full_name:
            font = pygame.font.SysFont(None, 12)
            name_text = font.render(self.first_name, True, (255, 255, 255))
            name_rect = name_text.get_rect(center=(screen_x + TILE_SIZE//2, screen_y - 10))
            surface.blit(name_text, name_rect)
            
            # Desenha indicador de inventário (debug)
            if self.get_inventory_total() > 0:
                inv_text = font.render(f"📦{self.get_inventory_total()}", True, (200, 200, 100))
                inv_rect = inv_text.get_rect(center=(screen_x + TILE_SIZE//2, screen_y - 25))
                surface.blit(inv_text, inv_rect)