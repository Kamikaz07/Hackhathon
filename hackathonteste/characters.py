import pygame
import random
import math

class Character:
    def __init__(self, x, y, name, is_player2=False):
        self.x = x
        self.y = y
        self.name = name
        self.is_player2 = is_player2
        self.width = 50
        self.height = 50
        self.speed = 5
        self.health = 200
        self.attack_power = 10
        self.defense = 5
        self.attack_range = 60
        self.special_cooldown = 0
        self.special_cooldown_max = 180  # 3 seconds
        self.attacking = False
        self.defending = False
        self.using_special = False
        self.attack_frame = 0
        self.attack_cooldown = 0
        self.attack_cooldown_max = 30  # 0.5 seconds between attacks
        self.direction = -1 if is_player2 else 1
        self.active_buffs = []
        self.color = self.get_color()
        self.attack_hitbox = pygame.Rect(0, 0, 0, 0)
        
        # Visual representation
        self.sprite = pygame.Surface((self.width, self.height))
        self.sprite.fill(self.color)
    
    def get_color(self):
        """Get base color for the character"""
        return (200, 200, 200)  # Default gray color for base character
    
    def move(self, keys):
        """Move the character based on key input"""
        if self.is_player2:
            return  # Player2 movement is controlled by local updates
        
        # Apply speed buff if any
        speed_multiplier = 1.0
        for buff in self.active_buffs:
            if buff.buff_type == "speed":
                speed_multiplier = 1.5
                break
        
        actual_speed = self.speed * speed_multiplier
        
        if keys[pygame.K_LEFT]:
            self.x -= actual_speed
            self.direction = -1
        if keys[pygame.K_RIGHT]:
            self.x += actual_speed
            self.direction = 1
        if keys[pygame.K_UP]:
            self.y -= actual_speed
        if keys[pygame.K_DOWN]:
            self.y += actual_speed
        
        # Boundary checking
        self.x = max(0, min(800 - self.width, self.x))
        self.y = max(0, min(600 - self.height, self.y))
    
    def attack(self, keys, opponent):
        """Perform a basic attack"""
        if self.is_player2:
            return
        
        if keys[pygame.K_SPACE] and not self.attacking and not self.defending and not self.using_special and self.attack_cooldown == 0:
            self.attacking = True
            self.attack_frame = 10
            self.attack_cooldown = self.attack_cooldown_max
            
            # Create attack hitbox based on direction
            attack_width = 80
            attack_height = 60
            if self.direction == -1:  # Facing left
                self.attack_hitbox = pygame.Rect(self.x - attack_width, self.y, attack_width, attack_height)
            else:  # Facing right
                self.attack_hitbox = pygame.Rect(self.x + self.width, self.y, attack_width, attack_height)
        
        if self.attacking:
            self.attack_frame -= 1
            
            # Check for hit during the attack animation
            if opponent and self.attack_hitbox.colliderect(pygame.Rect(opponent.x, opponent.y, opponent.width, opponent.height)):
                damage = self.calculate_attack_damage()
                if opponent.defending:
                    damage = max(0, damage - opponent.defense)
                opponent.take_damage(damage)
            
            # End attack animation
            if self.attack_frame <= 0:
                self.attacking = False
                self.attack_hitbox = pygame.Rect(0, 0, 0, 0)
    
    def defend(self, keys):
        """Perform defense"""
        if self.is_player2:
            return
        
        self.defending = keys[pygame.K_x] and not self.attacking and not self.using_special
    
    def use_special(self, keys, opponent):
        """Use special ability"""
        if self.is_player2:
            return
        
        if keys[pygame.K_z] and not self.attacking and not self.defending and self.special_cooldown == 0:
            self.using_special = True
            self.special_ability(opponent)
            self.special_cooldown = self.special_cooldown_max
    
    def special_ability(self, opponent):
        """Special ability, overridden by subclasses"""
        pass
    
    def take_damage(self, damage):
        """Take damage, reduced if defending"""
        if self.defending:
            # Apply defense buff if any
            defense_multiplier = 1.0
            for buff in self.active_buffs:
                if buff.buff_type == "defense":
                    defense_multiplier = 1.5
                    break
            
            actual_defense = self.defense * defense_multiplier
            damage = max(0, damage - actual_defense)
        
        self.health = max(0, self.health - damage)
    
    def calculate_attack_damage(self):
        """Calculate attack damage, including buffs"""
        # Apply attack buff if any
        attack_multiplier = 1.0
        for buff in self.active_buffs:
            if buff.buff_type == "attack":
                attack_multiplier = 1.5
                break
        
        return self.attack_power * attack_multiplier
    
    def is_in_range(self, opponent, range_value):
        """Check if opponent is in range"""
        if not opponent:
            return False
        
        distance = math.sqrt((self.x - opponent.x) ** 2 + (self.y - opponent.y) ** 2)
        return distance <= range_value
    
    def add_buff(self, buff):
        """Add a buff to the character"""
        # Check if we already have this type of buff
        for existing_buff in self.active_buffs:
            if existing_buff.buff_type == buff.buff_type:
                # Extend the duration
                existing_buff.duration += buff.duration
                return
        
        # Otherwise, add the new buff
        if buff.buff_type == "health":
            # Health buff immediately adds 20 health
            self.health = min(200, self.health + 20)
        else:
            # Other buffs are added to active_buffs
            self.active_buffs.append(buff)
    
    def update_buffs(self):
        """Update buff durations and remove expired buffs"""
        for buff in self.active_buffs[:]:
            buff.duration -= 1
            if buff.duration <= 0:
                self.active_buffs.remove(buff)
    
    def get_speed(self):
        """Get current speed, including buffs"""
        speed_multiplier = 1.0
        for buff in self.active_buffs:
            if buff.buff_type == "speed":
                speed_multiplier = 1.5
                break
        return self.speed * speed_multiplier
    
    def update_local(self, controls, opponent, buffs):
        """Update character with local controls"""
        if not self.attacking and not self.using_special:
            # Movement
            if controls["left"]:
                self.x = max(0, self.x - self.get_speed())
                self.direction = -1
            if controls["right"]:
                self.x = min(800 - self.width, self.x + self.get_speed())
                self.direction = 1
            if controls["up"]:
                self.y = max(0, self.y - self.get_speed())
            if controls["down"]:
                self.y = min(600 - self.height, self.y + self.get_speed())
        
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # Attack
        if controls["attack"] and not self.attacking and not self.using_special and self.attack_cooldown == 0:
            self.attacking = True
            self.attack_frame = 10
            self.attack_cooldown = self.attack_cooldown_max
            
            # Create attack hitbox based on direction
            attack_width = 80
            attack_height = 60
            if self.direction == -1:  # Facing left
                self.attack_hitbox = pygame.Rect(self.x - attack_width, self.y, attack_width, attack_height)
            else:  # Facing right
                self.attack_hitbox = pygame.Rect(self.x + self.width, self.y, attack_width, attack_height)
        
        if self.attacking:
            self.attack_frame -= 1
            
            # Check for hit during the attack animation
            if opponent and self.attack_hitbox.colliderect(pygame.Rect(opponent.x, opponent.y, opponent.width, opponent.height)):
                damage = self.calculate_attack_damage()
                if opponent.defending:
                    damage = max(0, damage - opponent.defense)
                opponent.take_damage(damage)
            
            # End attack animation
            if self.attack_frame <= 0:
                self.attacking = False
                self.attack_hitbox = pygame.Rect(0, 0, 0, 0)
        
        # Defense
        self.defending = controls["defend"] and not self.attacking and not self.using_special
        
        # Special ability
        if controls["special"] and not self.attacking and not self.defending and self.special_cooldown == 0:
            self.using_special = True
            self.special_ability(opponent)
            self.special_cooldown = self.special_cooldown_max
        
        # Update special cooldown
        if self.special_cooldown > 0:
            self.special_cooldown -= 1
        
        # Update buffs
        self.update_buffs()
    
    def draw(self, screen):
        """Draw the character"""
        # Base character
        sprite = pygame.Surface((self.width, self.height))
        sprite.fill(self.color)
        
        # Add visual indication for state
        if self.attacking:
            # Draw attack animation
            attack_color = (255, 255, 0)
            if self.direction == -1:  # Facing left
                pygame.draw.rect(screen, attack_color, (self.x - 80, self.y, 80, 60), 2)
            else:  # Facing right
                pygame.draw.rect(screen, attack_color, (self.x + self.width, self.y, 80, 60), 2)
        
        if self.defending:
            pygame.draw.rect(sprite, (0, 0, 255), (0, 0, self.width, self.height), 3)
        
        if self.using_special:
            special_indicator = pygame.Surface((30, 10))
            special_indicator.fill((255, 0, 255))
            sprite.blit(special_indicator, (10, 10))
        
        # Draw buffs indicators
        y_offset = 20
        for buff in self.active_buffs:
            buff_indicator = pygame.Surface((10, 10))
            
            if buff.buff_type == "attack":
                buff_indicator.fill((255, 0, 0))
            elif buff.buff_type == "defense":
                buff_indicator.fill((0, 0, 255))
            elif buff.buff_type == "speed":
                buff_indicator.fill((0, 255, 0))
            
            sprite.blit(buff_indicator, (0, y_offset))
            y_offset += 15
        
        # Draw health bar
        health_bar_width = self.width
        health_bar_height = 5
        health_percentage = self.health / 200
        
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y - 10, health_bar_width, health_bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 10, health_bar_width * health_percentage, health_bar_height))
        
        # Draw name
        font = pygame.font.Font(None, 24)
        name_surface = font.render(self.name, True, (255, 255, 255))
        screen.blit(name_surface, (self.x, self.y - 30))
        
        # Draw character sprite
        screen.blit(sprite, (self.x, self.y))


