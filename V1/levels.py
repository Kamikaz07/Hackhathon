from typing import List, Dict
import math

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WALL_THICKNESS = 40
JUMP_HEIGHT = 140  # Altura aproximada que um jogador pode pular

class Level:
    def __init__(self, name: str, platforms: List[Dict], spawn_points: List[Dict]):
        self.name = name
        self.platforms = platforms
        self.spawn_points = spawn_points

def create_boundaries():
    """Cria as barreiras ao redor da área de jogo"""
    return [
        # Barreira esquerda
        {
            'x': -WALL_THICKNESS/2,
            'y': SCREEN_HEIGHT/2,
            'width': WALL_THICKNESS,
            'height': SCREEN_HEIGHT + WALL_THICKNESS,
            'movement_type': 'static'
        },
        # Barreira direita
        {
            'x': SCREEN_WIDTH + WALL_THICKNESS/2,
            'y': SCREEN_HEIGHT/2,
            'width': WALL_THICKNESS,
            'height': SCREEN_HEIGHT + WALL_THICKNESS,
            'movement_type': 'static'
        },
        # Barreira inferior
        {
            'x': SCREEN_WIDTH/2,
            'y': SCREEN_HEIGHT + WALL_THICKNESS/2,
            'width': SCREEN_WIDTH + WALL_THICKNESS*2,
            'height': WALL_THICKNESS,
            'movement_type': 'static'
        },
        # Barreira superior (nova)
        {
            'x': SCREEN_WIDTH/2,
            'y': -WALL_THICKNESS/2,
            'width': SCREEN_WIDTH + WALL_THICKNESS*2,
            'height': WALL_THICKNESS,
            'movement_type': 'static'
        }
    ]

def create_pastelaria():
    """Nível da Pastelaria"""
    boundaries = create_boundaries()
    ground_height = 40
    
    platforms = [
        # Balcão principal (chão)
        {
            'x': SCREEN_WIDTH/2,
            'y': SCREEN_HEIGHT - ground_height/2,
            'width': SCREEN_WIDTH - 100,
            'height': ground_height,
            'movement_type': 'static'
        },
        # Prateleiras laterais - garantir que sejam acessíveis do chão (JUMP_HEIGHT)
        {
            'x': 150,
            'y': SCREEN_HEIGHT - JUMP_HEIGHT,
            'width': 250,
            'height': 35,
            'movement_type': 'static'
        },
        {
            'x': SCREEN_WIDTH - 150,
            'y': SCREEN_HEIGHT - JUMP_HEIGHT,
            'width': 250,
            'height': 35,
            'movement_type': 'static'
        },
        # Bandeja de doces (plataforma móvel) - garantir que seja acessível das prateleiras laterais
        {
            'x': SCREEN_WIDTH/2,
            'y': SCREEN_HEIGHT - JUMP_HEIGHT - JUMP_HEIGHT,
            'width': 250,
            'height': 35,
            'movement_type': 'horizontal',
            'amplitude': 150,
            'frequency': 0.5,
            'phase': 0
        }
    ]
    
    return Level(
        name="Pastelaria",
        platforms=boundaries + platforms,
        spawn_points=[
            {'x': 200, 'y': SCREEN_HEIGHT - ground_height - 50},
            {'x': SCREEN_WIDTH - 200, 'y': SCREEN_HEIGHT - ground_height - 50}
        ]
    )

