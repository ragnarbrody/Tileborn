# -*- coding: utf-8 -*-

from resources import ResourceType

class GameState:
    def __init__(self):
        self.resources = {
            ResourceType.WOOD: 100,
            ResourceType.STONE: 100,
            ResourceType.FOOD: 100,
            ResourceType.GOLD: 20,
        }

    def has_resources(self, cost: dict):
        for res, amount in cost.items():
            if self.resources.get(res, 0) < amount:
                return False
        return True

    def consume_resources(self, cost: dict):
        for res, amount in cost.items():
            self.resources[res] -= amount

    def add_resource(self, res, amount):
        self.resources[res] += amount
