"""
Gerenciador de recursos para carregar imagens e sons
"""
import os
import pygame
import config

class AssetManager:
    """
    Classe responsável por carregar e gerenciar recursos do jogo
    como imagens, sons, etc.
    """
    def __init__(self):
        self.images = {}
        self.sounds = {}
        self.animations = {}
        self.fonts = {}
    
    def load_image(self, path, convert_alpha=True, scale=None):
        """
        Carrega uma imagem e a armazena em cache
        
        Args:
            path: Caminho da imagem
            convert_alpha: Se deve converter para formato com alpha
            scale: Tupla (width, height) para redimensionar a imagem
            
        Returns:
            Surface da imagem carregada
        """
        # Verifica se a imagem já está em cache
        if path in self.images:
            image = self.images[path]
            if scale:
                return pygame.transform.scale(image, scale)
            return image
        
        try:
            if convert_alpha:
                image = pygame.image.load(path).convert_alpha()
            else:
                image = pygame.image.load(path).convert()
                
            # Armazena a imagem original em cache
            self.images[path] = image
            
            # Retorna a imagem redimensionada se necessário
            if scale:
                return pygame.transform.scale(image, scale)
            return image
        except Exception as e:
            print(f"Erro ao carregar imagem {path}: {e}")
            # Cria uma superfície de fallback
            fallback = pygame.Surface((64, 64), pygame.SRCALPHA)
            pygame.draw.rect(fallback, (255, 0, 255), fallback.get_rect(), 2)
            pygame.draw.line(fallback, (255, 0, 255), (0, 0), (64, 64), 2)
            pygame.draw.line(fallback, (255, 0, 255), (64, 0), (0, 64), 2)
            
            # Armazena a imagem de fallback em cache
            self.images[path] = fallback
            
            if scale:
                return pygame.transform.scale(fallback, scale)
            return fallback
    
    def load_sound(self, path):
        """
        Carrega um som e o armazena em cache
        
        Args:
            path: Caminho do som
            
        Returns:
            Objeto Sound carregado ou None se falhar
        """
        # Verifica se o som já está em cache
        if path in self.sounds:
            return self.sounds[path]
        
        try:
            sound = pygame.mixer.Sound(path)
            self.sounds[path] = sound
            return sound
        except Exception as e:
            print(f"Erro ao carregar som {path}: {e}")
            return None
    
    def load_animation_frames(self, folder_path):
        """
        Carrega todos os frames de uma animação de um diretório
        
        Args:
            folder_path: Caminho do diretório com os frames
            
        Returns:
            Lista de frames da animação
        """
        # Verifica se a animação já está em cache
        if folder_path in self.animations:
            return self.animations[folder_path]
        
        frames = []
        try:
            if os.path.exists(folder_path):
                for file in sorted(os.listdir(folder_path)):
                    if file.endswith('.png'):
                        image_path = os.path.join(folder_path, file)
                        image = self.load_image(image_path)
                        frames.append(image)
                
                # Armazena os frames em cache
                self.animations[folder_path] = frames
        except Exception as e:
            print(f"Erro ao carregar animação de {folder_path}: {e}")
        
        return frames
    
    def load_font(self, name, size):
        """
        Carrega uma fonte e a armazena em cache
        
        Args:
            name: Nome da fonte ou None para fonte padrão
            size: Tamanho da fonte
            
        Returns:
            Objeto Font carregado
        """
        key = f"{name}_{size}"
        
        # Verifica se a fonte já está em cache
        if key in self.fonts:
            return self.fonts[key]
        
        try:
            font = pygame.font.Font(name, size)
            self.fonts[key] = font
            return font
        except Exception as e:
            print(f"Erro ao carregar fonte {name} tamanho {size}: {e}")
            # Usa a fonte padrão como fallback
            font = pygame.font.Font(None, size)
            self.fonts[key] = font
            return font
    
    def create_gradient_surface(self, width, height, start_color, end_color, vertical=True):
        """
        Cria uma superfície com gradiente
        
        Args:
            width: Largura da superfície
            height: Altura da superfície
            start_color: Cor inicial do gradiente
            end_color: Cor final do gradiente
            vertical: Se o gradiente é vertical (True) ou horizontal (False)
            
        Returns:
            Surface com gradiente
        """
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        if vertical:
            for y in range(height):
                # Calcula a cor interpolada
                ratio = y / height
                r = start_color[0] * (1 - ratio) + end_color[0] * ratio
                g = start_color[1] * (1 - ratio) + end_color[1] * ratio
                b = start_color[2] * (1 - ratio) + end_color[2] * ratio
                a = 255
                if len(start_color) > 3 and len(end_color) > 3:
                    a = start_color[3] * (1 - ratio) + end_color[3] * ratio
                
                color = (int(r), int(g), int(b), int(a))
                pygame.draw.line(surface, color, (0, y), (width, y))
        else:
            for x in range(width):
                # Calcula a cor interpolada
                ratio = x / width
                r = start_color[0] * (1 - ratio) + end_color[0] * ratio
                g = start_color[1] * (1 - ratio) + end_color[1] * ratio
                b = start_color[2] * (1 - ratio) + end_color[2] * ratio
                a = 255
                if len(start_color) > 3 and len(end_color) > 3:
                    a = start_color[3] * (1 - ratio) + end_color[3] * ratio
                
                color = (int(r), int(g), int(b), int(a))
                pygame.draw.line(surface, color, (x, 0), (x, height))
        
        return surface

# Instância global do gerenciador de recursos
asset_manager = AssetManager() 