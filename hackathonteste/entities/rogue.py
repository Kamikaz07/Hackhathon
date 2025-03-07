import pygame
from entities.character import Character

class Rogue(Character):
    def __init__(self, x, y, name, is_player2=False):
        super().__init__(x, y, name, is_player2)
        # Rogue specific stats
        self.max_health = 90  # Medium health
        self.attack_damage = 12  # Medium melee damage
        self.defense = 5  # Medium defense
        self.speed = 7  # Fastest movement
        
        # Rogue specific mana costs
        self.max_mana = 100  # Standard mana pool
        self.mana = self.max_mana
        self.mana_regen = 0.7  # Medium mana regeneration
        self.attack_mana_cost = 15
        self.special_mana_cost = 45
        
        # Rogue specific cooldowns
        self.attack_duration = 12  # Very fast basic attacks
        self.special_cooldown = 300  # 5 seconds
        self.special_duration = 40
        
        # Special attack properties
        self.special_damage = 35
        self.dash_speed = 15
        self.dash_duration = 10
        self.is_dashing = False
        self.dash_timer = 0
        self.dash_direction = 1
        self.has_hit = False  # Track if dash attack has already hit
        
        # Load rogue-specific sprites
        self.load_sprites()
    
    def load_sprites(self):
        try:
            self.sprites = {
                "idle": [pygame.image.load(f"./imagens_characters/PNG/Rogue/idle_{i}.png").convert_alpha() for i in range(1, 5)],
                "run": [pygame.image.load(f"./imagens_characters/PNG/Rogue/run_{i}.png").convert_alpha() for i in range(1, 7)],
                "attack": [pygame.image.load(f"./imagens_characters/PNG/Rogue/attack_{i}.png").convert_alpha() for i in range(1, 5)],
                "special": [pygame.image.load(f"./imagens_characters/PNG/Rogue/special_{i}.png").convert_alpha() for i in range(1, 5)]
            }
            # Scale sprites if needed
            for state in self.sprites:
                self.sprites[state] = [pygame.transform.scale(img, (80, 80)) for img in self.sprites[state]]
        except:
            # Use parent's default sprite if loading fails
            super().load_sprites()
    
    def handle_movement(self, controls, platforms):
        if self.is_dashing:
            # During dash, move in dash direction
            self.velocity_x = self.dash_speed * self.dash_direction
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.is_dashing = False
                self.has_hit = False
        else:
            # Normal movement
            super().handle_movement(controls, platforms)
    
    def attack(self, opponent):
        if self.attack_cooldown == 0 and self.mana >= self.attack_mana_cost:
            self.is_attacking = True
            self.attack_cooldown = self.attack_duration
            self.mana -= self.attack_mana_cost
            
            if self.attack_rect.colliderect(opponent.rect) and not opponent.is_defending:
                damage = max(0, self.attack_damage - opponent.defense)
                opponent.take_damage(damage)
                return True
        return False
    
    def special_attack(self, opponent, projectiles):
        if self.special_cooldown == 0 and self.mana >= self.special_mana_cost and not self.is_dashing:
            self.is_attacking = True
            self.is_dashing = True
            self.dash_timer = self.dash_duration
            self.dash_direction = 1 if self.facing_right else -1
            self.special_cooldown = self.special_duration
            self.mana -= self.special_mana_cost
            self.has_hit = False
            return True
        return False
    
    def update_local(self, controls, opponent, projectiles, platforms):
        # Check for dash hit
        if self.is_dashing and not self.has_hit:
            if self.rect.colliderect(opponent.rect) and not opponent.is_defending:
                damage = max(0, self.special_damage - opponent.defense)
                opponent.take_damage(damage)
                
                # Knockback effect
                knockback = 10 * self.dash_direction
                opponent.velocity_x = knockback
                opponent.velocity_y = -5
                
                self.has_hit = True
        
        # Call parent update
        super().update_local(controls, opponent, projectiles, platforms)
    
    def update_animation(self):
        if not self.sprites:
            return
        
        if self.is_attacking or self.is_dashing:
            state = "special" if self.is_dashing else "attack"
            self.animation_frame = (self.animation_frame + self.animation_speed) % len(self.sprites[state])
            
            # Reset attacking state after animation completes
            if self.is_attacking and not self.is_dashing and self.animation_frame >= len(self.sprites["attack"]) - 1:
                self.is_attacking = False
        else:
            # Normal movement animation
            if abs(self.velocity_x) > 0:
                state = "run"
            else:
                state = "idle"
            self.animation_frame = (self.animation_frame + self.animation_speed) % len(self.sprites[state])
        
        # Speed up animation during dash
        if self.is_dashing:
            self.animation_frame = (self.animation_frame + self.animation_speed * 2) % len(self.sprites["special"])
    
    def get_current_sprite(self):
        if not self.sprites:
            return None
            
        if self.is_dashing:
            state = "special"
        elif self.is_attacking:
            state = "attack"
        elif abs(self.velocity_x) > 0:
            state = "run"
        else:
            state = "idle"
            
        frame = int(self.animation_frame)
        return self.sprites[state][frame % len(self.sprites[state])] 