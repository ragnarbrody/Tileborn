# -*- coding: utf-8 -*-
# tasks.py

from enum import Enum
from resources import ResourceType
import math

class TaskType(Enum):
    GATHER = "gather"      # Coletar recursos naturais
    DELIVER = "deliver"    # Entregar recursos
    WORK = "work"          # Trabalhar em um prédio
    BUILD = "build"        # Construir algo
    IDLE = "idle"          # Ocioso
    MOVE = "move"          # Movimentação

class Task:
    def __init__(self, task_type, target=None, resource_type=None, amount=1, building=None):
        self.task_type = task_type
        self.target = target  # Pode ser um objeto (árvore, pedra) ou coordenadas (x, y)
        self.resource_type = resource_type
        self.amount = amount
        self.building = building  # Prédio relacionado (para trabalho ou entrega)
        self.progress = 0.0
        self.duration = 5.0  # Tempo padrão para completar a task
        self.completed = False
        self.failed = False
        
    def update(self, dt, villager, world):
        """Atualiza o progresso da task"""
        if self.completed or self.failed:
            return True
            
        self.progress += dt
        
        if self.progress >= self.duration:
            self.completed = True
            return self._complete(villager, world)
            
        return False
        
    def _complete(self, villager, world):
        """Executa a ação quando a task é completada"""
        if self.task_type == TaskType.GATHER:
            return self._complete_gather(villager, world)
        elif self.task_type == TaskType.DELIVER:
            return self._complete_deliver(villager, world)
        elif self.task_type == TaskType.WORK:
            return self._complete_work(villager, world)
        return True
        
    def _complete_gather(self, villager, world):
        """Completa uma tarefa de coleta"""
        if not self.target or not self.resource_type:
            return False
            
        # Para árvores
        if hasattr(self.target, 'type') and self.target.type == "tree":
            if self.target.is_cut:
                return False
                
            # Pega os recursos da árvore
            resources = self.target.resources
            if resources and self.resource_type in resources:
                amount = resources[self.resource_type]
                
                # Adiciona ao inventário do villager
                if villager.add_to_inventory(self.resource_type, amount):
                    # Marca a árvore como cortada
                    self.target.is_cut = True
                    # Remove o cortador
                    if hasattr(self.target, 'cutter'):
                        self.target.cutter = None
                    return True
                    
        return False
        
    def _complete_deliver(self, villager, world):
        """Completa uma tarefa de entrega"""
        if not self.building:
            return False
            
        # Entrega todos os recursos do inventário
        for resource_type, amount in villager.inventory.items():
            if amount > 0:
                if hasattr(self.building, 'add_resource'):
                    self.building.add_resource(resource_type, amount)
                villager.inventory[resource_type] = 0
                
        villager.inventory_used = 0
        return True
        
    def _complete_work(self, villager, world):
        """Completa uma tarefa de trabalho"""
        # Trabalho padrão em prédios
        # Pode ser sobrescrito por tipos específicos de trabalho
        return True
        
    def can_start(self, villager, world):
        """Verifica se a task pode ser iniciada"""
        if self.task_type == TaskType.GATHER:
            return self._can_start_gather(villager, world)
        elif self.task_type == TaskType.DELIVER:
            return self._can_start_deliver(villager, world)
        return True
        
    def _can_start_gather(self, villager, world):
        """Verifica se pode começar a coletar"""
        if not self.target:
            return False
            
        # Verifica se o alvo ainda está disponível
        if hasattr(self.target, 'is_cut') and self.target.is_cut:
            return False
            
        # Verifica se outro villager já está coletando
        if hasattr(self.target, 'cutter') and self.target.cutter and self.target.cutter != villager:
            return False
            
        # Verifica se tem espaço no inventário
        if self.resource_type:
            estimated_amount = 1  # Quantidade estimada
            if hasattr(self.target, 'resources') and self.resource_type in self.target.resources:
                estimated_amount = self.target.resources[self.resource_type]
                
            if not villager.can_pickup_resource(self.resource_type, estimated_amount):
                return False
                
        return True
        
    def _can_start_deliver(self, villager, world):
        """Verifica se pode começar a entregar"""
        return villager.get_inventory_total() > 0