from typing import List, Dict
import math

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WALL_THICKNESS = 20

class Level:
    def __init__(self, name: str, platforms: List[Dict], spawn_points: List[Dict]):
        self.name = name
        self.platforms = platforms
        self.spawn_points = spawn_points

def create_boundaries():
    """Cria as barreiras invisíveis ao redor da área de jogo"""
    return [
        # Barreira esquerda
        {
            'x': 0,
            'y': SCREEN_HEIGHT/2,
            'width': 10,
            'height': SCREEN_HEIGHT,
            'movement_type': 'static'
        },
        # Barreira direita
        {
            'x': SCREEN_WIDTH,
            'y': SCREEN_HEIGHT/2,
            'width': 10,
            'height': SCREEN_HEIGHT,
            'movement_type': 'static'
        }
    ]

def create_level_1():
    boundaries = create_boundaries()
    platforms = [
        # Chão principal
        {
            'x': SCREEN_WIDTH / 2,
            'y': SCREEN_HEIGHT - 20,
            'width': SCREEN_WIDTH - 200,
            'height': 20,
            'movement_type': 'static'
        },
        # Plataformas laterais
        {
            'x': 200,
            'y': SCREEN_HEIGHT - 150,
            'width': 200,
            'height': 20,
            'movement_type': 'static'
        },
        {
            'x': SCREEN_WIDTH - 200,
            'y': SCREEN_HEIGHT - 150,
            'width': 200,
            'height': 20,
            'movement_type': 'static'
        },
        # Plataforma central móvel
        {
            'x': SCREEN_WIDTH/2,
            'y': SCREEN_HEIGHT - 300,
            'width': 200,
            'height': 20,
            'movement_type': 'horizontal',
            'amplitude': 100,
            'frequency': 0.5,
            'phase': 0
        }
    ]
    
    return Level(
        name="Classic Arena",
        platforms=boundaries + platforms,
        spawn_points=[
            {'x': 200, 'y': SCREEN_HEIGHT - 50},
            {'x': SCREEN_WIDTH - 200, 'y': SCREEN_HEIGHT - 50}
        ]
    )

def create_level_2():
    boundaries = create_boundaries()
    platforms = [
        # Chão principal
        {
            'x': SCREEN_WIDTH / 2,
            'y': SCREEN_HEIGHT - 20,
            'width': SCREEN_WIDTH - 200,
            'height': 20,
            'movement_type': 'static'
        },
        # Plataformas estáticas
        {
            'x': 200,
            'y': SCREEN_HEIGHT - 200,
            'width': 200,
            'height': 20,
            'movement_type': 'static'
        },
        {
            'x': SCREEN_WIDTH - 200,
            'y': SCREEN_HEIGHT - 200,
            'width': 200,
            'height': 20,
            'movement_type': 'static'
        },
        # Plataforma móvel central
        {
            'x': SCREEN_WIDTH/2,
            'y': SCREEN_HEIGHT - 350,
            'width': 200,
            'height': 20,
            'movement_type': 'horizontal',
            'amplitude': 150,
            'frequency': 0.8,
            'phase': 0
        }
    ]
    
    return Level(
        name="Tower Battle",
        platforms=boundaries + platforms,
        spawn_points=[
            {'x': 200, 'y': SCREEN_HEIGHT - 50},
            {'x': SCREEN_WIDTH - 200, 'y': SCREEN_HEIGHT - 50}
        ]
    )

def create_level_3():
    boundaries = create_boundaries()
    platforms = [
        # Plataformas base
        {
            'x': 200,
            'y': SCREEN_HEIGHT - 20,
            'width': 200,
            'height': 20,
            'movement_type': 'static'
        },
        {
            'x': SCREEN_WIDTH - 200,
            'y': SCREEN_HEIGHT - 20,
            'width': 200,
            'height': 20,
            'movement_type': 'static'
        },
        # Plataforma móvel central
        {
            'x': SCREEN_WIDTH/2,
            'y': SCREEN_HEIGHT - 150,
            'width': 250,
            'height': 20,
            'movement_type': 'horizontal',
            'amplitude': 100,
            'frequency': 0.5,
            'phase': 0
        },
        # Plataformas superiores
        {
            'x': 200,
            'y': SCREEN_HEIGHT - 300,
            'width': 150,
            'height': 20,
            'movement_type': 'static'
        },
        {
            'x': SCREEN_WIDTH - 200,
            'y': SCREEN_HEIGHT - 300,
            'width': 150,
            'height': 20,
            'movement_type': 'static'
        }
    ]
    
    return Level(
        name="Battle Bridge",
        platforms=boundaries + platforms,
        spawn_points=[
            {'x': 200, 'y': SCREEN_HEIGHT - 50},
            {'x': SCREEN_WIDTH - 200, 'y': SCREEN_HEIGHT - 50}
        ]
    )

# Dicionário com todos os níveis disponíveis
LEVELS = {
    "level1": create_level_1,
    "level2": create_level_2,
    "level3": create_level_3
}

def get_level(level_name: str) -> Level:
    """Retorna um nível específico pelo nome"""
    if level_name not in LEVELS:
        return create_level_1()  # Nível padrão se o solicitado não existir
    return LEVELS[level_name]() 