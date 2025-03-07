"""
Gerenciador de níveis do jogo
"""
import pygame
import random
import config
from assets.asset_manager import asset_manager
from core.platform import Platform

class Level:
    """
    Classe para um nível do jogo
    """
    def __init__(self, background_path, platform_layout, spawn_points):
        """
        Inicializa um nível
        
        Args:
            background_path: Caminho da imagem de fundo
            platform_layout: Lista de tuplas (x, y, platform_type) para plataformas
            spawn_points: Lista de tuplas (x, y) para pontos de spawn
        """
        # Carrega o fundo
        try:
            self.background = asset_manager.load_image(background_path)
        except:
            print(f"Could not load background: {background_path}")
            # Cria um fundo de fallback com gradiente
            self.background = self.create_fallback_background()
        
        # Inicializa plataformas e pontos de spawn
        self.platforms = []
        self.spawn_points = spawn_points
        self.create_platforms(platform_layout)
    
    def create_fallback_background(self):
        """
        Cria um fundo de fallback com gradiente
        
        Returns:
            Surface com fundo de fallback
        """
        surface = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        
        # Cria gradiente de céu
        for y in range(config.SCREEN_HEIGHT):
            ratio = y / config.SCREEN_HEIGHT
            r = int(100 * (1 - ratio))
            g = int(150 * (1 - ratio))
            b = int(255 * (1 - ratio))
            pygame.draw.line(surface, (r, g, b), (0, y), (config.SCREEN_WIDTH, y))
        
        # Adiciona alguns elementos decorativos
        for _ in range(20):
            x = random.randint(0, config.SCREEN_WIDTH)
            y = random.randint(0, 400)
            size = random.randint(2, 4)
            # Desenha estrelas/nuvens
            pygame.draw.circle(surface, (255, 255, 255), (x, y), size)
        
        return surface
    
    def create_platforms(self, platform_layout):
        """
        Cria plataformas baseado no layout
        
        Args:
            platform_layout: Lista de tuplas (x, y, platform_type)
        """
        for plat in platform_layout:
            x, y, platform_type = plat
            self.platforms.append(Platform(x, y, platform_type))
    
    def draw(self, screen):
        """
        Desenha o nível (fundo e plataformas)
        
        Args:
            screen: Superfície onde desenhar
        """
        # Desenha fundo
        screen.blit(pygame.transform.scale(self.background, (screen.get_width(), screen.get_height())), (0, 0))
        
        # Desenha plataformas
        for platform in self.platforms:
            platform.draw(screen)

