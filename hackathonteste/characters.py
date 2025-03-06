import pygame
import random
import math
import os

class Animation:
    def __init__(self, folder_path):
        self.frames = []
        self.current_frame = 0
        self.animation_speed = 0.1  # Faster animation speed
        self.animation_timer = 0
        
        # Load all frames from the folder
        if os.path.exists(folder_path):
            for file in sorted(os.listdir(folder_path)):
                if file.endswith('.png'):
                    image_path = os.path.join(folder_path, file)
                    image = pygame.image.load(image_path).convert_alpha()
                    self.frames.append(image)
    
    def update(self, dt):
        if not self.frames:
            return None
            
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
        
        return self.frames[self.current_frame]
    
    def reset(self):
        self.current_frame = 0
        self.animation_timer = 0

class Character:
    def __init__(self, x, y, name, is_player2=False):
        self.x = x
        self.y = y
        self.name = name
        self.is_player2 = is_player2
        self.width = 50
        self.height = 50
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.speed = 5
        self.health = 0  # Damage percentage starts at 0
        self.max_health = 300  # Maximum percentage reduced
        self.base_knockback = 2  # Reduced base knockback
        self.knockback_growth = 0.05  # Reduced knockback growth
        self.attack_power = 10
        self.defense = 5
        self.attack_range = 60
        
        # Physics
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 0.8
        self.jump_force = -15
        self.on_ground = False
        self.jumps_left = 2
        self.max_fall_speed = 12
        self.ground_friction = 0.85
        self.air_resistance = 0.95
        self.ground_snap_distance = 5  # Nova variável para snap ao chão
        self.last_ground_y = y  # Nova variável para rastrear última posição no chão
        
        # Combat
        self.special_cooldown = 0
        self.special_cooldown_max = 180  # 3 seconds
        self.attacking = False
        self.defending = False
        self.using_special = False
        self.attack_frame = 0
        self.attack_cooldown = 0
        self.attack_cooldown_max = 20  # Faster attacks
        self.direction = -1 if is_player2 else 1
        self.color = self.get_color()
        self.attack_hitbox = pygame.Rect(0, 0, 0, 0)
        
        # Dodge mechanics
        self.dodging = False
        self.dodge_cooldown = 0
        self.dodge_cooldown_max = 90  # 1.5 seconds
        self.dodge_duration = 15  # 0.25 seconds
        self.dodge_speed = 15
        self.dodge_direction = 0
        
        # Visual representation
        self.sprite = pygame.Surface((self.width, self.height))
        self.sprite.fill(self.color)
        
        # Animation states
        self.state = "idle"
        self.animations = {}
        self.load_animations()
        self.facing_right = not is_player2
        self.animation_timer = 0
    
    def get_color(self):
        """Get base color for the character"""
        return (200, 200, 200)  # Default gray color for base character
    
    def apply_knockback(self, direction, power):
        """Apply knockback based on percentage"""
        # Calculate knockback based on percentage
        # More gradual knockback increase
        knockback_multiplier = 1 + (self.health * self.knockback_growth)
        base_power = self.base_knockback + (power * 0.2)  # Reduced power multiplier
        
        # Cap maximum knockback
        max_knockback = 20
        knockback_x = direction * min(base_power * knockback_multiplier, max_knockback)
        knockback_y = -min(base_power * knockback_multiplier * 0.5, max_knockback * 0.5)
        
        self.velocity_x = knockback_x
        self.velocity_y = knockback_y

    def update_physics(self):
        """Update physics-based movement"""
        # Apply gravity
        self.velocity_y += self.gravity
        
        # Apply velocities
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Ground collision
        if self.y > 500:  # Ground level
            self.y = 500
            self.velocity_y = 0
            self.on_ground = True
            self.jumps_left = 2
        else:
            self.on_ground = False
        
        # Wall collision
        self.x = max(0, min(800 - self.width, self.x))
        
        # Air resistance
        self.velocity_x *= 0.9
        
        # Reset small velocities
        if abs(self.velocity_x) < 0.1:
            self.velocity_x = 0

    def update_local(self, controls, opponent, buffs, platforms):
        """Update character with local controls"""
        # Handle movement
        moving = False
        if controls["left"]:
            self.velocity_x = max(self.velocity_x - 1, -self.speed)  # Aceleração gradual
            self.direction = -1
            moving = True
        elif controls["right"]:
            self.velocity_x = min(self.velocity_x + 1, self.speed)  # Aceleração gradual
            self.direction = 1
            moving = True
        
        # Handle jumping
        if controls["up"] and self.jumps_left > 0:
            self.velocity_y = self.jump_force
            self.jumps_left -= 1
            self.on_ground = False
        
        # Aplicar atrito apropriado
        if self.on_ground:
            if not moving:
                self.velocity_x *= self.ground_friction  # Mais atrito no chão quando parado
            else:
                self.velocity_x *= 0.95  # Menos atrito quando movendo
        else:
            self.velocity_x *= self.air_resistance  # Menos atrito no ar
        
        # Movimento horizontal primeiro
        self.x += self.velocity_x
        self.rect.x = self.x
        
        # Movimento vertical e colisão com plataforma
        was_on_ground = self.on_ground
        self.on_ground = False
        
        # Se estava no chão no frame anterior, primeiro tenta manter no chão
        if was_on_ground:
            for platform in platforms:
                if (self.rect.bottom <= platform.top + self.ground_snap_distance and 
                    self.rect.bottom >= platform.top - self.ground_snap_distance and
                    self.rect.centerx >= platform.left and 
                    self.rect.centerx <= platform.right):
                    self.rect.bottom = platform.top
                    self.y = self.rect.y
                    self.velocity_y = 0
                    self.on_ground = True
                    self.last_ground_y = self.y
                    break
        
        # Se não está no chão, aplica gravidade e movimento vertical
        if not self.on_ground:
            # Aplica gravidade
            self.velocity_y += self.gravity
            self.velocity_y = min(self.velocity_y, self.max_fall_speed)
            
            # Move verticalmente
            self.y += self.velocity_y
            self.rect.y = self.y
            
            # Checa colisão com plataformas
            for platform in platforms:
                if self.rect.colliderect(platform):
                    if self.velocity_y > 0:  # Caindo
                        prev_bottom = self.rect.bottom - self.velocity_y
                        if prev_bottom <= platform.top + 2:  # Margem reduzida
                            self.rect.bottom = platform.top
                            self.y = self.rect.y
                            self.velocity_y = 0
                            self.on_ground = True
                            self.last_ground_y = self.y
                            self.jumps_left = 2
                            break
        
        # Atualiza posição final
        self.x = self.rect.x
        self.y = self.rect.y
        
        # Limpa velocidades muito pequenas para evitar deslizamento
        if abs(self.velocity_x) < 0.1:
            self.velocity_x = 0
        
        # Se estiver no chão, garante que a velocidade vertical é 0
        if self.on_ground:
            self.velocity_y = 0
            self.jumps_left = 2
        
        # Update attack state
        if controls["attack"] and not self.attacking and self.attack_cooldown <= 0:
            self.attacking = True
            self.attack_frame = 0
            # Apply knockback to opponent if in range
            if self.rect.colliderect(opponent.rect):
                damage = self.calculate_attack_damage()
                if damage is not None:
                    opponent.take_damage(damage)
                    # Calculate knockback based on opponent's damage percentage
                    knockback_power = self.base_knockback * (1 + opponent.health * 0.01)
                    knockback_x = self.direction * knockback_power
                    knockback_y = -knockback_power * 0.5
                    opponent.velocity_x = knockback_x
                    opponent.velocity_y = knockback_y
        
        if self.attacking:
            self.attack_frame += 1
            if self.attack_frame >= self.attack_cooldown_max:
                self.attacking = False
                self.attack_cooldown = self.attack_cooldown_max
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # Update special attack state
        if controls["special"] and not self.using_special and self.special_cooldown <= 0:
            self.using_special = True
            self.special_frame = 0
            self.special_cooldown = self.special_cooldown_max
            # Apply special attack effects
            if self.rect.colliderect(opponent.rect):
                damage = self.special_ability(opponent)
                if damage is not None:
                    opponent.take_damage(damage)
                    # Calculate knockback based on opponent's damage percentage
                    knockback_power = self.base_knockback * 2 * (1 + opponent.health * 0.01)
                    knockback_x = self.direction * knockback_power
                    knockback_y = -knockback_power * 0.5
                    opponent.velocity_x = knockback_x
                    opponent.velocity_y = knockback_y
        
        if self.using_special:
            self.special_frame += 1
            if self.special_frame >= self.special_cooldown_max:
                self.using_special = False
        
        if self.special_cooldown > 0:
            self.special_cooldown -= 1
        
        # Update defense state
        self.defending = controls["defend"]
    
    def draw(self, screen):
        """Draw the character with animations"""
        # Update animation state
        self.update_animation_state()
        
        # Get current animation frame
        current_animation = self.animations.get(self.state)
        if current_animation:
            frame = current_animation.update(1/60)  # Assuming 60 FPS
            if frame:
                # Flip the frame based on direction
                if self.direction == -1:  # Moving/facing left
                    frame = pygame.transform.flip(frame, True, False)
                
                # Scale the frame if needed
                scaled_frame = pygame.transform.scale(frame, (self.width, self.height))
                screen.blit(scaled_frame, (self.x, self.y))
        
        # Draw attack hitbox if attacking
        if self.attacking:
            pygame.draw.rect(screen, (255, 255, 0), self.attack_hitbox, 2)
        
        # Draw percentage instead of health bar
        font = pygame.font.Font(None, 36)
        percentage_text = f"{int(self.health)}%"
        percentage_color = (255, 
                          max(0, 255 - (self.health * 1.5)), 
                          max(0, 255 - (self.health * 1.5)))
        percentage_surface = font.render(percentage_text, True, percentage_color)
        screen.blit(percentage_surface, (self.x, self.y - 30))
        
        # Draw name
        name_font = pygame.font.Font(None, 24)
        name_surface = name_font.render(self.name, True, (255, 255, 255))
        screen.blit(name_surface, (self.x, self.y - 50))
    
    def take_damage(self, damage):
        """Take damage, increasing percentage"""
        if self.defending:
            damage *= 0.5  # Take half damage when defending
        
        self.health = min(self.max_health, self.health + damage)
    
    def calculate_attack_damage(self):
        """Calculate attack damage based on character stats"""
        base_damage = self.attack_power
        if self.defending:
            base_damage *= 0.5
        return base_damage
    
    def special_ability(self, opponent):
        """Special ability, overridden by subclasses"""
        return self.attack_power * 2  # Default special damage
    
    def load_animations(self):
        """Load character animations - to be overridden by subclasses"""
        pass
    
    def update_animation_state(self):
        """Update the current animation state based on character's actions"""
        new_state = "idle"
        
        if self.attacking:
            new_state = "attack"
        elif self.using_special:
            new_state = "attack_extra"
        elif abs(self.velocity_x) > 0.1:
            new_state = "walk"
        elif not self.on_ground:
            new_state = "jump"
        
        if self.state != new_state:
            self.state = new_state
            if self.state in self.animations:
                self.animations[self.state].reset()