def create_estacao():
    """Nível da Estação"""
    boundaries = create_boundaries()
    ground_height = 40
    
    platforms = [
        # Plataformas da estação
        {
            'x': 200,
            'y': SCREEN_HEIGHT - ground_height/2,
            'width': 300,
            'height': ground_height,
            'movement_type': 'static'
        },
        {
            'x': SCREEN_WIDTH - 200,
            'y': SCREEN_HEIGHT - ground_height/2,
            'width': 300,
            'height': ground_height,
            'movement_type': 'static'
        },
        # Banco de espera - acessível do chão
        {
            'x': SCREEN_WIDTH/2,
            'y': SCREEN_HEIGHT - JUMP_HEIGHT,
            'width': 250,
            'height': 35,
            'movement_type': 'static'
        },
        # Trem em movimento (plataforma móvel) - acessível do banco
        {
            'x': SCREEN_WIDTH/2,
            'y': SCREEN_HEIGHT - JUMP_HEIGHT - JUMP_HEIGHT,
            'width': 250,
            'height': 35,
            'movement_type': 'horizontal',
            'amplitude': 250,
            'frequency': 0.3,
            'phase': 0
        }
    ]
    
    return Level(
        name="Estação",
        platforms=boundaries + platforms,
        spawn_points=[
            {'x': 200, 'y': SCREEN_HEIGHT - ground_height - 50},
            {'x': SCREEN_WIDTH - 200, 'y': SCREEN_HEIGHT - ground_height - 50}
        ]
    )

def create_floresta():
    """Nível da Floresta"""
    boundaries = create_boundaries()
    ground_height = 40
    
    platforms = [
        # Solo da floresta
        {
            'x': SCREEN_WIDTH/2,
            'y': SCREEN_HEIGHT - ground_height/2,
            'width': SCREEN_WIDTH - 150,
            'height': ground_height,
            'movement_type': 'static'
        },
        # Troncos caídos - acessíveis do chão
        {
            'x': 150,
            'y': SCREEN_HEIGHT - JUMP_HEIGHT,
            'width': 200,
            'height': 35,
            'movement_type': 'static'
        },
        {
            'x': SCREEN_WIDTH - 150,
            'y': SCREEN_HEIGHT - JUMP_HEIGHT,
            'width': 200,
            'height': 35,
            'movement_type': 'static'
        },
        # Galhos balançando - acessível dos troncos
        {
            'x': SCREEN_WIDTH/2,
            'y': SCREEN_HEIGHT - JUMP_HEIGHT - JUMP_HEIGHT/2,
            'width': 250,
            'height': 35,
            'movement_type': 'vertical',
            'amplitude': 30,
            'frequency': 0.7,
            'phase': 0
        },
        # Plataformas de árvores - acessíveis dos galhos
        {
            'x': 180,
            'y': SCREEN_HEIGHT - JUMP_HEIGHT - JUMP_HEIGHT - 20,
            'width': 150,
            'height': 35,
            'movement_type': 'static'
        },
        {
            'x': SCREEN_WIDTH - 180,
            'y': SCREEN_HEIGHT - JUMP_HEIGHT - JUMP_HEIGHT - 20,
            'width': 150,
            'height': 35,
            'movement_type': 'static'
        }
    ]
    
    return Level(
        name="Floresta",
        platforms=boundaries + platforms,
        spawn_points=[
            {'x': 200, 'y': SCREEN_HEIGHT - ground_height - 50},
            {'x': SCREEN_WIDTH - 200, 'y': SCREEN_HEIGHT - ground_height - 50}
        ]
    )

