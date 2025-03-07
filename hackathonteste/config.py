"""
Configurações globais do jogo
"""

# Configurações da tela
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TITLE = "Batalha pela Queijada"
FPS = 60

# Configurações do jogo
TOTAL_LEVELS = 5
LIVES_PER_LEVEL = 3
ROUND_TIME = 360 * 60  # 1 minuto por round em frames

# Configurações de física
GRAVITY = 0.8
MAX_FALL_SPEED = 12
GROUND_FRICTION = 0.85
AIR_RESISTANCE = 0.95

# Configurações de combate
BASE_KNOCKBACK = 2
KNOCKBACK_GROWTH = 0.2

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)

# Caminhos de arquivos
BACKGROUNDS_PATH = "./imagens_background/"
CHARACTERS_PATH = "./imagens_characters/"
HUD_PATH = "./imagens_characters/SirLobo_Pack_HUD_2021_ONLY_PNG/HUD/Modulated/8/"
SOUNDS_PATH = "./sounds/" 