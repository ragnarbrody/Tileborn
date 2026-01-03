# utils.py
import importlib
import pygame

def reload_all_texts(hud_instance):
    """Recarrega todos os textos do jogo"""
    import resources
    import buildings
    
    # Recarrega os módulos
    importlib.reload(resources)
    importlib.reload(buildings)
    
    # Obtém os dados atualizados das funções
    from resources import get_resource_data
    from buildings import get_building_data
    
    # Atualiza as variáveis globais nos próprios módulos
    resources.RESOURCE_DATA = get_resource_data()
    buildings.BUILDING_DATA = get_building_data()
    
    # Importa as constantes atualizadas
    from resources import RESOURCE_DATA
    from buildings import BUILDING_DATA
    
    # Atualiza textos do HUD
    hud_instance.update_language_texts()
    hud_instance.create_main_buttons()
    hud_instance.create_build_buttons()
    
    # Atualiza ícones de recursos
    hud_instance.resource_icons = {}
    for res, data in RESOURCE_DATA.items():
        icon = pygame.image.load(data["icon"]).convert_alpha()
        icon = pygame.transform.scale(icon, (hud_instance.resource_icon_size, hud_instance.resource_icon_size))
        hud_instance.resource_icons[res] = icon
    
    return RESOURCE_DATA, BUILDING_DATA