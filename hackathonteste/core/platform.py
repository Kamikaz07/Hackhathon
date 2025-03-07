"""
Classe para plataformas do jogo
"""
import pygame
from assets.asset_manager import asset_manager

class Platform:
    """
    Classe para plataformas do jogo
    """
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
            x: Posição X da plataforma
            y: Posição Y da plataforma
            platform_type: Tipo da plataforma (SMALL, MEDIUM, LARGE ou GROUND)
        """
        width, height = self.SIZES.get(platform_type, self.SIZES[self.MEDIUM])
        self.rect = pygame.Rect(x, y, width, height)
        self.platform_type = platform_type
        
        # Carrega a imagem da plataforma
        try:
            self.image = asset_manager.load_image("./imagens_background/plataformateste.png", True, (width, height))
        except Exception as e:
            print(f"Could not load platform image: {e}")
            self.image = self.create_fallback_platform(width, height)
        
        # Propriedades para colisão
        self.top = self.rect.top
        self.bottom = self.rect.bottom
        self.left = self.rect.left
        self.right = self.rect.right
    
    def create_fallback_platform(self, width, height):
        """
        Cria uma textura de fallback para a plataforma caso a imagem não carregue
        
        Args:
            width: Largura da plataforma
            height: Altura da plataforma
            
        Returns:
            Surface com textura de fallback
        """
        surface = pygame.Surface((width, height))
        
        # Cria efeito de gradiente
        for y in range(height):
            color = (
                min(255, 100 + y * 2),  # Cinza mais claro no fundo
                min(255, 100 + y * 2),
                min(255, 100 + y * 2)
            )
            pygame.draw.line(surface, color, (0, y), (width, y))
        
        # Adiciona borda
        pygame.draw.rect(surface, (50, 50, 50), surface.get_rect(), 2)
        
        return surface
    
    def draw(self, screen):
        """
        Desenha a plataforma na tela
        
        Args:
            screen: Superfície onde desenhar
        """
        screen.blit(self.image, self.rect) 