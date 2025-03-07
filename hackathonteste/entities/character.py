import pygame
import math

class Character:
    def __init__(self, x, y, name, is_player2=False):
        # Position and movement
        self.x = x
        self.y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = 5
        self.jump_force = -15
        self.is_jumping = False
        self.facing_right = not is_player2
        
        # Combat stats
        self.name = name
        self.max_health = 100
        self.health = 0
        self.attack_damage = 10
        self.defense = 5
        self.lives = 3
        self.is_player2 = is_player2
        
        # Mana system
        self.max_mana = 100
        self.mana = self.max_mana
        self.mana_regen = 0.5  # Mana regeneration per frame
        
        # Combat states
        self.is_attacking = False
        self.is_defending = False
        self.attack_cooldown = 0
        self.defense_cooldown = 0
        self.special_cooldown = 0
        self.attack_duration = 20
        self.defense_duration = 30
        self.special_duration = 40
        self.hit_cooldown = 0
        
        # Animation
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.sprites = {}  # Dictionary to store sprites
        self.load_sprites()
        
        # Collision
        self.rect = pygame.Rect(x, y, 50, 80)
        self.attack_rect = pygame.Rect(x, y, 60, 80)
    
    def load_sprites(self):
        """Base method for loading sprites. Should be overridden by child classes."""
        pass
    
    def update_local(self, controls, opponent, projectiles, platforms):
        # Update position
        self.handle_movement(controls, platforms)
        
        # Update combat
        self.handle_combat(controls, opponent, projectiles)
        
        # Update mana
        self.handle_mana()
        
        # Update animation
        self.update_animation()
        
        # Update rectangles
        self.update_rectangles()
    
    def handle_mana(self):
        # Regenerate mana
        if self.mana < self.max_mana:
            self.mana = min(self.max_mana, self.mana + self.mana_regen)
    
    def handle_movement(self, controls, platforms):
        # Horizontal movement
        if controls["left"]:
            self.velocity_x = -self.speed
            self.facing_right = False
        elif controls["right"]:
            self.velocity_x = self.speed
            self.facing_right = True
        else:
            self.velocity_x = 0
        
        # Apply gravity
        self.velocity_y += 0.8
        
        # Jump
        if controls["up"] and not self.is_jumping:
            self.velocity_y = self.jump_force
            self.is_jumping = True
        
        # Update position
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Platform collision
        self.handle_platform_collision(platforms)
    
    def handle_platform_collision(self, platforms):
        self.rect.x = self.x
        self.rect.y = self.y
        
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # Vertical collision
                if self.velocity_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.y = self.rect.y
                    self.velocity_y = 0
                    self.is_jumping = False
                elif self.velocity_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.y = self.rect.y
                    self.velocity_y = 0
                
                # Horizontal collision
                if self.velocity_x > 0:
                    self.rect.right = platform.rect.left
                    self.x = self.rect.x
                elif self.velocity_x < 0:
                    self.rect.left = platform.rect.right
                    self.x = self.rect.x
    
    def handle_combat(self, controls, opponent, projectiles):
        # Update cooldowns
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.defense_cooldown > 0:
            self.defense_cooldown -= 1
        if self.special_cooldown > 0:
            self.special_cooldown -= 1
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1
        
        # Handle attacks
        if controls["attack"] and self.attack_cooldown == 0:
            self.attack(opponent)
        
        # Handle defense
        if controls["defend"] and self.defense_cooldown == 0:
            self.defend()
        
        # Handle special
        if controls["special"] and self.special_cooldown == 0:
            self.special_attack(opponent, projectiles)
    
    def attack(self, opponent):
        # Basic attack implementation
        self.is_attacking = True
        self.attack_cooldown = self.attack_duration
        
        if self.attack_rect.colliderect(opponent.rect) and not opponent.is_defending:
            damage = max(0, self.attack_damage - opponent.defense)
            opponent.take_damage(damage)
    
    def defend(self):
        # Basic defense implementation
        self.is_defending = True
        self.defense_cooldown = self.defense_duration
    
    def special_attack(self, opponent, projectiles):
        # This method should be overridden by child classes
        pass
    
    def take_damage(self, damage):
        if self.hit_cooldown == 0:
            self.health += damage
            self.hit_cooldown = 30
    
    def update_animation(self):
        # Update animation frame
        if self.sprites:
            if self.is_attacking:
                state = "attack"
            elif abs(self.velocity_x) > 0:
                state = "run"
            else:
                state = "idle"
            
            self.animation_frame = (self.animation_frame + self.animation_speed) % len(self.sprites[state])
            
            # Reset attacking state after animation completes
            if self.is_attacking and self.animation_frame >= len(self.sprites["attack"]) - 1:
                self.is_attacking = False
    
    def update_rectangles(self):
        # Update main rectangle
        self.rect.x = self.x
        self.rect.y = self.y
        
        # Update attack rectangle based on facing direction
        if self.facing_right:
            self.attack_rect.left = self.rect.right
        else:
            self.attack_rect.right = self.rect.left
        self.attack_rect.centery = self.rect.centery
    
    def draw(self, screen):
        # Draw character sprite
        current_sprite = self.get_current_sprite()
        if current_sprite:
            if not self.facing_right:
                current_sprite = pygame.transform.flip(current_sprite, True, False)
            screen.blit(current_sprite, self.rect)
        else:
            # Fallback: draw rectangle if no sprite is available
            color = (255, 0, 0) if self.is_player2 else (0, 0, 255)
            pygame.draw.rect(screen, color, self.rect)
    
    def get_current_sprite(self):
        if not self.sprites:
            return None
            
        if self.is_attacking:
            state = "attack"
        elif abs(self.velocity_x) > 0:
            state = "run"
        else:
            state = "idle"
            
        frame = int(self.animation_frame)
        return self.sprites[state][frame % len(self.sprites[state])] 