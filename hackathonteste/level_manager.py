import pygame
import random

class Platform:
    # Tamanhos predefinidos
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    GROUND = "ground"
    
    # Dimensões para cada tipo
    SIZES = {
        SMALL: (150, 40),
        MEDIUM: (300, 40),
        LARGE: (500, 40),
        GROUND: (800, 40)
    }
    
    def __init__(self, x, y, platform_type):
        """
        Inicializa uma plataforma com tamanho predefinido
        
        Args:
            x, y: Posição da plataforma
            platform_type: Tipo da plataforma (SMALL, MEDIUM, LARGE ou GROUND)
        """
        width, height = self.SIZES.get(platform_type, self.SIZES[self.MEDIUM])
        self.rect = pygame.Rect(x, y, width, height)
        self.platform_type = platform_type
        
        try:
            self.image = pygame.image.load("./imagens_background/plataformateste.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (width, height))
        except Exception as e:
            print(f"Could not load platform image: {e}")
            self.image = self.create_fallback_platform(width, height)
        
        self.top = self.rect.top
        self.bottom = self.rect.bottom
        self.left = self.rect.left
        self.right = self.rect.right
    
    def create_fallback_platform(self, width, height):
        """Create a fallback platform texture if image fails to load"""
        surface = pygame.Surface((width, height))
        
        # Create gradient effect
        for y in range(height):
            color = (
                min(255, 100 + y * 2),  # Lighter gray at bottom
                min(255, 100 + y * 2),
                min(255, 100 + y * 2)
            )
            pygame.draw.line(surface, color, (0, y), (width, y))
        
        # Add border
        pygame.draw.rect(surface, (50, 50, 50), surface.get_rect(), 2)
        
        return surface

class Level:
    def __init__(self, background_path, platform_layout, spawn_points):
        try:
            self.background = pygame.image.load(background_path).convert()
        except:
            print(f"Could not load background: {background_path}")
            # Create a fallback background with a gradient
            self.background = self.create_fallback_background()
        
        self.platforms = []
        self.spawn_points = spawn_points
        self.create_platforms(platform_layout)
    
    def create_fallback_background(self):
        """Create a fallback background with a gradient when image fails to load"""
        surface = pygame.Surface((1280, 820))  # Match screen dimensions
        
        # Create a gradient background
        for y in range(820):
            # Calculate gradient colors (sky blue to darker blue)
            color = (
                max(0, min(255, 135 - y//4)),  # R
                max(0, min(255, 206 - y//4)),  # G
                max(0, min(255, 235))          # B
            )
            pygame.draw.line(surface, color, (0, y), (1280, y))
        
        # Add some decorative elements
        for _ in range(20):
            x = random.randint(0, 1280)
            y = random.randint(0, 400)
            size = random.randint(2, 4)
            # Draw stars/clouds
            pygame.draw.circle(surface, (255, 255, 255), (x, y), size)
        
        return surface
    
    def create_platforms(self, platform_layout):
        """Create platforms based on the layout"""
        for plat in platform_layout:
            x, y, platform_type = plat
            self.platforms.append(Platform(x, y, platform_type))
    
    def draw(self, screen):
        """Draw the level background and platforms"""
        # Draw background
        screen.blit(pygame.transform.scale(self.background, (screen.get_width(), screen.get_height())), (0, 0))
        
        # Draw platforms
        for platform in self.platforms:
            screen.blit(platform.image, platform.rect)

class LevelManager:
    def __init__(self):
        self.current_level = 0
        self.total_levels = 5
        self.levels = []
        self.initialize_levels()
        
        # Round tracking
        self.current_round = 1
        self.rounds_per_level = 2
        self.total_rounds = self.total_levels * self.rounds_per_level
        
        # Score tracking
        self.player1_wins = 0
        self.player2_wins = 0
    
    def initialize_levels(self):
        """Initialize all level data"""
        screen_width = 1280  # Largura padrão da tela
        center_x = screen_width // 2  # Centro da tela
        
        # Level 1 - Basic Arena
        level1_platforms = [
            (center_x - 100, 400, Platform.MEDIUM),  # Central platform
            (center_x - 300, 300, Platform.SMALL),  # Left platform
            (center_x + 150, 300, Platform.SMALL),  # Right platform
            (center_x - 400, 600, Platform.GROUND)    # Ground
        ]
        spawn_points1 = [(center_x - 250, 200), (center_x + 250, 200)]
        self.levels.append(Level("./imagens_background/background1.png", level1_platforms, spawn_points1))
        
        # Level 2 - Floating Islands
        level2_platforms = [
            (center_x - 50, 250, Platform.SMALL),  # Central floating platform
            (center_x - 250, 350, Platform.SMALL),  # Left platform
            (center_x + 150, 350, Platform.SMALL),  # Right platform
            (center_x - 150, 450, Platform.MEDIUM),  # Lower central platform
            (center_x - 400, 600, Platform.GROUND)    # Ground
        ]
        spawn_points2 = [(center_x - 250, 250), (center_x + 250, 250)]
        self.levels.append(Level("./imagens_background/background2.png", level2_platforms, spawn_points2))
        
        # Level 3 - Vertical Challenge
        level3_platforms = [
            (center_x - 50, 150, Platform.SMALL),  # Top platform
            (center_x - 300, 250, Platform.SMALL),  # Left high platform
            (center_x + 200, 250, Platform.SMALL),  # Right high platform
            (center_x - 50, 350, Platform.SMALL),  # Middle platform
            (center_x - 200, 450, Platform.MEDIUM),  # Lower platform
            (center_x - 400, 600, Platform.GROUND)    # Ground
        ]
        spawn_points3 = [(center_x - 200, 350), (center_x + 200, 350)]
        self.levels.append(Level("./imagens_background/background3.png", level3_platforms, spawn_points3))
        
        # Level 4 - Asymmetric Arena
        level4_platforms = [
            (center_x - 200, 200, Platform.SMALL),  # Upper left
            (center_x + 100, 300, Platform.SMALL),  # Upper right
            (center_x - 300, 400, Platform.SMALL),  # Lower left
            (center_x, 450, Platform.SMALL),  # Lower right
            (center_x - 400, 600, Platform.GROUND)    # Ground
        ]
        spawn_points4 = [(center_x - 250, 300), (center_x + 250, 300)]
        self.levels.append(Level("./imagens_background/background4.png", level4_platforms, spawn_points4))
        
        # Level 5 - Final Arena
        level5_platforms = [
            (center_x - 50, 200, Platform.SMALL),  # Top center
            (center_x - 250, 300, Platform.SMALL),  # Mid left
            (center_x + 150, 300, Platform.SMALL),  # Mid right
            (center_x - 150, 400, Platform.MEDIUM),  # Lower center
            (center_x - 350, 450, Platform.SMALL),   # Bottom left
            (center_x + 250, 450, Platform.SMALL),  # Bottom right
            (center_x - 400, 600, Platform.GROUND)    # Ground
        ]
        spawn_points5 = [(center_x - 250, 350), (center_x + 250, 350)]
        self.levels.append(Level("./imagens_background/background5.png", level5_platforms, spawn_points5))
    
    def get_current_level(self):
        """Get the current level object"""
        return self.levels[self.current_level]
    
    def get_spawn_points(self):
        """Get spawn points for current level"""
        return self.get_current_level().spawn_points
    
    def get_platforms(self):
        """Get platforms for current level"""
        return self.get_current_level().platforms
    
    def next_round(self, winner):
        """Progress to next round and update scores"""
        if winner == 1:
            self.player1_wins += 1
        elif winner == 2:
            self.player2_wins += 1
        
        self.current_round += 1
        
        # Check if we should move to next level
        if self.current_round % self.rounds_per_level == 0:
            self.current_level = (self.current_level + 1) % self.total_levels
        
        return self.check_game_end()
    
    def check_game_end(self):
        """Check if the game has ended"""
        if self.current_round > self.total_rounds:
            return True
        return False
    
    def get_winner(self):
        """Get the overall winner"""
        if self.player1_wins > self.player2_wins:
            return 1
        elif self.player2_wins > self.player1_wins:
            return 2
        return 0  # Tie
    
    def get_score_text(self):
        """Get current score text"""
        return f"Player 1: {self.player1_wins} - Player 2: {self.player2_wins}"
    
    def get_round_text(self):
        """Get current round text"""
        return f"Round {self.current_round}/{self.total_rounds} - Level {self.current_level + 1}" 