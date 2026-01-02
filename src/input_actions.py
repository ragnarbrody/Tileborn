# -*- coding: utf-8 -*-

import pygame

ACTIONS = {
    "TOGGLE_BUILD_MENU": [pygame.K_b],
}

def is_action_pressed(action_name):
    keys = pygame.key.get_pressed()
    return any(keys[key] for key in ACTIONS.get(action_name, []))
