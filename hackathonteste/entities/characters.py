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
        self.width = 75
        self.height = 80
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.speed = 5
        self.health = 0  # Damage percentage starts at 0
        self.max_health = 100  # Adjust based on your game
        self.max_health = 300  # Maximum percentage reduced
        self.base_knockback = 2  # Reduced base knockback
        self.knockback_growth = 0.2  # Reduced knockback growth
        self.attack_power = 10
        self.defense = 5
        self.attack_range = 60
        self.lives = 3
        
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
        
        # Visual effects
        self.effect_surfaces = {}
        self.active_effects = []
        self.effect_duration = 0
        self.font = pygame.font.Font(None, 24)  # Add font initialization
        
        # Effect colors
        self.effect_colors = {
            "perfect_block": (255, 215, 0, 128),  # Golden
            "charging": (255, 200, 0, 100),  # Orange
            "teleport": (100, 100, 255, 128),  # Blue
            "levitate": (100, 100, 255, 128),  # Blue
            "combo": (255, 255, 255, 255),  # White
            "dash": (100, 255, 100, 50)  # Green
        }
        self.attack_multiplier = 1.0
        self.has_power_buff = False
        self.power_buff_timer = 0
        self.max_health = 100  # Adjust based on your game
        self.max_mana = 100    # Adjust based on your game
    
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
                    knockback_y = -knockback_power * 0.7
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
        
        # Draw name only, removed percentage display
        name_font = pygame.font.Font(None, 24)
        name_surface = name_font.render(self.name, True, (255, 255, 255))
        screen.blit(name_surface, (self.x, self.y - 30))
        pygame.draw.rect(screen, (255, 255, 0), self.rect, 2)
        # Draw effects
        self.draw_effects(screen)
        self.update_effects()
    
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

    def add_visual_effect(self, effect_name, duration=10):
        """Add a visual effect to be displayed"""
        self.active_effects.append(effect_name)
        self.effect_duration = duration
    
    def update_effects(self):
        """Update visual effects"""
        if self.effect_duration > 0:
            self.effect_duration -= 1
        else:
            self.active_effects = []
    
    def draw_effects(self, screen):
        """Draw active visual effects"""
        if "perfect_block" in self.active_effects:
            # Draw golden shield effect with pulsing
            radius = self.width * 0.7
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 0.3 + 0.7
            shield_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            color = self.effect_colors["perfect_block"]
            pygame.draw.circle(shield_surface, color, (radius, radius), radius * pulse, 3)
            screen.blit(shield_surface, (self.x + self.width//2 - radius, self.y + self.height//2 - radius))
        
        if "charging" in self.active_effects:
            # Draw charging effect with particles
            charge_height = int(self.height * (getattr(self, 'charge_time', 0) / getattr(self, 'max_charge_time', 60)))
            charge_surface = pygame.Surface((self.width, charge_height), pygame.SRCALPHA)
            color = self.effect_colors["charging"]
            charge_surface.fill(color)
            
            # Add particle effects
            for _ in range(3):
                particle_x = random.randint(0, self.width)
                particle_y = random.randint(0, charge_height)
                particle_size = random.randint(2, 4)
                pygame.draw.circle(charge_surface, (255, 255, 200, 150), (particle_x, particle_y), particle_size)
            
            screen.blit(charge_surface, (self.x, self.y + self.height - charge_height))
        
        if "teleport" in self.active_effects:
            # Draw teleport trail with fade effect
            color = self.effect_colors["teleport"]
            for i in range(5):
                alpha = int(color[3] * (1 - i/5))
                trail_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                x = self.x - (self.direction * i * 20)
                pygame.draw.rect(trail_surface, (*color[:3], alpha), (0, 0, self.width, self.height))
                screen.blit(trail_surface, (x, self.y))
        
        if "levitate" in self.active_effects:
            # Draw levitation waves with dynamic effect
            wave_points = []
            time = pygame.time.get_ticks() * 0.01
            color = self.effect_colors["levitate"]
            
            for i in range(5):
                x = self.x + (i * self.width//4)
                y = self.y + self.height + math.sin(time + i) * 5
                wave_points.append((x, y))
            
            if len(wave_points) > 1:
                wave_surface = pygame.Surface((self.width, 20), pygame.SRCALPHA)
                pygame.draw.lines(wave_surface, color, False, [(x - self.x, y - self.y) for x, y in wave_points], 2)
                screen.blit(wave_surface, (self.x, self.y + self.height))
        
        if "combo" in self.active_effects:
            # Draw combo counter with dynamic scaling
            combo_count = getattr(self, 'combo_count', 0)
            scale = 1 + math.sin(pygame.time.get_ticks() * 0.01) * 0.2
            combo_text = self.font.render(f"Combo: {combo_count}", True, self.effect_colors["combo"][:3])
            scaled_text = pygame.transform.scale(combo_text, 
                (int(combo_text.get_width() * scale), int(combo_text.get_height() * scale)))
            screen.blit(scaled_text, (self.x, self.y - 60))
        
        if "dash" in self.active_effects:
            # Draw dash trail with motion blur effect
            color = self.effect_colors["dash"]
            for i in range(3):
                alpha = int(color[3] * (1 - i/3))
                ghost_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                ghost_surface.fill((*color[:3], alpha))
                screen.blit(ghost_surface, (self.x - (self.direction * i * 20), self.y))

    def update(self):
        # Update power buff
        if self.has_power_buff:
            self.power_buff_timer -= 1
            if self.power_buff_timer <= 0:
                self.has_power_buff = False
                self.attack_multiplier = 1.0


class Fighter(Character):
    def __init__(self, x, y, name, is_player2=False):
        super().__init__(x, y, name, is_player2)
        self.health = 0  # Start at 0%
        self.attack_power = 6  # High base damage
        self.defense = 8  # Highest defense
        self.attack_range = 70
        self.special_damage = 12
        self.speed = 4  # Slower but steady
        self.width = 100
        self.height = 100
        self.base_knockback = 3  # High base knockback
        
        # Knight specific attributes
        self.stamina = 100
        self.max_stamina = 100
        self.stamina_regen = 0.3  # Stamina regeneration per frame
        self.blocking = False
        self.perfect_block_window = 10  # Frames for perfect block timing
        self.perfect_block_timer = 0
        
        # Combat attributes
        self.combo_count = 0
        self.combo_timer = 0
        self.combo_timer_max = 45  # 0.75 seconds to continue combo
        self.attack_types = ["normal", "running", "heavy"]  # Different attack animations
        self.current_attack_type = "normal"
        
        # Charge attack
        self.charging = False
        self.charge_time = 0
        self.max_charge_time = 60  # 1 second for full charge
        self.charge_multiplier = 2.5  # Increased damage multiplier for fully charged attacks
        self.charge_attack_active = False  # New flag to prevent multiple hits
        
        # Special moves cooldowns
        self.slam_cooldown = 0
        self.slam_cooldown_max = 90  # 1.5 seconds
        self.push_cooldown = 0
        self.push_cooldown_max = 60  # 1 second
    
    def update_local(self, controls, opponent, buffs, platforms):
        """Update with enhanced knight abilities"""
        # Stamina regeneration
        if not self.charging and not self.blocking:
            self.stamina = min(self.max_stamina, self.stamina + self.stamina_regen)
        
        # Cooldown timers
        if self.slam_cooldown > 0:
            self.slam_cooldown -= 1
        if self.push_cooldown > 0:
            self.push_cooldown -= 1
        
        # Perfect block timer
        if self.perfect_block_timer > 0:
            self.perfect_block_timer -= 1
        
        # Combo timer
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo_count = 0
        
        # Movement with running attack
        if controls["right"] or controls["left"]:
            if controls["attack"] and self.stamina >= 15:
                self.state = "run_attack"
                self.current_attack_type = "running"
                self.stamina -= 0.5  # Drain stamina while running and attacking
            else:
                self.state = "run" if abs(self.velocity_x) > 2 else "walk"
        
        # Blocking mechanics
        self.blocking = controls["defend"] and self.stamina >= 10
        if self.blocking:
            self.stamina -= 0.2  # Drain stamina while blocking
            self.perfect_block_timer = self.perfect_block_window  # Start perfect block window
            self.velocity_x *= 0.7  # Slower movement while blocking
        
        # Charge attack system
        if controls["attack"] and not self.attacking and not self.charging and not self.charge_attack_active:
            self.charging = True
            self.charge_time = 0
            self.state = "attack_extra"  # Use heavy attack animation while charging
            self.attacking = True  # Set attacking to true to prevent normal attacks
        elif self.charging and controls["attack"]:
            self.charge_time = min(self.charge_time + 1, self.max_charge_time)
            # Visual feedback while charging
            self.add_visual_effect("charging", 5)
            # Prevent movement while charging
            self.velocity_x *= 0.8
            # Prevent damage during charge
            self.attack_frame = 0  # Reset attack frame to prevent damage
        elif self.charging:  # Released attack button
            # Release charge attack
            self.charging = False
            self.charge_attack_active = True
            charge_ratio = self.charge_time / self.max_charge_time
            
            # Different attacks based on charge time
            if charge_ratio > 0.8:  # Fully charged
                self.current_attack_type = "heavy"
                damage_mult = self.charge_multiplier
                self.state = "attack_extra"
            else:  # Normal attack with charge bonus
                self.current_attack_type = "normal"
                damage_mult = 1 + (charge_ratio * 0.5)
                self.state = "attack"
            
            # Apply attack only once when releasing the charge
            if self.rect.colliderect(opponent.rect):
                damage = self.calculate_attack_damage() * damage_mult
                opponent.take_damage(damage)
                knockback_power = self.base_knockback * (1 + charge_ratio)
                opponent.velocity_x = self.direction * knockback_power
                opponent.velocity_y = -knockback_power * 0.5
        
        # Reset charge attack state
        if self.charge_attack_active and self.attack_frame >= self.attack_cooldown_max:
            self.charge_attack_active = False
            self.attacking = False
            self.attack_cooldown = self.attack_cooldown_max
        
        # Special ability (Ground slam or uppercut)
        if controls["special"] and not self.using_special and self.slam_cooldown <= 0 and self.stamina >= 30:
            self.using_special = True
            self.special_frame = 0
            self.slam_cooldown = self.slam_cooldown_max
            self.stamina -= 30
            
            attack_width = 120
            attack_height = 80
            
            if not self.on_ground:
                # Ground slam
                self.state = "attack_extra"
                self.velocity_y = 20
                hitbox = pygame.Rect(self.x - attack_width/2, self.y + self.height, attack_width, attack_height)
            else:
                # Uppercut
                self.state = "attack"
                self.velocity_y = self.jump_force * 1.2
                hitbox = pygame.Rect(self.x - attack_width/2, self.y - attack_height, attack_width, attack_height)
            
            if hitbox.colliderect(opponent.rect):
                damage = self.special_damage * (1.5 if not self.on_ground else 1.2)
                opponent.take_damage(damage)
                # Strong vertical knockback
                opponent.velocity_y = -15 if self.on_ground else 15
                opponent.velocity_x = self.direction * 10
        
        # Push attack
        if controls["defend"] and controls["attack"] and self.push_cooldown <= 0 and self.stamina >= 20:
            self.state = "push"
            self.push_cooldown = self.push_cooldown_max
            self.stamina -= 20
            
            if self.rect.colliderect(opponent.rect):
                push_power = 12
                opponent.velocity_x = self.direction * push_power
                opponent.velocity_y = -4
                # Stun effect
                opponent.attack_cooldown = max(opponent.attack_cooldown, 30)
        
        # Visual feedback for charging
        if self.charging:
            self.add_visual_effect("charging")
        
        # Visual feedback for perfect block
        if self.blocking and self.perfect_block_timer > 0:
            self.add_visual_effect("perfect_block", 5)
        
        super().update_local(controls, opponent, buffs, platforms)
    
    def take_damage(self, damage):
        """Override to add perfect block mechanic"""
        if self.blocking:
            if self.perfect_block_timer > 0:
                # Perfect block
                damage = 0
                self.stamina = min(self.max_stamina, self.stamina + 20)  # Gain stamina on perfect block
            else:
                # Normal block
                damage *= 0.2  # Block 80% of damage
                self.stamina -= damage  # Drain stamina based on damage blocked
        
        super().take_damage(damage)
    
    def special_ability(self, opponent):
        """Knight's special ability: Ground pound or uppercut"""
        attack_width = 120
        attack_height = 80
        damage = 0
        
        if not self.on_ground:
            # Ground slam
            self.state = "attack_extra"
            self.velocity_y = 20
            hitbox = pygame.Rect(self.x - attack_width/2, self.y + self.height, attack_width, attack_height)
            damage = self.special_damage * 1.5
        else:
            # Uppercut
            self.state = "attack"
            self.velocity_y = self.jump_force * 1.2
            hitbox = pygame.Rect(self.x - attack_width/2, self.y - attack_height, attack_width, attack_height)
            damage = self.special_damage * 1.2
        
        if hitbox.colliderect(opponent.rect):
            opponent.take_damage(damage)
            # Strong vertical knockback
            opponent.velocity_y = -15 if self.on_ground else 15
            opponent.velocity_x = self.direction * 10
        
        return damage  # Return damage for knockback calculation
    
    def draw(self, screen):
        """Override draw to add stamina bar"""
        super().draw(screen)
        
        # Barra de stamina removida - será exibida apenas no HUD
        
        # Show perfect block indicator
        if self.perfect_block_timer > 0:
            pygame.draw.circle(screen, (255, 215, 0), (self.x + self.width//2, self.y - 50), 5)
    
    def get_color(self):
        """Knight's unique color"""
        return (255, 0, 0)  # Red for Knight
    
    def load_animations(self):
        base_path = "./imagens_characters/PNG/Knight"
        self.animations = {
            "idle": Animation(os.path.join(base_path, "Idle")),
            "walk": Animation(os.path.join(base_path, "Walk")),
            "run": Animation(os.path.join(base_path, "Run")),
            "attack": Animation(os.path.join(base_path, "Attack")),
            "attack_extra": Animation(os.path.join(base_path, "Attack_Extra")),
            "walk_attack": Animation(os.path.join(base_path, "Walk_Attack")),
            "run_attack": Animation(os.path.join(base_path, "Run_Attack")),
            "jump": Animation(os.path.join(base_path, "Jump")),
            "high_jump": Animation(os.path.join(base_path, "High_Jump")),
            "hurt": Animation(os.path.join(base_path, "Hurt")),
            "climb": Animation(os.path.join(base_path, "Climb")),
            "push": Animation(os.path.join(base_path, "Push"))
        }


class FireProjectile:
    def __init__(self, x, y, direction, damage, is_special=False):
        self.x = x
        self.y = y
        self.direction = direction
        self.damage = damage
        self.is_special = is_special
        self.width = 30 if not is_special else 60
        self.height = 20 if not is_special else 40
        self.speed = 15 if not is_special else 10
        self.lifetime = 60 if not is_special else 30  # Frames until disappear
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # Visual effect properties
        self.alpha = 255
        self.fade_rate = 5 if not is_special else 8
    
    def update(self):
        self.x += self.direction * self.speed
        self.rect.x = self.x
        self.rect.y = self.y
        self.lifetime -= 1
        
        # Fade out effect
        if self.lifetime < 30:
            self.alpha = max(0, self.alpha - self.fade_rate)
        
        return self.lifetime > 0
    
    def draw(self, screen):
        # Create a surface for the projectile with transparency
        projectile_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw the projectile with current alpha
        if self.is_special:
            color = (255, 100, 0, self.alpha)  # Orange for special
            pygame.draw.ellipse(projectile_surface, color, (0, 0, self.width, self.height))
        else:
            color = (255, 0, 0, self.alpha)  # Red for normal
            pygame.draw.ellipse(projectile_surface, color, (0, 0, self.width, self.height))
        
        screen.blit(projectile_surface, (self.x, self.y))


class Mage(Character):
    def __init__(self, x, y, name, is_player2=False):
        super().__init__(x, y, name, is_player2)
        self.health = 0  # Start at 0%
        self.attack_power = 4  # Base damage
        self.defense = 3  # Lowest defense but powerful ranged attacks
        self.attack_range = 200  # Longest range
        self.special_damage = 8
        self.speed = 4  # Slower movement speed
        self.width = 100
        self.height = 100
        self.base_knockback = 2
        
        # Configurações de pulo idênticas à classe base (Character)
        self.gravity = 0.8
        self.jump_force = -15
        self.jumps_left = 2
        
        # Mage specific attributes
        self.mana = 100
        self.max_mana = 100
        self.mana_regen = 0.5  # Mana regeneration per frame
        self.fire_cooldown = 0
        self.fire_cooldown_max = 45  # 0.75 seconds
        self.fire_extra_cooldown = 0
        self.fire_extra_cooldown_max = 120  # 2 seconds
        
        # Atributos para custo de mana dos ataques
        self.fire_mana_cost = 20
        self.fire_extra_mana_cost = 40
        
        # Substituindo levitação por pulo contínuo
        self.continuous_jump_power = -0.7  # Impulso mais leve para cima por frame
        self.continuous_jump_mana_cost = 0.5  # Reduzido o custo de mana por frame
        
        # Combo system for spells
        self.spell_combo = []
        self.combo_timer = 0
        self.combo_timer_max = 60  # 1 second to complete combo
        
        # Projectile management
        self.projectiles = []
        self.projectile_damage = 15
        self.special_projectile_damage = 25
    
    def update_local(self, controls, opponent, buffs, platforms):
        """Update with enhanced magic abilities"""
        # Update existing projectiles
        self.projectiles = [proj for proj in self.projectiles if proj.update()]
        
        # Mana regeneration
        self.mana = min(self.max_mana, self.mana + self.mana_regen)
        
        # Cooldown timers
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1
        if self.fire_extra_cooldown > 0:
            self.fire_extra_cooldown -= 1
        
        # Combo timer
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.spell_combo = []
        
        # Pulo contínuo enquanto mantém o botão pressionado e tem mana
        if controls["up"] and not self.on_ground and self.mana >= self.continuous_jump_mana_cost:
            # Aplicando um impulso para cima enquanto o botão é pressionado
            self.velocity_y += self.continuous_jump_power
            # Limitando a velocidade máxima de subida
            self.velocity_y = max(self.velocity_y, -8)
            # Consumindo mana
            self.mana -= self.continuous_jump_mana_cost
            self.state = "jump"
            self.add_visual_effect("levitate", 5)
        
        # Basic attack (Fire spell)
        if controls["attack"] and self.fire_cooldown <= 0 and self.mana >= self.fire_mana_cost:
            self.attacking = True
            self.attack_frame = 0
            self.fire_cooldown = self.fire_cooldown_max
            self.mana -= self.fire_mana_cost
            self.state = "fire"
            
            # Create fire projectile
            projectile = FireProjectile(
                self.x + (self.width if self.direction == 1 else 0),
                self.y + self.height/2,
                self.direction,
                self.projectile_damage
            )
            self.projectiles.append(projectile)
        
        # Special ability (Enhanced fire spell)
        if controls["special"] and self.fire_extra_cooldown <= 0 and self.mana >= self.fire_extra_mana_cost:
            self.using_special = True
            self.special_frame = 0
            self.fire_extra_cooldown = self.fire_extra_cooldown_max
            self.mana -= self.fire_extra_mana_cost
            self.state = "fire_extra"
            
            # Create special fire projectile
            projectile = FireProjectile(
                self.x + (self.width if self.direction == 1 else 0),
                self.y + self.height/2,
                self.direction,
                self.special_projectile_damage,
                is_special=True
            )
            self.projectiles.append(projectile)
        
        # Check projectile collisions
        for projectile in self.projectiles:
            if projectile.rect.colliderect(opponent.rect):
                opponent.take_damage(projectile.damage)
                # Knockback based on projectile type
                knockback_power = 12 if projectile.is_special else 8
                opponent.velocity_x = projectile.direction * knockback_power
                opponent.velocity_y = -6
                self.projectiles.remove(projectile)
                break
        
        # Defensive teleport (using climb animation)
        if controls["defend"] and self.mana >= 30:
            self.state = "climb"
            self.mana -= 30
            # Teleport in facing direction
            teleport_distance = 150
            new_x = self.x + (teleport_distance * self.direction)
            # Check if new position is valid
            if 0 <= new_x <= 800 - self.width:
                self.x = new_x
                self.velocity_x = self.direction * 5  # Small momentum after teleport
        
        # Visual feedback for teleport
        if controls["defend"] and self.mana >= 30:
            self.add_visual_effect("teleport", 10)
        
        super().update_local(controls, opponent, buffs, platforms)
    
    def special_ability(self, opponent):
        """Mage's special ability: Enhanced fire blast"""
        # Create large fire explosion
        attack_width = 250
        attack_height = 200
        center_x = self.x + self.width/2
        center_y = self.y + self.height/2
        
        # Calculate distance to opponent's center
        opp_center_x = opponent.x + opponent.width/2
        opp_center_y = opponent.y + opponent.height/2
        distance = math.sqrt((center_x - opp_center_x)**2 + (center_y - opp_center_y)**2)
        
        damage = 0
        if distance < attack_width/2:
            damage = self.special_damage * 1.8
            # Knockback away from center with fire lift
            angle = math.atan2(opp_center_y - center_y, opp_center_x - center_x)
            opponent.velocity_x = math.cos(angle) * 18
            opponent.velocity_y = -15  # Strong upward knockback
            opponent.take_damage(damage)
        
        return damage  # Return damage for knockback calculation
    
    def draw(self, screen):
        """Override draw to add projectiles and mana bar"""
        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(screen)
        
        super().draw(screen)
        
        # Barra de mana removida - será exibida apenas no HUD
    
    def get_color(self):
        """Mage's unique color"""
        return (0, 0, 255)  # Blue for Mage
    
    def load_animations(self):
        base_path = "./imagens_characters/PNG/Mage"
        self.animations = {
            "idle": Animation(os.path.join(base_path, "Idle")),
            "walk": Animation(os.path.join(base_path, "Walk")),
            "attack": Animation(os.path.join(base_path, "Attack")),
            "attack_extra": Animation(os.path.join(base_path, "Attack_Extra")),
            "jump": Animation(os.path.join(base_path, "Jump")),
            "high_jump": Animation(os.path.join(base_path, "High_Jump")),
            "hurt": Animation(os.path.join(base_path, "Hurt")),
            "run": Animation(os.path.join(base_path, "Run")),
            "fire": Animation(os.path.join(base_path, "Fire")),
            "fire_extra": Animation(os.path.join(base_path, "Fire_Extra")),
            "climb": Animation(os.path.join(base_path, "Climb"))  # Used for teleport
        }


class Rogue(Character):
    def __init__(self, x, y, name, is_player2=False):
        super().__init__(x, y, name, is_player2)
        self.health = 0  # Start at 0%
        self.attack_power = 3  # Base damage
        self.defense = 4  # Lower defense but more agile
        self.attack_range = 200
        self.special_damage = 6
        self.speed = 7  # Increased base speed
        self.width = 100
        self.height = 100
        self.base_knockback = 1.5
        
        # Sistema de energia
        self.energy = 100
        self.max_energy = 100
        self.energy_regen = 0.4  # Regeneração de energia por frame
        
        # Custos de energia
        self.dash_energy_cost = 25
        self.push_energy_cost = 15
        self.double_jump_energy_cost = 10
        
        # Rogue specific attributes
        self.can_climb = True
        self.climbing = False
        self.climb_speed = 4
        self.double_jump_available = True
        self.run_multiplier = 1.6  # Run speed multiplier
        self.combo_count = 0
        self.combo_timer = 0
        self.max_combo = 3
        self.dash_cooldown = 0
        self.dash_cooldown_max = 60  # 1 second
        self.push_cooldown = 0
        self.push_cooldown_max = 90  # 1.5 seconds
        self.special_frame = 0  # Initialize special_frame
        self.special_duration = 15  # Duration of special ability in frames
    
    def update_local(self, controls, opponent, buffs, platforms):
        """Update with enhanced movement and abilities"""
        # Regeneração de energia
        self.energy = min(self.max_energy, self.energy + self.energy_regen)
        
        # Reset combo if timer expires
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo_count = 0
        
        # Cooldown timers
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
        if self.push_cooldown > 0:
            self.push_cooldown -= 1
        
        # Enhanced movement
        if controls["right"]:
            speed_mult = self.run_multiplier if controls["attack"] else 1.0
            self.velocity_x = min(self.velocity_x + 1, self.speed * speed_mult)
            self.direction = 1
            self.state = "run" if speed_mult > 1 else "walk"
        elif controls["left"]:
            speed_mult = self.run_multiplier if controls["attack"] else 1.0
            self.velocity_x = max(self.velocity_x - 1, -self.speed * speed_mult)
            self.direction = -1
            self.state = "run" if speed_mult > 1 else "walk"
        
        # Climbing mechanics
        near_wall = False  # This should be checked against actual walls in the game
        if self.can_climb and controls["up"] and near_wall:
            self.climbing = True
            self.velocity_y = -self.climb_speed
        elif self.climbing and not controls["up"]:
            self.climbing = False
        
        # Double jump com custo de energia
        if controls["up"]:
            if self.on_ground:
                self.velocity_y = self.jump_force
                self.double_jump_available = True
                self.state = "jump"
            elif self.double_jump_available and not self.climbing and self.energy >= self.double_jump_energy_cost:
                self.velocity_y = self.jump_force * 0.8
                self.double_jump_available = False
                self.energy -= self.double_jump_energy_cost
                self.state = "high_jump"
        
        # Combat system with combos
        if controls["attack"] and self.attack_cooldown <= 0:
            self.attacking = True
            self.attack_frame = 0
            self.combo_timer = 30  # Half second to continue combo
            
            # Different attacks based on combo count
            if self.combo_count == 0:
                self.state = "attack"
                damage = self.attack_power
            elif self.combo_count == 1:
                self.state = "walk_attack"
                damage = self.attack_power * 1.2
            else:
                self.state = "attack_extra"
                damage = self.attack_power * 1.5
            
            self.combo_count = (self.combo_count + 1) % self.max_combo
            
            # Apply damage if in range
            if self.rect.colliderect(opponent.rect):
                opponent.take_damage(damage)
                self.apply_knockback(self.direction, damage)
        
        # Push ability com custo de energia
        if controls["defend"] and self.push_cooldown <= 0 and self.energy >= self.push_energy_cost:
            self.state = "push"  # Set animation state to push
            self.push_cooldown = self.push_cooldown_max
            self.energy -= self.push_energy_cost
            # Add visual effect for push
            self.add_visual_effect("dash", 10)  # Reuse dash effect for push visualization
            
            if self.rect.colliderect(opponent.rect):
                push_power = 15
                opponent.velocity_x = self.direction * push_power
                opponent.velocity_y = -5
        
        # Special ability (dash attack) com custo de energia
        if controls["special"] and not self.using_special and self.dash_cooldown <= 0 and self.energy >= self.dash_energy_cost:
            self.using_special = True
            self.special_frame = 0  # Reset frame counter
            self.dash_cooldown = self.dash_cooldown_max
            self.energy -= self.dash_energy_cost
            self.state = "run_attack"
            dash_speed = 20
            self.velocity_x = self.direction * dash_speed
            
            # Apply damage immediately if in contact
            if self.rect.colliderect(opponent.rect):
                damage = self.special_damage
                opponent.take_damage(damage)
                # Strong horizontal knockback
                opponent.velocity_x = self.direction * 15
                opponent.velocity_y = -8
            
            # Add dash effect
            self.add_visual_effect("dash", 15)
        
        # Continue checking for dash attack collision during the dash
        if self.using_special:
            if self.special_frame < 10:  # Check for first 10 frames of dash
                if self.rect.colliderect(opponent.rect):
                    damage = self.special_damage
                    opponent.take_damage(damage)
                    opponent.velocity_x = self.direction * 15
                    opponent.velocity_y = -8
                    self.using_special = False  # End special after hitting
            
            # Update special frame and check duration
            self.special_frame += 1
            if self.special_frame >= self.special_duration:
                self.using_special = False
                self.special_frame = 0
        
        super().update_local(controls, opponent, buffs, platforms)
    
    def special_ability(self, opponent):
        """Rogue's special ability: Dash Attack"""
        if self.dash_cooldown <= 0 and self.energy >= self.dash_energy_cost:
            self.state = "run_attack"
            self.dash_cooldown = self.dash_cooldown_max
            self.energy -= self.dash_energy_cost
            dash_speed = 20
            self.velocity_x = self.direction * dash_speed
            
            if opponent and self.rect.colliderect(opponent.rect):
                damage = self.special_damage
                opponent.take_damage(damage)
                # Strong horizontal knockback
                opponent.velocity_x = self.direction * 15
                opponent.velocity_y = -8
            
            self.using_special = False
            return self.special_damage
        return 0
    
    def get_color(self):
        """Rogue's unique color"""
        return (0, 255, 0)  # Green for Rogue
    
    def load_animations(self):
        base_path = "./imagens_characters/PNG/Rogue"
        self.animations = {
            "idle": Animation(os.path.join(base_path, "Idle")),
            "walk": Animation(os.path.join(base_path, "Walk")),
            "attack": Animation(os.path.join(base_path, "Attack")),
            "attack_extra": Animation(os.path.join(base_path, "Attack_Extra")),
            "jump": Animation(os.path.join(base_path, "Jump")),
            "hurt": Animation(os.path.join(base_path, "Hurt")),
            "run": Animation(os.path.join(base_path, "Run")),
            "push": Animation(os.path.join(base_path, "Push"))  # Added Push animation
        }