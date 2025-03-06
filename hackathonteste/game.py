import pygame
import sys
import random
from characters import Fighter, Mage, Archer
from buff import Buff

class Game:
    def __init__(self, screen, player1_class, player1_name, player2_class, player2_name, level, background):
        self.screen = screen
        self.level = level
        self.background = background
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game state
        self.player1 = self.create_player(player1_class, player1_name, is_player2=False)
        self.player2 = self.create_player(player2_class, player2_name, is_player2=True)
        self.buffs = []  # Available buffs on the field
        self.game_started = False
        self.start_delay = 180  # 3 seconds delay before game starts
        
        # Generate initial buffs
        self.generate_buffs(3)
        
        # Game settings
        self.fps = 60
        self.round_time = 60 * 60  # 1 minute per round
        self.current_time = self.round_time
        self.game_over = False
        self.winner = None
    
    def create_player(self, class_id, name, is_player2=False):
        """Create a player based on the selected class"""
        x = 100 if not is_player2 else 700
        y = 300
        
        if class_id == 0:  # Fighter
            return Fighter(x, y, name, is_player2)
        elif class_id == 1:  # Mage
            return Mage(x, y, name, is_player2)
        else:  # Archer
            return Archer(x, y, name, is_player2)
    
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
            
            if self.game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return
    
    def update(self):
        """Update game state"""
        if self.game_over:
            return
            
        # Handle start delay
        if not self.game_started:
            if self.start_delay > 0:
                self.start_delay -= 1
                return
            else:
                self.game_started = True
        
        # Update timer only if game has started
        if self.game_started and self.current_time > 0:
            self.current_time -= 1
        elif self.game_started and self.current_time <= 0:
            self.game_over = True
            # Determine winner based on health
            if self.player1.health > self.player2.health:
                self.winner = self.player1.name
            elif self.player2.health > self.player1.health:
                self.winner = self.player2.name
            else:
                self.winner = "Empate! Um pombo roubou a Queijada!"
        
        # Get input for both players
        keys = pygame.key.get_pressed()
        
        # Update players
        if self.game_started:
            # Player 1 controls (WASD + F/G/H)
            player1_controls = {
                "left": keys[pygame.K_a],
                "right": keys[pygame.K_d],
                "up": keys[pygame.K_w],
                "down": keys[pygame.K_s],
                "attack": keys[pygame.K_f],
                "defend": keys[pygame.K_g],
                "special": keys[pygame.K_h]
            }
            
            # Player 2 controls (Arrow keys + K/L/M)
            player2_controls = {
                "left": keys[pygame.K_LEFT],
                "right": keys[pygame.K_RIGHT],
                "up": keys[pygame.K_UP],
                "down": keys[pygame.K_DOWN],
                "attack": keys[pygame.K_k],
                "defend": keys[pygame.K_l],
                "special": keys[pygame.K_m]
            }
            
            # Update players
            self.player1.update_local(player1_controls, self.player2, self.buffs)
            self.player2.update_local(player2_controls, self.player1, self.buffs)
            
            # Check for collisions with buffs
            for buff in self.buffs[:]:
                if buff.collides_with(self.player1):
                    self.player1.add_buff(buff)
                    self.buffs.remove(buff)
                elif buff.collides_with(self.player2):
                    self.player2.add_buff(buff)
                    self.buffs.remove(buff)
            
            # Generate new buffs occasionally
            if random.random() < 0.005 and len(self.buffs) < 5:  # 0.5% chance per frame
                self.generate_buffs(1)
        
        # Check if either player is defeated
        if self.game_started and (self.player1.health <= 0 or self.player2.health <= 0):
            self.game_over = True
            if self.player1.health <= 0:
                self.winner = self.player2.name
            else:
                self.winner = self.player1.name
    
    def draw(self):
        """Draw everything to the screen"""
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw start countdown
        if not self.game_started:
            countdown = (self.start_delay // 60) + 1
            text = self.font.render(f"Começando em {countdown}...", True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
            self.screen.blit(text, text_rect)
            
            # Draw controls
            controls1 = self.small_font.render("Jogador 1: WASD (movimento) F (ataque) G (defesa) H (especial)", True, (255, 255, 255))
            controls2 = self.small_font.render("Jogador 2: Setas (movimento) K (ataque) L (defesa) M (especial)", True, (255, 255, 255))
            self.screen.blit(controls1, (50, 500))
            self.screen.blit(controls2, (50, 530))
        
        # Draw players
        self.player1.draw(self.screen)
        self.player2.draw(self.screen)
        
        # Draw buffs
        for buff in self.buffs:
            buff.draw(self.screen)
        
        # Draw HUD
        self.draw_hud()
        
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
        
        # Draw player1 health and buffs
        health_text = f"{self.player1.name}: {self.player1.health}"
        health_surface = self.font.render(health_text, True, (255, 255, 255))
        self.screen.blit(health_surface, (50, 20))
        
        # Draw player1 active buffs
        y_offset = 50
        for buff in self.player1.active_buffs:
            buff_text = f"{buff.buff_type.capitalize()}: {buff.duration // 60}s"
            buff_surface = self.small_font.render(buff_text, True, (255, 255, 0))
            self.screen.blit(buff_surface, (50, y_offset))
            y_offset += 20
        
        # Draw player2 health and buffs
        health_text = f"{self.player2.name}: {self.player2.health}"
        health_surface = self.font.render(health_text, True, (255, 255, 255))
        self.screen.blit(health_surface, (550, 20))
        
        # Draw player2 active buffs
        y_offset = 50
        for buff in self.player2.active_buffs:
            buff_text = f"{buff.buff_type.capitalize()}: {buff.duration // 60}s"
            buff_surface = self.small_font.render(buff_text, True, (255, 255, 0))
            self.screen.blit(buff_surface, (550, y_offset))
            y_offset += 20
    
    def draw_game_over(self):
        """Draw game over screen"""
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        if self.winner == "Empate! Um pombo roubou a Queijada!":
            text = self.winner
            color = (255, 255, 0)
        else:
            text = f"{self.winner} conquistou a Queijada!"
            color = (0, 255, 0)
        
        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
        self.screen.blit(text_surface, text_rect)
        
        instruction = self.small_font.render("Pressione ESC para voltar ao menu", True, (255, 255, 255))
        instruction_rect = instruction.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 50))
        self.screen.blit(instruction, instruction_rect)
    
    def run(self):
        """Run the game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps) 