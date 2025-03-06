import pygame
import random

class Buff:
    def __init__(self, x, y, buff_type, duration):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.buff_type = buff_type
        self.duration = duration  # Duration in frames
        self.color = self.get_color_for_type()
    
    def get_color_for_type(self):
        """Get color based on buff type"""
        if self.buff_type == "health":
            return (0, 255, 0)  # Green for health
        elif self.buff_type == "attack":
            return (255, 0, 0)  # Red for attack
        elif self.buff_type == "defense":
            return (0, 0, 255)  # Blue for defense
        elif self.buff_type == "speed":
            return (255, 255, 0)  # Yellow for speed
        else:
            return (255, 255, 255)  # White for unknown
    
    def draw(self, screen):
        """Draw the buff on the screen"""
        # Draw the buff as a colored circle
        pygame.draw.circle(screen, self.color, (self.x + self.width // 2, self.y + self.height // 2), self.width // 2)
        
        # Draw a white border
        pygame.draw.circle(screen, (255, 255, 255), (self.x + self.width // 2, self.y + self.height // 2), self.width // 2, 2)
        
        # Add a letter in the middle to identify the buff type
        font = pygame.font.Font(None, 20)
        
        if self.buff_type == "health":
            letter = "H"
        elif self.buff_type == "attack":
            letter = "A"
        elif self.buff_type == "defense":
            letter = "D"
        elif self.buff_type == "speed":
            letter = "S"
        else:
            letter = "?"
        
        text = font.render(letter, True, (0, 0, 0))
        text_rect = text.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(text, text_rect)
    
    def collides_with(self, character):
        """Check if the buff collides with a character"""
        return (self.x < character.x + character.width and
                self.x + self.width > character.x and
                self.y < character.y + character.height and
                self.y + self.height > character.y)
    
    def to_dict(self):
        """Convert buff to dictionary for network transmission"""
        return {
            "buff_type": self.buff_type,
            "duration": self.duration
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a buff from dictionary data"""
        return cls(
            0, 0,  # Position doesn't matter for active buffs
            data["buff_type"],
            data["duration"]
        ) 