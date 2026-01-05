# i18n.py
import json
from pathlib import Path
import sys

class I18n:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True

        # Detectar se está rodando como executável
        if getattr(sys, 'frozen', False):
            # Para executável PyInstaller
            base_path = Path(sys._MEIPASS)
        else:
            # Para desenvolvimento
            base_path = Path(__file__).parent.parent
        
        # Caminho para a pasta de idiomas
        self.locales_dir = base_path / "assets" / "locales"
        self.locales_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_lang = "en"  # Idioma padrão
        self.translations = {}
        self.load_language(self.current_lang)
    
    def load_language(self, lang_code):
        """Carrega um arquivo de idioma"""
        lang_file = self.locales_dir / f"{lang_code}.json"
        
        # Se o arquivo não existe, cria um padrão em inglês
        if not lang_file.exists():
            print(f"Arquivo de idioma não encontrado: {lang_file}")
            self.create_default_english_file()
            lang_file = self.locales_dir / "en.json"
        
        try:
            with open(lang_file, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
            self.current_lang = lang_code
            print(f"Idioma carregado: {lang_code}")
        except Exception as e:
            print(f"Erro ao carregar idioma {lang_code}: {e}")
            # Fallback para inglês
            self.translations = {}
    
    def create_default_english_file(self):
        """Cria um arquivo padrão em inglês se não existir"""
        default_translations = {
            "menu": {
                "save": "Save",
                "options": "Options",
                "quit": "Quit"
            },
            "options": {
                "general": "General",
                "display": "Display",
                "audio": "Audio",
                "language": "Language",
                "auto_save": "Auto-save frequency",
                "game_settings": "Game settings",
                "controls": "Controls"
            },
            "resources": {
                "wood": "Wood",
                "stone": "Stone",
                "food": "Food",
                "gold": "Gold",
                "population": "Population"
            },
            "buildings": {
                "house": "House",
                "sawmill": "Sawmill",
                "townhall": "Town Hall",
                "dirt_road": "Dirt Road"
            },
            "descriptions": {
                "wood_desc": "Used for building houses and structures.",
                "stone_desc": "Used for building strong structures.",
                "food_desc": "Feeds your population.",
                "gold_desc": "Used for trade and upgrades.",
                "population_desc": "Your citizens count.",
                "house_desc": "A home for your inhabitants.",
                "sawmill_desc": "A place to get some wood.",
                "townhall_desc": "A place where the town is administrated.",
                "dirt_road_desc": "Something to your citizen walk on.",
                "build_mode": "Allows Building (Shortcut: B)"
            },
            "ui": {
                "build_mode": "Build Mode",
                "settings_will_be_implemented": "Settings will be implemented soon...",
                "general_settings": "General Settings",
                "display_settings": "Display Settings",
                "audio_settings": "Audio Settings",
                "resolution": "Resolution",
                "fullscreen": "Fullscreen",
                "vsync": "VSync",
                "master_volume": "Master volume",
                "music_volume": "Music volume",
                "sound_effects": "Sound effects",
                "with_housing": "With housing",
                "without_housing": "Without housing",
                "production_per_day": "Production per day",
                "consumption_per_day": "Consumption per day",
                "camera_movement": "Camera movement"
            }
        }
        
        try:
            with open(self.locales_dir / "en.json", 'w', encoding='utf-8') as f:
                json.dump(default_translations, f, indent=2, ensure_ascii=False)
            print("Arquivo de idioma padrão criado: en.json")
        except Exception as e:
            print(f"Erro ao criar arquivo de idioma padrão: {e}")
    
    def get(self, key, default=None):
        """Obtém uma tradução usando notação de ponto: 'menu.save'"""
        keys = key.split('.')
        value = self.translations
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default if default is not None else key
    
    def get_language_name(self, lang_code):
        """Retorna o nome do idioma no próprio idioma"""
        try:
            lang_file = self.locales_dir / f"{lang_code}.json"
            with open(lang_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Tenta obter do campo "languages" primeiro, senão usa código
                return data.get("languages", {}).get(lang_code, lang_code)
        except Exception as e:
            print(f"Erro ao obter nome do idioma {lang_code}: {e}")
            return lang_code

    def get_all_language_names(self):
        """Retorna dicionário com códigos e nomes de todos os idiomas disponíveis"""
        languages = {}
        for lang_code in self.get_available_languages():
            languages[lang_code] = self.get_language_name(lang_code)
        return languages

    def get_available_languages(self):
        """Retorna lista de idiomas disponíveis"""
        languages = []
        
        print(f"=== DEBUG I18n ===")
        print(f"Procurando arquivos em: {self.locales_dir}")
        print(f"Diretório existe: {self.locales_dir.exists()}")
        
        if self.locales_dir.exists():
            print(f"Conteúdo do diretório:")
            for item in self.locales_dir.iterdir():
                print(f"  - {item.name} (arquivo: {item.is_file()})")
            
            for file in self.locales_dir.glob("*.json"):
                print(f"  Encontrado arquivo JSON: {file.name}")
                languages.append(file.stem)
        else:
            print(f"ERRO: Diretório não encontrado!")
            # Tenta caminho alternativo para executável
            import os
            if getattr(sys, 'frozen', False):
                # Para executável PyInstaller
                base_path = sys._MEIPASS
                alt_path = Path(base_path) / "assets" / "locales"
                print(f"Tentando caminho alternativo: {alt_path}")
                if alt_path.exists():
                    for file in alt_path.glob("*.json"):
                        print(f"  Encontrado no caminho alternativo: {file.name}")
                        languages.append(file.stem)
        
        print(f"Idiomas detectados: {languages}")
        print(f"==================")
        
        return sorted(languages)

# Instância global
i18n = I18n()