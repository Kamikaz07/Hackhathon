import pygame
from entities.character import Character

class Fighter(Character):
    def __init__(self, x, y, name, is_player2=False):
        super().__init__(x, y, name, is_player2)
        # Fighter specific stats
        self.max_health = 120  # More health than other classes
        self.attack_damage = 15  # High melee damage
        self.defense = 8  # High defense
        self.speed = 4  # Slower movement
        
        # Fighter specific mana costs
        self.max_mana = 80  # Less mana than other classes
        self.mana = self.max_mana
        self.mana_regen = 0.3  # Slower mana regeneration
        self.attack_mana_cost = 10
        self.special_mana_cost = 40
        
        # Fighter specific cooldowns
        self.attack_duration = 15  # Faster basic attacks
        self.special_cooldown = 180  # 3 seconds
        self.special_duration = 40
        
        # Special attack properties
        self.special_damage = 25
        self.special_range = 100
        self.is_charging = False
        self.charge_timer = 0
        self.charge_duration = 20
    
    def load_sprites(self):
        try:
            self.sprites = {
                "idle": [pygame.image.load(f"./imagens_characters/PNG/Knight/idle_{i}.png").convert_alpha() for i in range(1, 5)],
                "run": [pygame.image.load(f"./imagens_characters/PNG/Knight/run_{i}.png").convert_alpha() for i in range(1, 7)],
                "attack": [pygame.image.load(f"./imagens_characters/PNG/Knight/attack_{i}.png").convert_alpha() for i in range(1, 5)],
                "special": [pygame.image.load(f"./imagens_characters/PNG/Knight/special_{i}.png").convert_alpha() for i in range(1, 5)]
            }
            # Scale sprites if needed
            for state in self.sprites:
                self.sprites[state] = [pygame.transform.scale(img, (80, 80)) for img in self.sprites[state]]
        except:
            # Use parent's default sprite if loading fails
            super().load_sprites()
    
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
        if self.special_cooldown == 0 and self.mana >= self.special_mana_cost and not self.is_charging:
            self.is_attacking = True
            self.is_charging = True
            self.charge_timer = self.charge_duration
            self.special_cooldown = self.special_duration
            self.mana -= self.special_mana_cost
            return True
        return False
    
    def update_local(self, controls, opponent, projectiles, platforms):
        # Update charge attack
        if self.is_charging:
            self.charge_timer -= 1
            if self.charge_timer <= 0:
                self.is_charging = False
                # Charge attack that hits in a wider area
                attack_rect = pygame.Rect(
                    self.rect.right if self.facing_right else self.rect.left - self.special_range,
                    self.rect.centery - 40,
                    self.special_range,
                    80
                )
                
                if attack_rect.colliderect(opponent.rect) and not opponent.is_defending:
                    damage = max(0, self.special_damage - opponent.defense)
                    opponent.take_damage(damage)
        
        # Call parent update
        super().update_local(controls, opponent, projectiles, platforms)
    
    def update_animation(self):
        if not self.sprites:
            return
        
        if self.is_attacking or self.is_charging:
            state = "special" if self.is_charging else "attack"
            self.animation_frame = (self.animation_frame + self.animation_speed) % len(self.sprites[state])
            
            # Reset attacking state after animation completes
            if self.is_attacking and not self.is_charging and self.animation_frame >= len(self.sprites["attack"]) - 1:
                self.is_attacking = False
        else:
            # Normal movement animation
            if abs(self.velocity_x) > 0:
                state = "run"
            else:
                state = "idle"
            self.animation_frame = (self.animation_frame + self.animation_speed) % len(self.sprites[state])
    
    def get_current_sprite(self):
        if not self.sprites:
            return None
            
        if self.is_charging:
            state = "special"
        elif self.is_attacking:
            state = "attack"
        elif abs(self.velocity_x) > 0:
            state = "run"
        else:
            state = "idle"
            
        frame = int(self.animation_frame)
        return self.sprites[state][frame % len(self.sprites[state])] 