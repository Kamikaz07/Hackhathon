import pygame
import sys
import random
from entities.characters import Fighter, Mage, Rogue

from ui.hud import HUD
from ui.game_over import GameOver

class Game:
    def __init__(self, screen, player1_class, player2_class, player1_name, player2_name, level_manager):
        self.screen = screen
        self.level_manager = level_manager
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game settings
        self.fps = 60
        self.round_time = 360 * 60  # 1 minuto por round
        self.current_time = self.round_time
        self.game_over = False
        self.winner = None
        self.respawn_delay = 120  # 2 segundos para respawn
        self.respawn_timer = 0
        
        # Controls guide
        self.show_controls = True
        self.controls_alpha = 128  # Semi-transparent
        self.controls_fade_timer = 600  # 10 segundos antes de começar a desaparecer
        self.controls_position = "left"  # Pode ser "left" ou "right"
        
        # Game state
        self.player1_class = player1_class
        self.player2_class = player2_class
        self.player1_name = player1_name
        self.player2_name = player2_name
        self.player1_lives = 3
        self.player2_lives = 3
        
        # Componentes
        self.hud = HUD(self)
        self.game_over_screen = GameOver(self)
        
        # Initialize first round with full lives
        self.initialize_round()
    
    def initialize_round(self):
        """Initialize or reset the round state"""
        # Get spawn points from current level
        spawn_points = self.level_manager.get_spawn_points()
        
        # Create players at spawn points with current lives
        self.player1 = self.create_player(self.player1_class, self.player1_name, spawn_points[0], self.player1_lives, is_player2=False)
        self.player2 = self.create_player(self.player2_class, self.player2_name, spawn_points[1], self.player2_lives, is_player2=True)
        
        # Reset round-specific variables
        self.game_started = False
        self.start_delay = 180  # 3 seconds delay before round starts
        self.current_time = self.round_time
        self.round_over = False
        
        # Get platforms from current level
        self.platforms = self.level_manager.get_platforms()
    
    def create_player(self, class_id, name, spawn_point, lives, is_player2=False):
        """Create a player based on the selected class at the spawn point"""
        x, y = spawn_point
        
        if class_id == 0:  # Fighter
            player = Fighter(x, y, name, is_player2)
        elif class_id == 1:  # Mage
            player = Mage(x, y, name, is_player2)
        else:  #
            player = Rogue(x, y, name, is_player2)
        
        player.lives = lives
        return player
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and self.game_over:
                    self.running = False
                    return
                # Toggle controls visibility with Tab
                elif event.key == pygame.K_TAB:
                    self.show_controls = not self.show_controls
                # Switch controls position with C key
                elif event.key == pygame.K_c:
                    self.controls_position = "right" if self.controls_position == "left" else "left"
    
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
            # Tempo acabou, determina o vencedor com base no dano atual
            self.determine_round_winner()
            return
        
        # Get input for both players
        keys = pygame.key.get_pressed()
        
        # Update players
        if self.game_started:
            # Check for out of bounds
            for player in [self.player1, self.player2]:
                if player.y > 700:  # Reduzido de 800 para 700 para corresponder às novas posições das plataformas
                    if player == self.player1:
                        self.player1_lives -= 1
                        player.lives = self.player1_lives
                    else:
                        self.player2_lives -= 1
                        player.lives = self.player2_lives
                    
                    # Reposiciona o jogador se ainda tiver vidas
                    if (player == self.player1 and self.player1_lives > 0) or (player == self.player2 and self.player2_lives > 0):
                        spawn_points = self.level_manager.get_spawn_points()
                        if player == self.player1:
                            player.x, player.y = spawn_points[0]
                        else:
                            player.x, player.y = spawn_points[1]
                        player.rect.x, player.rect.y = player.x, player.y
                        player.velocity_y = 0
                        player.health = 0  # Reseta o dano ao respawnar
                    
                    # Verifica se algum jogador ficou sem vidas
                    if self.player1_lives <= 0 or self.player2_lives <= 0:
                        self.determine_round_winner()
                        return

            # Verifica se algum jogador atingiu o limite de dano
            if self.player1.health >= self.player1.max_health:
                self.player1_lives -= 1
                if self.player1_lives <= 0:
                    self.determine_round_winner()
                    return
                else:
                    # Respawn com uma vida a menos
                    spawn_points = self.level_manager.get_spawn_points()
                    self.player1.x, self.player1.y = spawn_points[0]
                    self.player1.rect.x, self.player1.rect.y = self.player1.x, self.player1.y
                    self.player1.velocity_y = 0
                    self.player1.health = 0
            
            if self.player2.health >= self.player2.max_health:
                self.player2_lives -= 1
                if self.player2_lives <= 0:
                    self.determine_round_winner()
                    return
                else:
                    # Respawn com uma vida a menos
                    spawn_points = self.level_manager.get_spawn_points()
                    self.player2.x, self.player2.y = spawn_points[1]
                    self.player2.rect.x, self.player2.rect.y = self.player2.x, self.player2.y
                    self.player2.velocity_y = 0
                    self.player2.health = 0
 
            # Player controls
            player1_controls = {
                "left": keys[pygame.K_a],
                "right": keys[pygame.K_d],
                "up": keys[pygame.K_w],
                "down": keys[pygame.K_s],
                "attack": keys[pygame.K_f],
                "defend": keys[pygame.K_g],
                "special": keys[pygame.K_h]
            }
            
            player2_controls = {
                "left": keys[pygame.K_LEFT],
                "right": keys[pygame.K_RIGHT],
                "up": keys[pygame.K_UP],
                "down": keys[pygame.K_DOWN],
                "attack": keys[pygame.K_k],
                "defend": keys[pygame.K_l],
                "special": keys[pygame.K_m]
            }
            
            # Update players with platform collision
            self.player1.update_local(player1_controls, self.player2, [], self.platforms)
            self.player2.update_local(player2_controls, self.player1, [], self.platforms)
    
    def determine_round_winner(self):
        """Determina o vencedor do nível atual e avança para o próximo"""
        # Determina o vencedor com base nas vidas restantes ou na porcentagem de dano
        if self.player1_lives <= 0:
            # Player 2 vence porque player 1 ficou sem vidas
            level_winner = 2
            self.level_manager.player2_wins += 1
        elif self.player2_lives <= 0:
            # Player 1 vence porque player 2 ficou sem vidas
            level_winner = 1
            self.level_manager.player1_wins += 1
        else:
            # Ambos ainda têm vidas, então compara a porcentagem de dano
            if self.player1.health < self.player2.health:
                level_winner = 1
                self.level_manager.player1_wins += 1
            elif self.player2.health < self.player1.health:
                level_winner = 2
                self.level_manager.player2_wins += 1
            else:
                # Empate, escolhe aleatoriamente
                level_winner = random.choice([1, 2])
                if level_winner == 1:
                    self.level_manager.player1_wins += 1
                else:
                    self.level_manager.player2_wins += 1
        
        # Avança para o próximo nível
        self.level_manager.current_level += 1
        
        # Verifica se o jogo acabou (todos os níveis completados)
        if self.level_manager.current_level >= 5:  # Termina após o 5º nível
            self.game_over = True
            # Determina o vencedor final com base no número total de vitórias
            if self.level_manager.player1_wins > self.level_manager.player2_wins:
                self.winner = self.player1_name
            elif self.level_manager.player2_wins > self.level_manager.player1_wins:
                self.winner = self.player2_name
            else:
                self.winner = "Empate! Um pombo roubou a Queijada!"
        else:
            # Reseta as vidas para o próximo nível
            self.player1_lives = 3
            self.player2_lives = 3
            self.initialize_round()
    
    def draw(self):
        """Draw everything to the screen"""
        # Draw current level
        current_level = self.level_manager.get_current_level()
        current_level.draw(self.screen)
        
        # Draw platforms
        for platform in self.platforms:
            # Desenha a imagem da plataforma em vez de um retângulo simples
            self.screen.blit(platform.image, platform.rect)
        
        # Draw start countdown
        if not self.game_started:
            countdown = (self.start_delay // 60) + 1
            text = self.hud.font.render(f"Começando em {countdown}...", True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
            self.screen.blit(text, text_rect)
        
        # Draw players
        self.player1.draw(self.screen)
        self.player2.draw(self.screen)
        
        # Draw HUD
        self.hud.draw()
        
        # Draw controls guide if enabled
        if self.show_controls:
            self.hud.draw_controls_guide()
        
        # Draw game over screen if game is over
        if self.game_over:
            self.game_over_screen.draw()
        
        pygame.display.flip()
    
    def run(self):
        """Run the game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps) 