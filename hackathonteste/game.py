import pygame
import sys
import random
from characters import Fighter, Mage, Archer
from buff import Buff

class Game:
    def __init__(self, screen, network, player_class, player_name, level, background):
        self.screen = screen
        self.network = network
        self.player_class = player_class
        self.player_name = player_name
        self.level = level
        self.background = background
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.easter_egg_triggered = False
        self.easter_egg_timer = 0
        
        # Game state
        self.player = self.create_player(player_class, player_name, is_opponent=False)
        self.opponent = None
        self.buffs = []  # Available buffs on the field
        
        # Generate initial buffs
        self.generate_buffs(3)
        
        # Game settings
        self.fps = 60
        self.round_time = 60 * 3  # 3 minutes per round
        self.current_time = self.round_time
        self.game_over = False
        self.winner = None
    
    def create_player(self, class_id, name, is_opponent=False):
        """Create a player based on the selected class"""
        x = 100 if not is_opponent else 700
        y = 300
        
        if class_id == 0:  # Fighter
            return Fighter(x, y, name, is_opponent)
        elif class_id == 1:  # Mage
            return Mage(x, y, name, is_opponent)
        else:  # Archer
            return Archer(x, y, name, is_opponent)
    
    def generate_buffs(self, count):
        """Generate random buffs on the field"""
        buff_types = ["health", "attack", "defense", "speed"]
        
        for _ in range(count):
            buff_type = random.choice(buff_types)
            x = random.randint(100, 700)
            y = random.randint(100, 500)
            duration = random.randint(5, 15) * 60  # 5-15 seconds in frames
            self.buffs.append(Buff(x, y, buff_type, duration))
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            
            # Check for Easter Egg key combo (press keys "T", "M" in sequence)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    self.easter_egg_sequence = 1
                elif event.key == pygame.K_m and self.easter_egg_sequence == 1:
                    self.easter_egg_sequence = 2
                elif event.key == pygame.K_u and self.easter_egg_sequence == 2:
                    self.trigger_easter_egg()
                else:
                    self.easter_egg_sequence = 0
    
    def trigger_easter_egg(self):
        """Trigger the Three Musketeers Easter Egg"""
        self.easter_egg_triggered = True
        self.easter_egg_timer = 5 * 60  # Display for 5 seconds
    
    def update(self):
        """Update game state"""
        if self.game_over:
            return
        
        # Update timer
        if self.current_time > 0:
            self.current_time -= 1
        else:
            self.game_over = True
            # Determine winner based on health
            if self.player.health > self.opponent.health:
                self.winner = self.player_name
            elif self.opponent.health > self.player.health:
                self.winner = self.opponent.name
            else:
                self.winner = "Empate! Um pombo roubou a Queijada!"
        
        # Get input
        keys = pygame.key.get_pressed()
        
        # Update player
        self.player.update(keys, self.opponent, self.buffs)
        
        # Send player data to server
        player_data = {
            "x": self.player.x,
            "y": self.player.y,
            "health": self.player.health,
            "attacking": self.player.attacking,
            "defending": self.player.defending,
            "using_special": self.player.using_special,
            "direction": self.player.direction,
            "buffs": [b.to_dict() for b in self.player.active_buffs]
        }
        
        # Send data to server and get opponent data
        opponent_data = self.network.send(player_data)
        
        if opponent_data and not self.opponent:
            # First time we receive opponent data, create opponent
            self.opponent = self.create_player(
                opponent_data.get("class", 0),
                opponent_data.get("name", "Opponent"),
                is_opponent=True
            )
        
        # Update opponent with received data
        if self.opponent and opponent_data:
            self.opponent.x = opponent_data.get("x", self.opponent.x)
            self.opponent.y = opponent_data.get("y", self.opponent.y)
            self.opponent.health = opponent_data.get("health", self.opponent.health)
            self.opponent.attacking = opponent_data.get("attacking", False)
            self.opponent.defending = opponent_data.get("defending", False)
            self.opponent.using_special = opponent_data.get("using_special", False)
            self.opponent.direction = opponent_data.get("direction", self.opponent.direction)
            
            # Update opponent buffs
            self.opponent.active_buffs = []
            for buff_data in opponent_data.get("buffs", []):
                self.opponent.active_buffs.append(Buff.from_dict(buff_data))
        
        # Check for collisions with buffs
        for buff in self.buffs[:]:
            if buff.collides_with(self.player):
                self.player.add_buff(buff)
                self.buffs.remove(buff)
        
        # Generate new buffs occasionally
        if random.random() < 0.005 and len(self.buffs) < 5:  # 0.5% chance per frame
            self.generate_buffs(1)
        
        # Check if either player is defeated
        if self.player.health <= 0 or self.opponent and self.opponent.health <= 0:
            self.game_over = True
            if self.player.health <= 0:
                self.winner = self.opponent.name if self.opponent else "Oponente"
            else:
                self.winner = self.player_name
        
        # Update Easter Egg timer
        if self.easter_egg_triggered and self.easter_egg_timer > 0:
            self.easter_egg_timer -= 1
        elif self.easter_egg_triggered:
            self.easter_egg_triggered = False
    
    def draw(self):
        """Draw everything to the screen"""
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw players
        self.player.draw(self.screen)
        if self.opponent:
            self.opponent.draw(self.screen)
        
        # Draw buffs
        for buff in self.buffs:
            buff.draw(self.screen)
        
        # Draw HUD
        self.draw_hud()
        
        # Draw Easter Egg if triggered
        if self.easter_egg_triggered:
            self.draw_easter_egg()
        
        # Draw game over screen if game is over
        if self.game_over:
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_hud(self):
        """Draw heads-up display"""
        # Draw time remaining
        minutes = self.current_time // (60 * 60)
        seconds = (self.current_time // 60) % 60
        time_text = f"Tempo: {minutes:02d}:{seconds:02d}"
        time_surface = self.font.render(time_text, True, (255, 255, 255))
        self.screen.blit(time_surface, (350, 20))
        
        # Draw player health
        health_text = f"{self.player_name}: {self.player.health}"
        health_surface = self.font.render(health_text, True, (255, 255, 255))
        self.screen.blit(health_surface, (50, 20))
        
        # Draw player active buffs
        y_offset = 50
        for buff in self.player.active_buffs:
            buff_text = f"{buff.buff_type.capitalize()}: {buff.duration // 60}s"
            buff_surface = self.small_font.render(buff_text, True, (255, 255, 0))
            self.screen.blit(buff_surface, (50, y_offset))
            y_offset += 20
        
        # Draw opponent health if opponent exists
        if self.opponent:
            opp_health_text = f"{self.opponent.name}: {self.opponent.health}"
            opp_health_surface = self.font.render(opp_health_text, True, (255, 255, 255))
            self.screen.blit(opp_health_surface, (550, 20))
    
    def draw_easter_egg(self):
        """Draw the Three Musketeers Easter Egg"""
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        text = self.font.render("Os Três Mosqueteiros aparecem!", True, (255, 255, 255))
        text2 = self.font.render("Todos por um e um por todos!", True, (255, 255, 255))
        
        # Center the text
        text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 20))
        text2_rect = text2.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 20))
        
        self.screen.blit(text, text_rect)
        self.screen.blit(text2, text2_rect)
    
    def draw_game_over(self):
        """Draw game over screen"""
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.font.render("Fim de Jogo!", True, (255, 255, 255))
        winner_text = self.font.render(f"Vencedor: {self.winner}", True, (255, 255, 255))
        queijada_text = self.font.render("A Queijada Real é sua!", True, (255, 255, 0))
        
        # Center the text
        game_over_rect = game_over_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 40))
        winner_rect = winner_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
        queijada_rect = queijada_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 40))
        
        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(winner_text, winner_rect)
        
        # Only show this if there's a clear winner (not a tie)
        if "Empate" not in self.winner and "pombo" not in self.winner:
            self.screen.blit(queijada_text, queijada_rect)
    
    def run(self):
        """Run the game loop"""
        self.easter_egg_sequence = 0
        
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps) 