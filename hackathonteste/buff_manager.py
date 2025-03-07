import random
import pygame
from buff import Buff  # Add this import at the top

class BuffManager:
    def __init__(self, screen_width, screen_height):
        self.buffs = []
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.spawn_timer = 0
        self.spawn_delay = 180  # Reduced from 300 to spawn more frequently

    def spawn_buff(self):
        """Spawn a new random buff"""
        buff_types = ["heal", "power", "mana"]
        buff_type = random.choice(buff_types)
        
        # Random position, keeping buffs away from edges
        x = random.randint(50, self.screen_width - 50)
        y = random.randint(50, self.screen_height - 50)
        
        # Different durations for different buffs
        if buff_type == "power":
            duration = 300  # 5 seconds at 60 FPS
        else:
            duration = 1  # Instant effect for heal and mana
            
        self.buffs.append(Buff(x, y, buff_type, duration))
    
    def update(self, characters):
        """Update all buffs and check for collisions"""
        # Spawn new buffs periodically
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_delay:
            self.spawn_buff()
            self.spawn_timer = 0

        # Update existing buffs
        for buff in self.buffs[:]:  # Copy list to safely remove items
            if not buff.active:
                self.buffs.remove(buff)
                continue

            buff.update()
            
            # Check collisions with characters
            for character in characters:
                if buff.collides_with(character):
                    buff.apply_effect(character)
                    if buff.buff_type == "power":
                        character.has_power_buff = True
                        character.power_buff_timer = buff.duration

    def draw(self, screen):
        """Draw all active buffs"""
        for buff in self.buffs:
            buff.draw(screen)