class Fighter(Character):
    def __init__(self, x, y, name, is_player2=False):
        super().__init__(x, y, name, is_player2)
        self.health = 0  # Start at 0%
        self.attack_power = 5  # Base damage
        self.defense = 8
        self.attack_range = 70
        self.special_damage = 10
        self.speed = 4
        self.width = 64
        self.height = 64
        self.base_knockback = 3  # Slightly higher base knockback
    
    def get_color(self):
        """Fighter's unique color"""
        return (255, 0, 0)  # Red for Fighter
    
    def special_ability(self, opponent):
        """Fighter's special ability: Ground pound"""
        if opponent:
            # Create large attack hitbox below
            attack_width = 120
            attack_height = 80
            
            if not self.on_ground:
                # If in air, slam down
                self.velocity_y = 20
                hitbox = pygame.Rect(self.x - attack_width/2, self.y + self.height, attack_width, attack_height)
            else:
                # If on ground, uppercut
                self.velocity_y = self.jump_force * 1.5
                hitbox = pygame.Rect(self.x - attack_width/2, self.y - attack_height, attack_width, attack_height)
            
            if hitbox.colliderect(pygame.Rect(opponent.x, opponent.y, opponent.width, opponent.height)):
                damage = self.calculate_attack_damage() * 2
                # Strong vertical knockback
                opponent.velocity_y = -15 if self.on_ground else 15
                opponent.velocity_x = self.direction * 10
                opponent.take_damage(damage)
            
            self.using_special = False
    
    def load_animations(self):
        base_path = "./imagens_characters/PNG/Knight"
        self.animations = {
            "idle": Animation(os.path.join(base_path, "Idle")),
            "walk": Animation(os.path.join(base_path, "Walk")),
            "attack": Animation(os.path.join(base_path, "Walk_Attack")),
            "attack": Animation(os.path.join(base_path, "Attack")),
            "attack_extra": Animation(os.path.join(base_path, "Attack_Extra")),
            "jump": Animation(os.path.join(base_path, "Jump")),
            "hurt": Animation(os.path.join(base_path, "Hurt")),
            "run": Animation(os.path.join(base_path, "Run"))
        }


