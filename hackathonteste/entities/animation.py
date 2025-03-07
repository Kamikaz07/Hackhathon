"""
Sistema de animação para personagens e efeitos
"""
import os
import pygame
from assets.asset_manager import asset_manager

class Animation:
    """
    Classe para gerenciar animações de sprites
    """
    def __init__(self, folder_path, speed=0.1):
        """
        Inicializa uma animação a partir de um diretório de frames
        
        Args:
            folder_path: Caminho do diretório com os frames
            speed: Velocidade da animação (frames por segundo)
        """
        self.frames = asset_manager.load_animation_frames(folder_path)
        self.current_frame = 0
        self.animation_speed = speed
        self.animation_timer = 0
        self.is_playing = True
        self.loop = True
        self.finished = False
    
    def update(self, dt):
        """
        Atualiza a animação
        
        Args:
            dt: Delta time (tempo desde o último frame)
            
        Returns:
            Frame atual da animação ou None se não houver frames
        """
        if not self.frames or not self.is_playing:
            return self.get_current_frame()
        
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame += 1
            
            # Verifica se chegou ao fim da animação
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.is_playing = False
                    self.finished = True
        
        return self.get_current_frame()
    
    def get_current_frame(self):
        """
        Retorna o frame atual da animação
        
        Returns:
            Frame atual ou None se não houver frames
        """
        if not self.frames:
            return None
        
        return self.frames[self.current_frame]
    
    def reset(self):
        """
        Reinicia a animação
        """
        self.current_frame = 0
        self.animation_timer = 0
        self.is_playing = True
        self.finished = False
    
    def play(self):
        """
        Inicia ou continua a animação
        """
        self.is_playing = True
    
    def pause(self):
        """
        Pausa a animação
        """
        self.is_playing = False
    
    def set_speed(self, speed):
        """
        Define a velocidade da animação
        
        Args:
            speed: Nova velocidade da animação
        """
        self.animation_speed = speed
    
    def set_loop(self, loop):
        """
        Define se a animação deve repetir
        
        Args:
            loop: True para repetir, False para parar no último frame
        """
        self.loop = loop
    
    def is_finished(self):
        """
        Verifica se a animação terminou (apenas para animações sem loop)
        
        Returns:
            True se a animação terminou, False caso contrário
        """
        return self.finished 