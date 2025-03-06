from typing import List, Dict
import math

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WALL_THICKNESS = 40
JUMP_HEIGHT = 140

class Level:
    def __init__(self, name: str, platforms: List[Dict], spawn_points: List[Dict]):
        self.name = name
        self.platforms = platforms
        self.spawn_points = spawn_points

def create_boundaries():
    return [
        {'x': -WALL_THICKNESS/2, 'y': SCREEN_HEIGHT/2, 'width': WALL_THICKNESS, 'height': SCREEN_HEIGHT + WALL_THICKNESS, 'movement_type': 'static'},
        {'x': SCREEN_WIDTH + WALL_THICKNESS/2, 'y': SCREEN_HEIGHT/2, 'width': WALL_THICKNESS, 'height': SCREEN_HEIGHT + WALL_THICKNESS, 'movement_type': 'static'},
        {'x': SCREEN_WIDTH/2, 'y': SCREEN_HEIGHT + WALL_THICKNESS/2, 'width': SCREEN_WIDTH + WALL_THICKNESS*2, 'height': WALL_THICKNESS, 'movement_type': 'static'},
        {'x': SCREEN_WIDTH/2, 'y': -WALL_THICKNESS/2, 'width': SCREEN_WIDTH + WALL_THICKNESS*2, 'height': WALL_THICKNESS, 'movement_type': 'static'}
    ]

def create_pastelaria():
    boundaries = create_boundaries()
    ground_height = 40
    
    platforms = [
        {'x': SCREEN_WIDTH/2, 'y': SCREEN_HEIGHT - ground_height/2, 'width': SCREEN_WIDTH - 100, 'height': ground_height * 2, 'movement_type': 'static'},
        {'x': 150, 'y': SCREEN_HEIGHT - JUMP_HEIGHT, 'width': 250, 'height': 70, 'movement_type': 'static'},
        {'x': SCREEN_WIDTH - 150, 'y': SCREEN_HEIGHT - JUMP_HEIGHT, 'width': 250, 'height': 70, 'movement_type': 'static'},
        {'x': SCREEN_WIDTH/2, 'y': SCREEN_HEIGHT - JUMP_HEIGHT - JUMP_HEIGHT, 'width': 250, 'height': 70, 'movement_type': 'horizontal', 'amplitude': 150, 'frequency': 0.5, 'phase': 0}
    ]
    
    return Level(
        name="Pastelaria",
        platforms=boundaries + platforms,
        spawn_points=[{'x': 200, 'y': SCREEN_HEIGHT - ground_height - 50}, {'x': SCREEN_WIDTH - 200, 'y': SCREEN_HEIGHT - ground_height - 50}]
    )

def create_estacao():
    boundaries = create_boundaries()
    ground_height = 40
    
    platforms = [
        {'x': 200, 'y': SCREEN_HEIGHT - ground_height/2, 'width': 300, 'height': ground_height * 2, 'movement_type': 'static'},
        {'x': SCREEN_WIDTH - 200, 'y': SCREEN_HEIGHT - ground_height/2, 'width': 300, 'height': ground_height * 2, 'movement_type': 'static'},
        {'x': SCREEN_WIDTH/2, 'y': SCREEN_HEIGHT - JUMP_HEIGHT, 'width': 250, 'height': 70, 'movement_type': 'static'},
        {'x': SCREEN_WIDTH/2, 'y': SCREEN_HEIGHT - JUMP_HEIGHT - JUMP_HEIGHT, 'width': 250, 'height': 70, 'movement_type': 'horizontal', 'amplitude': 250, 'frequency': 0.3, 'phase': 0}
    ]
    
    return Level(
        name="Estação",
        platforms=boundaries + platforms,
        spawn_points=[{'x': 200, 'y': SCREEN_HEIGHT - ground_height - 50}, {'x': SCREEN_WIDTH - 200, 'y': SCREEN_HEIGHT - ground_height - 50}]
    )

