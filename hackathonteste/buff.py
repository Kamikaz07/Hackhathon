import pygame
import random

class Buff:
    def __init__(self, x, y, buff_type, duration):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.buff_type = buff_type
        self.duration = duration
        self.active = True
        
        # Load buff images
        try:
            image_path = f"./imagens_background/{buff_type}_buff.png"
            self.sprite = pygame.image.load(image_path).convert_alpha()
            self.sprite = pygame.transform.scale(self.sprite, (self.width, self.height))
        except:
            # Fallback to colored rectangle if image fails to load
            self.sprite = pygame.Surface((self.width, self.height))
            self.sprite.fill(self.get_color())
    
    def get_color(self):
        """Fallback colors for buffs"""
        if self.buff_type == "heal":
            return (0, 255, 0)  # Green
        elif self.buff_type == "power":
            return (255, 0, 0)  # Red
        elif self.buff_type == "mana":
            return (0, 0, 255)  # Blue
        return (255, 255, 255)  # White default

    def apply_effect(self, character):
        """Apply buff effect to character"""
        if not self.active:
            return

        if self.buff_type == "heal":
            healing = 20
            character.health = min(character.max_health, character.health + healing)
            character.active_buffs.append("heal")
            character.buff_durations["heal"] = 3  # Show healing effect for 3 seconds
        elif self.buff_type == "power":
            character.attack_multiplier = 1.5
            character.active_buffs.append("power")
            character.buff_durations["power"] = self.duration // 60  # Convert frames to seconds
        elif self.buff_type == "mana":
            character.mana = min(character.max_mana, character.mana + 30)
            character.active_buffs.append("mana")
            character.buff_durations["mana"] = 3  # Show mana effect for 3 seconds
        
        self.active = False

    def collides_with(self, character):
        """Check if buff collides with a character"""
        buff_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        char_rect = pygame.Rect(character.x, character.y, character.width, character.height)
        return buff_rect.colliderect(char_rect)
    
    def draw(self, screen):
        """Draw the buff"""
        if self.active:
            screen.blit(self.sprite, (self.x, self.y))

    def update(self):
        """Update buff state"""
        if self.duration > 0:
            self.duration -= 1
            if self.duration <= 0:
                self.active = False
    
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