class Fighter(Character):
    def __init__(self, x, y, name, is_player2=False):
        super().__init__(x, y, name, is_player2)
        self.health = 250
        self.attack_power = 25  # Higher attack power for Fighter
        self.defense = 8
        self.attack_range = 70
        self.special_damage = 30
        self.speed = 4
        
        # Visual representation
        self.sprite = pygame.Surface((self.width, self.height))
        self.sprite.fill(self.color)
    
    def get_color(self):
        """Fighter's unique color"""
        return (255, 0, 0)  # Red for Fighter
    
    def special_ability(self, opponent):
        """Fighter's special ability: Strong blow that does double damage"""
        if opponent:
            # Create large attack hitbox
            attack_width = 120
            attack_height = 100
            if self.direction == -1:  # Facing left
                hitbox = pygame.Rect(self.x - attack_width, self.y - 20, attack_width, attack_height)
            else:  # Facing right
                hitbox = pygame.Rect(self.x + self.width, self.y - 20, attack_width, attack_height)
            
            if hitbox.colliderect(pygame.Rect(opponent.x, opponent.y, opponent.width, opponent.height)):
                damage = self.calculate_attack_damage() * 2
                opponent.take_damage(damage)
            self.using_special = False


class Mage(Character):
    def __init__(self, x, y, name, is_player2=False):
        super().__init__(x, y, name, is_player2)
        self.health = 180
        self.attack_power = 12
        self.defense = 4
        self.attack_range = 150
        self.special_damage = 35
        self.speed = 5
        
        # Visual representation
        self.sprite = pygame.Surface((self.width, self.height))
        self.sprite.fill(self.color)
    
    def get_color(self):
        """Mage's unique color"""
        return (0, 0, 255)  # Blue for Mage
    
    def special_ability(self, opponent):
        """Mage's special ability: Freeze opponent"""
        if opponent:
            # Create large attack hitbox
            attack_width = 150
            attack_height = 150
            if self.direction == -1:  # Facing left
                hitbox = pygame.Rect(self.x - attack_width, self.y - 35, attack_width, attack_height)
            else:  # Facing right
                hitbox = pygame.Rect(self.x + self.width, self.y - 35, attack_width, attack_height)
            
            if hitbox.colliderect(pygame.Rect(opponent.x, opponent.y, opponent.width, opponent.height)):
                damage = self.calculate_attack_damage() * 1.5
                opponent.take_damage(damage)
                # TODO: Add freeze effect
            self.using_special = False


class Archer(Character):
    def __init__(self, x, y, name, is_player2=False):
        super().__init__(x, y, name, is_player2)
        self.health = 200
        self.attack_power = 8
        self.defense = 5
        self.attack_range = 200
        self.special_damage = 25
        self.speed = 6
        
        # Visual representation
        self.sprite = pygame.Surface((self.width, self.height))
        self.sprite.fill(self.color)
    
    def get_color(self):
        """Archer's unique color"""
        return (0, 255, 0)  # Green for Archer
    
    def special_ability(self, opponent):
        """Archer's special ability: Long range powerful shot"""
        if opponent:
            # Create very long attack hitbox
            attack_width = 300
            attack_height = 40
            if self.direction == -1:  # Facing left
                hitbox = pygame.Rect(self.x - attack_width, self.y + 20, attack_width, attack_height)
            else:  # Facing right
                hitbox = pygame.Rect(self.x + self.width, self.y + 20, attack_width, attack_height)
            
            if hitbox.colliderect(pygame.Rect(opponent.x, opponent.y, opponent.width, opponent.height)):
                damage = self.calculate_attack_damage() * 1.8
                opponent.take_damage(damage)
            self.using_special = False 