class LevelManager:
    """
    Gerenciador de níveis do jogo
    """
    def __init__(self):
        """
        Inicializa o gerenciador de níveis
        """
        self.current_level = 0
        self.total_levels = config.TOTAL_LEVELS
        self.player1_wins = 0
        self.player2_wins = 0
        self.levels = []
        self.initialize_levels()
    
    def initialize_levels(self):
        """
        Inicializa todos os níveis do jogo
        """
        screen_width = config.SCREEN_WIDTH
        center_x = screen_width // 2
        
        # Nível 1 - Arena Básica
        level1_platforms = [
            (center_x - 100, 470, Platform.MEDIUM),  # Plataforma central
            (center_x - 300, 340, Platform.SMALL),  # Plataforma esquerda
            (center_x + 200, 340, Platform.SMALL),  # Plataforma direita
            (center_x - 400, 600, Platform.GROUND)  # Chão
        ]
        spawn_points1 = [(center_x - 250, 200), (center_x + 250, 200)]
        self.levels.append(Level(f"{config.BACKGROUNDS_PATH}background1.png", level1_platforms, spawn_points1))
        
        # Nível 2 - Ilhas Flutuantes
        level2_platforms = [
            (center_x - 50, 250, Platform.SMALL),  # Plataforma flutuante central
            (center_x - 270, 350, Platform.SMALL),  # Plataforma esquerda
            (center_x + 180, 350, Platform.SMALL),  # Plataforma direita
            (center_x - 150, 470, Platform.MEDIUM),  # Plataforma central inferior
            (center_x - 400, 600, Platform.GROUND)  # Chão
        ]
        spawn_points2 = [(center_x - 250, 250), (center_x + 250, 250)]
        self.levels.append(Level(f"{config.BACKGROUNDS_PATH}background2.png", level2_platforms, spawn_points2))
        
        # Nível 3 - Desafio Vertical
        level3_platforms = [
            (center_x - 50, 150, Platform.SMALL),  # Plataforma superior
            (center_x - 300, 250, Platform.SMALL),  # Plataforma alta esquerda
            (center_x + 200, 250, Platform.SMALL),  # Plataforma alta direita
            (center_x - 50, 350, Platform.SMALL),  # Plataforma do meio
            (center_x - 200, 470, Platform.MEDIUM),  # Plataforma inferior
            (center_x - 400, 600, Platform.GROUND)  # Chão
        ]
        spawn_points3 = [(center_x - 200, 350), (center_x + 200, 350)]
        self.levels.append(Level(f"{config.BACKGROUNDS_PATH}background3.png", level3_platforms, spawn_points3))
        
        # Nível 4 - Arena Assimétrica
        level4_platforms = [
            (center_x - 200, 200, Platform.SMALL),  # Superior esquerda
            (center_x + 100, 300, Platform.SMALL),  # Superior direita
            (center_x - 300, 460, Platform.SMALL),  # Inferior esquerda
            (center_x, 420, Platform.SMALL),  # Inferior direita
            (center_x - 400, 600, Platform.GROUND)  # Chão
        ]
        spawn_points4 = [(center_x - 250, 300), (center_x + 250, 300)]
        self.levels.append(Level(f"{config.BACKGROUNDS_PATH}background4.jpg", level4_platforms, spawn_points4))
        
        # Nível 5 - Arena Final
        level5_platforms = [
            (center_x - 50, 200, Platform.SMALL),  # Centro superior
            (center_x - 250, 300, Platform.SMALL),  # Meio esquerda
            (center_x + 150, 300, Platform.SMALL),  # Meio direita
            (center_x - 150, 400, Platform.MEDIUM),  # Centro inferior
            (center_x - 350, 450, Platform.SMALL),  # Inferior esquerda
            (center_x + 250, 450, Platform.SMALL),  # Inferior direita
            (center_x - 400, 600, Platform.GROUND)  # Chão
        ]
        spawn_points5 = [(center_x - 250, 350), (center_x + 250, 350)]
        self.levels.append(Level(f"{config.BACKGROUNDS_PATH}background5.jpg", level5_platforms, spawn_points5))
    
    def get_current_level(self):
        """
        Retorna o nível atual
        
        Returns:
            Objeto Level do nível atual
        """
        # Garante que o índice não ultrapasse o número de níveis disponíveis
        safe_index = min(self.current_level, len(self.levels) - 1)
        return self.levels[safe_index]
    
    def get_spawn_points(self):
        """
        Retorna os pontos de spawn do nível atual
        
        Returns:
            Lista de pontos de spawn
        """
        return self.get_current_level().spawn_points
    
    def get_platforms(self):
        """
        Retorna as plataformas do nível atual
        
        Returns:
            Lista de plataformas
        """
        return self.get_current_level().platforms
    
    def next_level(self, winner):
        """
        Avança para o próximo nível e atualiza pontuações
        
        Args:
            winner: ID do jogador vencedor (1 ou 2)
            
        Returns:
            True se o jogo acabou, False caso contrário
        """
        # Atualiza pontuação
        if winner == 1:
            self.player1_wins += 1
        elif winner == 2:
            self.player2_wins += 1
        
        # Avança para o próximo nível
        self.current_level += 1
        
        # Verifica se o jogo acabou
        return self.current_level >= self.total_levels
    
    def get_winner(self):
        """
        Retorna o ID do jogador com mais vitórias
        
        Returns:
            1 para jogador 1, 2 para jogador 2, 0 para empate
        """
        if self.player1_wins > self.player2_wins:
            return 1
        elif self.player2_wins > self.player1_wins:
            return 2
        else:
            return 0  # Empate
    
    def get_score_text(self):
        """
        Retorna texto com placar atual
        
        Returns:
            String com placar
        """
        return f"Placar: Jogador 1 ({self.player1_wins}) x ({self.player2_wins}) Jogador 2"
    
    def get_level_text(self):
        """
        Retorna texto com nível atual
        
        Returns:
            String com nível atual
        """
        return f"Nível {self.current_level + 1}/{self.total_levels}" 