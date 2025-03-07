import pygame
from entities.character import Character

class Projectile:
    def __init__(self, x, y, direction, damage, speed=10):
        self.x = x
        self.y = y
        self.direction = direction
        self.damage = damage
        self.speed = speed
        self.speed_y = 0  # Vertical speed for special attack
        self.rect = pygame.Rect(x, y, 20, 20)
        self.lifetime = 60  # 1 second at 60 FPS
    
    def update(self):
        self.x += self.speed * self.direction
        self.y += self.speed_y
        self.rect.x = self.x
        self.rect.y = self.y
        self.lifetime -= 1
        return self.lifetime <= 0
    
    def draw(self, screen):
        pygame.draw.circle(screen, (0, 0, 255), (int(self.x + 10), int(self.y + 10)), 10)

class Mage(Character):
    def __init__(self, x, y, name, is_player2=False):
        super().__init__(x, y, name, is_player2)
        # Mage specific stats
        self.max_health = 80  # Less health than other classes
        self.attack_damage = 8  # Low melee damage
        self.defense = 4  # Low defense
        self.speed = 6  # Fast movement
        
        # Mage specific mana costs
        self.max_mana = 150  # More mana than other classes
        self.mana = self.max_mana
        self.mana_regen = 1.0  # Faster mana regeneration
        self.attack_mana_cost = 20
        self.special_mana_cost = 50
        
        # Mage specific cooldowns
        self.attack_duration = 25  # Slower basic attacks
        self.special_cooldown = 240  # 4 seconds
        self.special_duration = 40
        
        # Special attack properties
        self.special_damage = 30
        self.projectile_speed = 12
        self.casting_special = False
        self.cast_timer = 0
        self.cast_duration = 20
    
    def load_sprites(self):
        try:
            self.sprites = {
                "idle": [pygame.image.load(f"./imagens_characters/PNG/Mage/idle_{i}.png").convert_alpha() for i in range(1, 5)],
                "run": [pygame.image.load(f"./imagens_characters/PNG/Mage/run_{i}.png").convert_alpha() for i in range(1, 7)],
                "attack": [pygame.image.load(f"./imagens_characters/PNG/Mage/attack_{i}.png").convert_alpha() for i in range(1, 5)],
                "special": [pygame.image.load(f"./imagens_characters/PNG/Mage/special_{i}.png").convert_alpha() for i in range(1, 5)]
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
            
            # Create a magic projectile
            direction = 1 if self.facing_right else -1
            projectile = Projectile(
                self.rect.centerx,
                self.rect.centery,
                direction,
                self.attack_damage,
                self.projectile_speed
            )
            return projectile
        return None
    
    def special_attack(self, opponent, projectiles):
        if self.special_cooldown == 0 and self.mana >= self.special_mana_cost and not self.casting_special:
            self.is_attacking = True
            self.casting_special = True
            self.cast_timer = self.cast_duration
            self.special_cooldown = self.special_duration
            self.mana -= self.special_mana_cost
            return True
        return False
    
    def update_local(self, controls, opponent, projectiles, platforms):
        # Update casting state
        if self.casting_special:
            self.cast_timer -= 1
            if self.cast_timer <= 0:
                self.casting_special = False
                # Create multiple projectiles in a spread pattern
                directions = [-0.5, 0, 0.5]
                base_direction = 1 if self.facing_right else -1
                
                for spread in directions:
                    projectile = Projectile(
                        self.rect.centerx,
                        self.rect.centery,
                        base_direction,
                        self.special_damage // 3,  # Divide damage among projectiles
                        self.projectile_speed
                    )
                    projectile.speed_y = spread * self.projectile_speed
                    projectiles.append(projectile)
        
        # Call parent update
        super().update_local(controls, opponent, projectiles, platforms)
    
    def update_animation(self):
        if not self.sprites:
            return
        
        if self.is_attacking or self.casting_special:
            state = "special" if self.casting_special else "attack"
            self.animation_frame = (self.animation_frame + self.animation_speed) % len(self.sprites[state])
            
            # Reset attacking state after animation completes
            if self.is_attacking and not self.casting_special and self.animation_frame >= len(self.sprites["attack"]) - 1:
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
            
        if self.casting_special:
            state = "special"
        elif self.is_attacking:
            state = "attack"
        elif abs(self.velocity_x) > 0:
            state = "run"
        else:
            state = "idle"
            
        frame = int(self.animation_frame)
        return self.sprites[state][frame % len(self.sprites[state])] 