def create_montanha():
    """Nível da Montanha"""
    boundaries = create_boundaries()
    ground_height = 40
    
    platforms = [
        # Base da montanha
        {
            'x': SCREEN_WIDTH/2,
            'y': SCREEN_HEIGHT - ground_height/2,
            'width': SCREEN_WIDTH - 100,
            'height': ground_height,
            'movement_type': 'static'
        },
        # Plataformas rochosas - acessíveis do chão
        {
            'x': 180,
            'y': SCREEN_HEIGHT - JUMP_HEIGHT,
            'width': 200,
            'height': 35,
            'movement_type': 'static'
        },
        {
            'x': SCREEN_WIDTH - 180,
            'y': SCREEN_HEIGHT - JUMP_HEIGHT,
            'width': 200,
            'height': 35,
            'movement_type': 'static'
        },
        # Plataformas intermediárias - acessíveis das plataformas rochosas
        {
            'x': 300,
            'y': SCREEN_HEIGHT - JUMP_HEIGHT - JUMP_HEIGHT/2,
            'width': 180,
            'height': 35,
            'movement_type': 'static'
        },
        {
            'x': SCREEN_WIDTH - 300,
            'y': SCREEN_HEIGHT - JUMP_HEIGHT - JUMP_HEIGHT/2,
            'width': 180,
            'height': 35,
            'movement_type': 'static'
        },
        # Ponte suspensa (plataforma móvel) - acessível das plataformas intermediárias
        {
            'x': SCREEN_WIDTH/2,
            'y': SCREEN_HEIGHT - JUMP_HEIGHT - JUMP_HEIGHT - 30,
            'width': 220,
            'height': 35,
            'movement_type': 'vertical',
            'amplitude': 25,
            'frequency': 1.0,
            'phase': 0
        }
    ]
    
    return Level(
        name="Montanha",
        platforms=boundaries + platforms,
        spawn_points=[
            {'x': 200, 'y': SCREEN_HEIGHT - ground_height - 50},
            {'x': SCREEN_WIDTH - 200, 'y': SCREEN_HEIGHT - ground_height - 50}
        ]
    )

def create_palacio():
    """Nível do Palácio - Batalha Final"""
    boundaries = create_boundaries()
    ground_height = 40
    
    platforms = [
        # Piso do salão real
        {
            'x': SCREEN_WIDTH/2,
            'y': SCREEN_HEIGHT - ground_height/2,
            'width': SCREEN_WIDTH - 80,
            'height': ground_height,
            'movement_type': 'static'
        },
        # Escadarias laterais - acessíveis do chão
        {
            'x': 180,
            'y': SCREEN_HEIGHT - JUMP_HEIGHT,
            'width': 250,
            'height': 35,
            'movement_type': 'static'
        },
        {
            'x': SCREEN_WIDTH - 180,
            'y': SCREEN_HEIGHT - JUMP_HEIGHT,
            'width': 250,
            'height': 35,
            'movement_type': 'static'
        },
        # Plataformas de candelabros - acessíveis das escadarias
        {
            'x': 250,
            'y': SCREEN_HEIGHT - JUMP_HEIGHT - JUMP_HEIGHT/2,
            'width': 180,
            'height': 35,
            'movement_type': 'horizontal',
            'amplitude': 80,
            'frequency': 0.6,
            'phase': 0
        },
        {
            'x': SCREEN_WIDTH - 250,
            'y': SCREEN_HEIGHT - JUMP_HEIGHT - JUMP_HEIGHT/2,
            'width': 180,
            'height': 35,
            'movement_type': 'horizontal',
            'amplitude': 80,
            'frequency': 0.6,
            'phase': 3.14 # fase oposta à do outro candelabro
        },
        # Trono real (plataforma central) - acessível dos candelabros
        {
            'x': SCREEN_WIDTH/2,
            'y': SCREEN_HEIGHT - JUMP_HEIGHT - JUMP_HEIGHT - 40,
            'width': 300,
            'height': 45,
            'movement_type': 'static'
        }
    ]
    
    return Level(
        name="Palácio Real",
        platforms=boundaries + platforms,
        spawn_points=[
            {'x': 200, 'y': SCREEN_HEIGHT - ground_height - 50},
            {'x': SCREEN_WIDTH - 200, 'y': SCREEN_HEIGHT - ground_height - 50}
        ]
    )

# Dicionário com todos os níveis disponíveis
LEVELS = {
    "pastelaria": create_pastelaria,
    "estacao": create_estacao,
    "floresta": create_floresta,
    "montanha": create_montanha,
    "palacio": create_palacio
}

def get_level(level_name: str) -> Level:
    """Retorna um nível específico pelo nome"""
    if level_name not in LEVELS:
        return create_pastelaria()  # Nível padrão se o solicitado não existir
    return LEVELS[level_name]() 