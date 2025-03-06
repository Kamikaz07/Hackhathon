import pygame
import random

class Buff:
    def __init__(self, x, y, buff_type, duration):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.buff_type = buff_type
        self.duration = duration
        
        # Visual representation
        self.sprite = pygame.Surface((self.width, self.height))
        self.color = self.get_color()
        self.sprite.fill(self.color)
    
    def get_color(self):
        """Get color based on buff type"""
        if self.buff_type == "attack":
            return (255, 0, 0)  # Red
        elif self.buff_type == "defense":
            return (0, 0, 255)  # Blue
        elif self.buff_type == "speed":
            return (0, 255, 0)  # Green
        else:  # health
            return (255, 255, 0)  # Yellow
    
    def collides_with(self, character):
        """Check if buff collides with a character"""
        buff_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        char_rect = pygame.Rect(character.x, character.y, character.width, character.height)
        return buff_rect.colliderect(char_rect)
    
    def draw(self, screen):
        """Draw the buff"""
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
    
    def to_dict(self):
        """Convert buff to dictionary for network transmission"""
        return {
            "x": self.x,
            "y": self.y,
            "buff_type": self.buff_type,
            "duration": self.duration
        }
    
    @staticmethod
    def from_dict(data):
        """Create buff from dictionary"""
        return Buff(
            data["x"],
            data["y"],
            data["buff_type"],
            data["duration"]
        ) 