class Mage(Character):
    def __init__(self, x, y, name, is_player2=False):
        super().__init__(x, y, name, is_player2)
        self.health = 0  # Start at 0%
        self.attack_power = 4  # Base damage
        self.defense = 4
        self.attack_range = 150
        self.special_damage = 8
        self.speed = 5
        self.width = 64
        self.height = 64
        self.base_knockback = 2  # Medium base knockback
    
    def get_color(self):
        """Mage's unique color"""
        return (0, 0, 255)  # Blue for Mage
    
    def special_ability(self, opponent):
        """Mage's special ability: Orb blast"""
        if opponent:
            # Create expanding circular attack
            attack_width = 200
            attack_height = 200
            center_x = self.x + self.width/2
            center_y = self.y + self.height/2
            
            # Calculate distance to opponent's center
            opp_center_x = opponent.x + opponent.width/2
            opp_center_y = opponent.y + opponent.height/2
            distance = math.sqrt((center_x - opp_center_x)**2 + (center_y - opp_center_y)**2)
            
            if distance < attack_width/2:
                damage = self.calculate_attack_damage() * 1.5
                # Knockback away from center
                angle = math.atan2(opp_center_y - center_y, opp_center_x - center_x)
                opponent.velocity_x = math.cos(angle) * 15
                opponent.velocity_y = math.sin(angle) * 15
                opponent.take_damage(damage)
            
            self.using_special = False
    
    def load_animations(self):
        base_path = "./imagens_characters/PNG/Mage"
        self.animations = {
            "idle": Animation(os.path.join(base_path, "Idle")),
            "walk": Animation(os.path.join(base_path, "Walk")),
            "attack": Animation(os.path.join(base_path, "Attack")),
            "attack_extra": Animation(os.path.join(base_path, "Attack_Extra")),
            "jump": Animation(os.path.join(base_path, "Jump")),
            "hurt": Animation(os.path.join(base_path, "Hurt")),
            "run": Animation(os.path.join(base_path, "Run"))
        }


