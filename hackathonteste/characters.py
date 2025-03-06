import pygame
import random
import math

class Character:
    def __init__(self, x, y, name, is_opponent=False):
        self.x = x
        self.y = y
        self.name = name
        self.is_opponent = is_opponent
        self.width = 50
        self.height = 80
        self.speed = 5
        self.health = 100
        self.attack_power = 10
        self.defense_power = 5
        self.special_power = 20
        self.special_cooldown = 0
        self.special_cooldown_max = 60 * 3  # 3 seconds
        self.attacking = False
        self.defending = False
        self.using_special = False
        self.attack_frame = 0
        self.attack_frame_max = 30
        self.direction = 1 if is_opponent else -1  # -1 = left, 1 = right
        self.active_buffs = []
        self.color = (255, 0, 0)  # Default color, overridden by subclasses
        
        # Visual representation
        self.sprite = pygame.Surface((self.width, self.height))
        self.sprite.fill(self.color)
    
    def move(self, keys):
        """Move the character based on key input"""
        if self.is_opponent:
            return  # Opponent movement is controlled by network updates
        
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
        if self.is_opponent:
            return
        
        if keys[pygame.K_SPACE] and not self.attacking and not self.defending and not self.using_special:
            self.attacking = True
            self.attack_frame = 0
        
        if self.attacking:
            self.attack_frame += 1
            
            # Check for hit at the middle of the animation
            if self.attack_frame == self.attack_frame_max // 2 and opponent:
                if self.is_in_range(opponent, 100):  # Attack range
                    damage = self.calculate_attack_damage()
                    opponent.take_damage(damage)
            
            # End attack animation
            if self.attack_frame >= self.attack_frame_max:
                self.attacking = False
    
    def defend(self, keys):
        """Perform defense"""
        if self.is_opponent:
            return
        
        self.defending = keys[pygame.K_x] and not self.attacking and not self.using_special
    
    def use_special(self, keys, opponent):
        """Use special ability"""
        if self.is_opponent:
            return
        
        if keys[pygame.K_z] and not self.attacking and not self.defending and not self.using_special and self.special_cooldown == 0:
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
            
            actual_defense = self.defense_power * defense_multiplier
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
            self.health = min(100, self.health + 20)
        else:
            # Other buffs are added to active_buffs
            self.active_buffs.append(buff)
    
    def update_buffs(self):
        """Update buff durations and remove expired buffs"""
        for buff in self.active_buffs[:]:
            buff.duration -= 1
            if buff.duration <= 0:
                self.active_buffs.remove(buff)
    
    def update(self, keys, opponent, buffs):
        """Update character state"""
        if not self.is_opponent:
            self.move(keys)
            self.attack(keys, opponent)
            self.defend(keys)
            self.use_special(keys, opponent)
        
        # Update cooldowns
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
            attack_indicator = pygame.Surface((30, 10))
            attack_indicator.fill((255, 255, 0))
            sprite.blit(attack_indicator, (10, 0))
        
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
        health_percentage = self.health / 100
        
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y - 10, health_bar_width, health_bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 10, health_bar_width * health_percentage, health_bar_height))
        
        # Draw name
        font = pygame.font.Font(None, 24)
        name_surface = font.render(self.name, True, (255, 255, 255))
        screen.blit(name_surface, (self.x, self.y - 30))
        
        # Draw character sprite
        screen.blit(sprite, (self.x, self.y))


class Fighter(Character):
    def __init__(self, x, y, name, is_opponent=False):
        super().__init__(x, y, name, is_opponent)
        self.color = (220, 100, 100)  # Reddish
        self.attack_power = 15  # Stronger attack
        self.defense_power = 8  # Better defense
        self.speed = 4  # Slightly slower
        
        # Visual representation
        self.sprite = pygame.Surface((self.width, self.height))
        self.sprite.fill(self.color)
    
    def special_ability(self, opponent):
        """Fighter's special ability: Strong blow that does double damage"""
        if opponent and self.is_in_range(opponent, 120):
            damage = self.calculate_attack_damage() * 2
            opponent.take_damage(damage)
            self.using_special = False


class Mage(Character):
    def __init__(self, x, y, name, is_opponent=False):
        super().__init__(x, y, name, is_opponent)
        self.color = (100, 100, 220)  # Bluish
        self.attack_power = 8  # Weaker attack
        self.defense_power = 5  # Weaker defense
        self.speed = 5  # Average speed
        self.special_range = 200  # Longer range for special ability
        
        # Visual representation
        self.sprite = pygame.Surface((self.width, self.height))
        self.sprite.fill(self.color)
    
    def special_ability(self, opponent):
        """Mage's special ability: Blind opponent temporarily (slow them down)"""
        if opponent and self.is_in_range(opponent, self.special_range):
            # Create a speed debuff for the opponent
            opponent.speed = 2  # Slow down the opponent
            
            # Set a timer to restore speed after 3 seconds
            pygame.time.set_timer(pygame.USEREVENT, 3000)
            
            # This event will be handled in the game loop to restore speed
            def restore_speed():
                opponent.speed = 5
            
            pygame.time.set_timer(pygame.USEREVENT, 3000, 1)  # Once only
        
        self.using_special = False


class Archer(Character):
    def __init__(self, x, y, name, is_opponent=False):
        super().__init__(x, y, name, is_opponent)
        self.color = (100, 220, 100)  # Greenish
        self.attack_power = 12  # Medium attack
        self.defense_power = 3  # Weak defense
        self.speed = 6  # Fast
        self.special_range = 250  # Long range for special ability
        
        # Visual representation
        self.sprite = pygame.Surface((self.width, self.height))
        self.sprite.fill(self.color)
    
    def special_ability(self, opponent):
        """Archer's special ability: Steal a random buff from opponent"""
        if opponent and self.is_in_range(opponent, self.special_range):
            if opponent.active_buffs:
                # Take a random buff from opponent
                stolen_buff_index = random.randint(0, len(opponent.active_buffs) - 1)
                stolen_buff = opponent.active_buffs.pop(stolen_buff_index)
                
                # Add it to our own buffs
                self.add_buff(stolen_buff)
        
        self.using_special = False 