def create_floresta():
    boundaries = create_boundaries()
    ground_height = 40
    
    platforms = [
        {'x': SCREEN_WIDTH/2, 'y': SCREEN_HEIGHT - ground_height/2, 'width': SCREEN_WIDTH - 150, 'height': ground_height * 2, 'movement_type': 'static'},
        {'x': 150, 'y': SCREEN_HEIGHT - JUMP_HEIGHT, 'width': 200, 'height': 70, 'movement_type': 'static'},
        {'x': SCREEN_WIDTH - 150, 'y': SCREEN_HEIGHT - JUMP_HEIGHT, 'width': 200, 'height': 70, 'movement_type': 'static'},
        {'x': SCREEN_WIDTH/2, 'y': SCREEN_HEIGHT - JUMP_HEIGHT - JUMP_HEIGHT/2, 'width': 250, 'height': 70, 'movement_type': 'vertical', 'amplitude': 30, 'frequency': 0.7, 'phase': 0},
        {'x': 180, 'y': SCREEN_HEIGHT - JUMP_HEIGHT - JUMP_HEIGHT - 20, 'width': 150, 'height': 70, 'movement_type': 'static'},
        {'x': SCREEN_WIDTH - 180, 'y': SCREEN_HEIGHT - JUMP_HEIGHT - JUMP_HEIGHT - 20, 'width': 150, 'height': 70, 'movement_type': 'static'}
    ]
    
    return Level(
        name="Floresta",
        platforms=boundaries + platforms,
        spawn_points=[{'x': 200, 'y': SCREEN_HEIGHT - ground_height - 50}, {'x': SCREEN_WIDTH - 200, 'y': SCREEN_HEIGHT - ground_height - 50}]
    )

def create_montanha():
    boundaries = create_boundaries()
    ground_height = 40
    
    platforms = [
        {'x': SCREEN_WIDTH/2, 'y': SCREEN_HEIGHT - ground_height/2, 'width': SCREEN_WIDTH - 100, 'height': ground_height * 2, 'movement_type': 'static'},
        {'x': 180, 'y': SCREEN_HEIGHT - JUMP_HEIGHT, 'width': 200, 'height': 70, 'movement_type': 'static'},
        {'x': SCREEN_WIDTH - 180, 'y': SCREEN_HEIGHT - JUMP_HEIGHT, 'width': 200, 'height': 70, 'movement_type': 'static'},
        {'x': 300, 'y': SCREEN_HEIGHT - JUMP_HEIGHT - JUMP_HEIGHT/2, 'width': 180, 'height': 70, 'movement_type': 'static'},
        {'x': SCREEN_WIDTH - 300, 'y': SCREEN_HEIGHT - JUMP_HEIGHT - JUMP_HEIGHT/2, 'width': 180, 'height': 70, 'movement_type': 'static'},
        {'x': SCREEN_WIDTH/2, 'y': SCREEN_HEIGHT - JUMP_HEIGHT - JUMP_HEIGHT - 30, 'width': 220, 'height': 70, 'movement_type': 'vertical', 'amplitude': 25, 'frequency': 1.0, 'phase': 0}
    ]
    
    return Level(
        name="Montanha",
        platforms=boundaries + platforms,
        spawn_points=[{'x': 200, 'y': SCREEN_HEIGHT - ground_height - 50}, {'x': SCREEN_WIDTH - 200, 'y': SCREEN_HEIGHT - ground_height - 50}]
    )

def create_palacio():
    boundaries = create_boundaries()
    ground_height = 40
    
    platforms = [
        {'x': SCREEN_WIDTH/2, 'y': SCREEN_HEIGHT - ground_height/2, 'width': SCREEN_WIDTH - 80, 'height': ground_height * 2, 'movement_type': 'static'},
        {'x': 180, 'y': SCREEN_HEIGHT - JUMP_HEIGHT, 'width': 250, 'height': 70, 'movement_type': 'static'},
        {'x': SCREEN_WIDTH - 180, 'y': SCREEN_HEIGHT - JUMP_HEIGHT, 'width': 250, 'height': 70, 'movement_type': 'static'},
        {'x': 250, 'y': SCREEN_HEIGHT - JUMP_HEIGHT - JUMP_HEIGHT/2, 'width': 180, 'height': 70, 'movement_type': 'horizontal', 'amplitude': 80, 'frequency': 0.6, 'phase': 0},
        {'x': SCREEN_WIDTH - 250, 'y': SCREEN_HEIGHT - JUMP_HEIGHT - JUMP_HEIGHT/2, 'width': 180, 'height': 70, 'movement_type': 'horizontal', 'amplitude': 80, 'frequency': 0.6, 'phase': 3.14},
        {'x': SCREEN_WIDTH/2, 'y': SCREEN_HEIGHT - JUMP_HEIGHT - JUMP_HEIGHT - 40, 'width': 300, 'height': 90, 'movement_type': 'static'}
    ]
    
    return Level(
        name="Palácio Real",
        platforms=boundaries + platforms,
        spawn_points=[{'x': 200, 'y': SCREEN_HEIGHT - ground_height - 50}, {'x': SCREEN_WIDTH - 200, 'y': SCREEN_HEIGHT - ground_height - 50}]
    )

LEVELS = {
    "pastelaria": create_pastelaria,
    "estacao": create_estacao,
    "floresta": create_floresta,
    "montanha": create_montanha,
    "palacio": create_palacio
}

def get_level(level_name: str) -> Level:
    if level_name not in LEVELS:
        return create_pastelaria()
    return LEVELS[level_name]()