class Archer(Character):
    def __init__(self, x, y, name, is_player2=False):
        super().__init__(x, y, name, is_player2)
        self.health = 0  # Start at 0%
        self.attack_power = 3  # Base damage
        self.defense = 5
        self.attack_range = 200
        self.special_damage = 6
        self.speed = 6
        self.width = 64
        self.height = 64
        self.base_knockback = 1.5  # Lower base knockback
    
    def get_color(self):
        """Archer's unique color"""
        return (0, 255, 0)  # Green for Archer
    
    def special_ability(self, opponent):
        """Archer's special ability: Recovery shot"""
        if opponent:
            # Create diagonal attack hitbox and boost upward
            attack_width = 150
            attack_height = 150
            
            # Boost in direction while attacking
            self.velocity_y = self.jump_force * 1.2
            self.velocity_x = self.direction * 10
            
            if self.direction == -1:  # Facing left
                hitbox = pygame.Rect(self.x - attack_width, self.y - attack_height/2, attack_width, attack_height)
            else:  # Facing right
                hitbox = pygame.Rect(self.x + self.width, self.y - attack_height/2, attack_width, attack_height)
            
            if hitbox.colliderect(pygame.Rect(opponent.x, opponent.y, opponent.width, opponent.height)):
                damage = self.calculate_attack_damage() * 1.8
                # Diagonal knockback
                opponent.velocity_x = self.direction * 12
                opponent.velocity_y = -12
                opponent.take_damage(damage)
            
            self.using_special = False
    
    def load_animations(self):
        base_path = "./imagens_characters/PNG/Rogue"
        self.animations = {
            "idle": Animation(os.path.join(base_path, "Idle")),
            "walk": Animation(os.path.join(base_path, "Walk")),
            "attack": Animation(os.path.join(base_path, "Attack")),
            "attack_extra": Animation(os.path.join(base_path, "Attack_Extra")),
            "jump": Animation(os.path.join(base_path, "Jump")),
            "hurt": Animation(os.path.join(base_path, "Hurt")),
            "run": Animation(os.path.join(base_path, "Run"))
        } 