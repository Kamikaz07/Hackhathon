import pygame
import sys
import random
import math
from characters import Character, Fighter, Mage, Archer
from buff import Buff
from buff_manager import BuffManager

class Game:
    def __init__(self, screen, player1_class, player2_class, player1_name, player2_name, level_manager):
        self.screen = screen
        self.level_manager = level_manager
        # Get screen dimensions from the screen surface
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.tiny_font = pygame.font.Font(None, 20)  # New font for controls display
        
        # Game settings
        self.fps = 60
        self.round_time = 360 * 60  # 1 minute per round
        self.current_time = self.round_time
        self.game_over = False
        self.winner = None
        self.respawn_delay = 120  # 2 seconds for respawn
        self.respawn_timer = 0
        
        # Controls guide
        self.show_controls = True
        self.controls_alpha = 128  # Semi-transparent
        self.controls_fade_timer = 600  # 10 seconds before starting to fade
        self.controls_position = "left"  # Can be "left" or "right"
        
        # Game state
        self.player1_class = player1_class
        self.player2_class = player2_class
        self.player1_name = player1_name
        self.player2_name = player2_name
        self.player1_lives = 3
        self.player2_lives = 3
        
        # Load HUD assets
        self.load_hud_assets()
        
        # Initialize first round with full lives
        self.initialize_round()

        # Initialize buff manager with screen dimensions
        self.buff_manager = BuffManager(self.screen_width, self.screen_height)
    
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
        else:  # Archer
            player = Archer(x, y, name, is_player2)
        
        player.lives = lives
        return player
    
    def load_hud_assets(self):
        """Load all HUD assets"""
        hud_base = "./imagens_characters/SirLobo_Pack_HUD_2021_ONLY_PNG/HUD/Modulated/8"
        try:
            self.hp_bar = pygame.image.load(f"{hud_base}/hp_bar.png").convert_alpha()
            self.hp_bar = pygame.transform.scale(self.hp_bar, (200, 10))
            
            self.mp_bar = pygame.image.load(f"{hud_base}/mp_bar.png").convert_alpha()
            self.mp_bar = pygame.transform.scale(self.mp_bar, (200, 10))
            
            # Load heart image
            self.heart_image = pygame.image.load("./imagens_characters/heart.png").convert_alpha()
            self.heart_image = pygame.transform.scale(self.heart_image, (15, 15))
            
            # Load character portraits
            self.portraits = {
                "Knight": self.load_character_portrait("Knight"),
                "Mage": self.load_character_portrait("Mage"),
                "Rogue": self.load_character_portrait("Rogue")
            }
        except Exception as e:
            print(f"Error loading HUD assets: {str(e)}")
            self.hp_bar = None
            self.mp_bar = None
            self.heart_image = None
            self.portraits = {}
    
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
                if player.y > 800:  # If player falls off screen
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
        
        # Check if either player is defeated (percentage too high)
        if self.game_started and (self.player1.health >= self.player1.max_health or self.player2.health >= self.player2.max_health):
            self.round_over = True
            self.determine_round_winner()

        self.buff_manager.update([self.player1, self.player2])
    
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
            text = self.font.render(f"Começando em {countdown}...", True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
            self.screen.blit(text, text_rect)
        
        # Draw players
        self.player1.draw(self.screen)
        self.player2.draw(self.screen)
        
        # Draw HUD
        self.draw_hud()
        
        # Draw time remaining
        minutes = self.current_time // (60 * 60)
        seconds = (self.current_time // 60) % 60
        time_text = f"Tempo: {minutes:02d}:{seconds:02d}"
        time_surface = self.font.render(time_text, True, (255, 255, 255))
        time_x = self.screen.get_width()//2 - time_surface.get_width()//2
        self.screen.blit(time_surface, (time_x, 20))
        
        # Draw level info below time
        level_text = f"Nível {self.level_manager.current_level + 1}/5"
        level_surface = self.font.render(level_text, True, (255, 255, 0))
        level_x = self.screen.get_width()//2 - level_surface.get_width()//2
        self.screen.blit(level_surface, (level_x, 60))
        
        # Draw game over screen if game is over
        if self.game_over:
            self.draw_game_over()
        
        # Draw controls guide if enabled
        if self.show_controls:
            self.draw_controls_guide()

        self.buff_manager.draw(self.screen)
        
        pygame.display.flip()
    
    def draw_damage_percentage(self, player):
        """Desenha a porcentagem de dano e o nome acima do jogador"""
        # Cores baseadas na porcentagem de dano (verde para baixo, vermelho para alto)
        damage_pct = player.health / player.max_health if player.max_health > 0 else 0
        # Cor gradiente de verde para vermelho baseado no dano
        r = min(255, int(255 * damage_pct * 2))
        g = min(255, int(255 * (1 - damage_pct)))
        color = (r, g, 0)
        
        # Renderiza o texto com a porcentagem de dano (sem fundo)
        damage_text = self.small_font.render(f"{int(player.health)}%", True, color)
        
        # Renderiza o nome do jogador
        name_text = self.small_font.render(f"{player.name}", True, (255, 255, 255))
        
        # Posiciona o texto acima do jogador
        damage_x = player.rect.centerx - damage_text.get_width() // 2
        damage_y = player.rect.y - damage_text.get_height() - 10  # 10 pixels acima do jogador
        
        # Posiciona o nome acima da porcentagem
        name_x = player.rect.centerx - name_text.get_width() // 2
        name_y = damage_y - name_text.get_height() - 5  # 5 pixels acima da porcentagem
        
        # Desenha os textos (sem fundo)
        self.screen.blit(name_text, (name_x, name_y))
        self.screen.blit(damage_text, (damage_x, damage_y))
    
    def draw_hud(self):
        """Draw heads-up display"""
        # Draw time remaining
        minutes = self.current_time // (60 * 60)
        seconds = (self.current_time // 60) % 60
        time_text = f"Tempo: {minutes:02d}:{seconds:02d}"
        time_surface = self.font.render(time_text, True, (255, 255, 255))
        self.screen.blit(time_surface, (self.screen.get_width()//2 - time_surface.get_width()//2, 20))
        
        # Draw HUD for each player if assets loaded successfully
        if self.hp_bar and self.mp_bar and self.heart_image:
            # Player 1 HUD (left side)
            self.draw_player_hud(
                self.player1,
                10,  # x position
                10,  # y position
                False  # not flipped
            )
            
            # Player 2 HUD (right side)
            self.draw_player_hud(
                self.player2,
                self.screen.get_width() - 310,  # x position (adjusted for new width)
                10,  # y position
                True  # flipped
            )
    
    def draw_player_hud(self, player, x, y, flip):
        """Draw HUD elements for a player"""
        # Get character type and portrait
        char_type = "Knight" if isinstance(player, Fighter) else "Mage" if isinstance(player, Mage) else "Rogue"
        portrait = self.portraits.get(char_type)
        
        # Draw player name
        name_x = x + (10 if flip else 10)
        name_surface = self.small_font.render(player.name, True, (255, 255, 255))
        self.screen.blit(name_surface, (name_x, y + 15))
        
        # Draw percentage
        percentage_text = f"{int(player.health)}%"
        percentage_color = (255, max(0, 255 - (player.health * 1.5)), max(0, 255 - (player.health * 1.5)))
        percentage_surface = self.small_font.render(percentage_text, True, percentage_color)
        percentage_x = x + (10 if flip else 10)
        self.screen.blit(percentage_surface, (percentage_x, y + 35))
        
        # Calculate bar positions
        bar_x = x + (10 if flip else 10)
        hp_y = y + 55
        mp_y = y + 75
        
        # Draw HP bar
        hp_width = int((1 - player.health/player.max_health) * 200)  # Reduzido para 200px
        if hp_width > 0:
            hp_rect = pygame.Rect(bar_x, hp_y, hp_width, 10)  # Altura reduzida para 10px
            hp_surf = pygame.transform.chop(self.hp_bar, (hp_width, 0, 200-hp_width, 0))
            self.screen.blit(hp_surf, hp_rect)
        
        # Draw MP/Stamina/Energy bar
        mp_bar_scaled = pygame.transform.scale(self.mp_bar, (200, 10))  # Redimensionado para 200x10
        self.screen.blit(mp_bar_scaled, (bar_x, mp_y))
        
        # Desenha nível atual de mana/stamina/energy
        mp_level = 0
        if isinstance(player, Mage):
            mp_level = (player.mana / player.max_mana) * 200
            mp_color = (0, 100, 255)  # Azul para mana
        elif isinstance(player, Fighter):
            mp_level = (player.stamina / player.max_stamina) * 200
            mp_color = (255, 255, 0)  # Amarelo para stamina
        elif isinstance(player, Archer):
            mp_level = (player.energy / player.max_energy) * 200
            mp_color = (0, 255, 0)  # Verde para energia
        else:
            mp_level = 0  # Para outros personagens
        
        if mp_level > 0:
            pygame.draw.rect(self.screen, mp_color, (bar_x, mp_y, mp_level, 10))
        
        # Draw hearts for lives
        heart_start_x = x + (10 if flip else 10)
        heart_y = y + 90
        
        # Usar as vidas do Game em vez das vidas do player
        lives_to_show = self.player1_lives if player == self.player1 else self.player2_lives
        for i in range(lives_to_show):
            heart_x = heart_start_x + (i * 20)  # Reduzido espaçamento para 20px
            self.screen.blit(self.heart_image, (heart_x, heart_y))
        
        # Draw character portrait on the right
        if portrait:
            portrait_x = x + (200 if flip else 200)  # Moved to the right
            portrait_y = y + 10
            portrait_size = 80
            portrait_flipped = pygame.transform.flip(portrait, flip, False)
            self.screen.blit(portrait_flipped, (portrait_x, portrait_y))
    
    def draw_game_over(self):
        """Draw game over screen"""
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(180)  # Mais opaco para melhor legibilidade
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Título "Fim de Jogo"
        title_text = self.font.render("FIM DE JOGO", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 100))
        self.screen.blit(title_text, title_rect)
        
        # Texto do vencedor
        if self.winner == "Empate! Um pombo roubou a Queijada!":
            text = self.winner
            color = (255, 255, 0)
        else:
            text = f"{self.winner} conquistou a Queijada!"
            color = (0, 255, 0)
        
        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 40))
        self.screen.blit(text_surface, text_rect)
        
        # Placar final
        score_text = self.font.render(f"Placar Final: {self.player1_name} {self.level_manager.player1_wins} x {self.level_manager.player2_wins} {self.player2_name}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 20))
        self.screen.blit(score_text, score_rect)
        
        # Texto adicional sobre o fim do jogo
        completed_text = self.small_font.render("Todos os 5 níveis foram completados!", True, (255, 255, 255))
        completed_rect = completed_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 60))
        self.screen.blit(completed_text, completed_rect)
        
        # Instrução para voltar ao menu
        instruction = self.small_font.render("Pressione ESC para voltar ao menu", True, (255, 255, 255))
        instruction_rect = instruction.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 100))
        self.screen.blit(instruction, instruction_rect)
    
    def draw_controls_guide(self):
        """Draw the controls guide with new abilities"""
        # Create semi-transparent overlay for controls
        controls_surface = pygame.Surface((250, 800))  # Increased height from 400 to 600
        controls_surface.fill((0, 0, 0))
        controls_surface.set_alpha(self.controls_alpha)
        
        # Calculate positions
        margin = 10
        line_height = 18  # Slightly reduced line height
        y = margin
        
        # Helper function to draw text
        def draw_control_line(text, y_pos, color=(255, 255, 255)):
            text_surface = self.tiny_font.render(text, True, color)
            controls_surface.blit(text_surface, (margin, y_pos))
            return y_pos + line_height
        
        # Draw toggle instructions
        y = draw_control_line("TAB: Mostrar/Ocultar Controles", y, (255, 255, 0))
        y = draw_control_line("C: Mudar Posição dos Controles", y, (255, 255, 0))
        y = draw_control_line("", y)  # Spacing
        
        # Draw controls for each player
        for player_num in range(1, 3):
            player = self.player1 if player_num == 1 else self.player2
            
            # Header with player class name
            class_name = "Cavaleiro" if isinstance(player, Fighter) else "Mago" if isinstance(player, Mage) else "Arqueiro"
            y = draw_control_line(f"Jogador {player_num} - {class_name}:", y, (255, 215, 0))
            
            # Movement
            controls = {
                "Movimento": "WASD" if player_num == 1 else "Setas",
                "Ataque": "F" if player_num == 1 else "K",
                "Defesa": "G" if player_num == 1 else "L",
                "Especial": "H" if player_num == 1 else "M"
            }
            
            for action, key in controls.items():
                y = draw_control_line(f"{action}: {key}", y)
            
            # Special abilities based on character class
            y = draw_control_line("", y)  # Spacing
            
            if isinstance(player, Fighter):
                y = draw_control_line("Habilidades do Cavaleiro:", y, (200, 200, 200))
                y = draw_control_line("- Segurar Ataque: Golpe Carregado", y)
                y = draw_control_line("  (Mais dano e knockback)", y, (150, 150, 150))
                y = draw_control_line("- Defesa + Ataque: Empurrão", y)
                y = draw_control_line("  (Causa stun no inimigo)", y, (150, 150, 150))
                y = draw_control_line("- Defesa (timing): Bloqueio Perfeito", y)
                y = draw_control_line("  (0 dano e ganha stamina)", y, (150, 150, 150))
                y = draw_control_line("- Especial no ar: Ataque Descendente", y)
                y = draw_control_line("  (Dano em área)", y, (150, 150, 150))
                y = draw_control_line("- Especial no chão: Uppercut", y)
                y = draw_control_line("  (Lança inimigo para cima)", y, (150, 150, 150))
                y = draw_control_line("- Barra amarela: Stamina", y)
                y = draw_control_line("  (Regenera ao não usar)", y, (150, 150, 150))
            
            elif isinstance(player, Mage):
                y = draw_control_line("Habilidades do Mago:", y, (100, 100, 255))
                y = draw_control_line("- Ataque: Projétil de Fogo", y)
                y = draw_control_line("  (Dano à distância)", y, (75, 75, 200))
                y = draw_control_line("- Especial: Explosão de Fogo", y)
                y = draw_control_line("  (Grande dano em área)", y, (75, 75, 200))
                y = draw_control_line("- Defesa: Teleporte", y)
                y = draw_control_line("  (Escapa rapidamente)", y, (75, 75, 200))
                y = draw_control_line("- Segurar Cima: Levitação", y)
                y = draw_control_line("  (Controle aéreo)", y, (75, 75, 200))
                y = draw_control_line("- Barra azul: Mana", y)
                y = draw_control_line("  (Regenera com tempo)", y, (75, 75, 200))
            
            elif isinstance(player, Archer):
                y = draw_control_line("Habilidades do Arqueiro:", y, (100, 255, 100))
                y = draw_control_line("- Ataque: Combo de 3 Golpes", y)
                y = draw_control_line("  (Dano crescente)", y, (75, 200, 75))
                y = draw_control_line("- Ataque + Movimento: Ataque Rápido", y)
                y = draw_control_line("  (Golpes enquanto corre)", y, (75, 200, 75))
                y = draw_control_line("- Especial: Dash Attack (25 energia)", y)
                y = draw_control_line("  (Avanço com dano)", y, (75, 200, 75))
                y = draw_control_line("- Defesa: Empurrão (15 energia)", y)
                y = draw_control_line("  (Cria distância)", y, (75, 200, 75))
                y = draw_control_line("- Pulo Duplo (10 energia)", y)
                y = draw_control_line("  (Melhor mobilidade)", y, (75, 200, 75))
                y = draw_control_line("- Velocidade Aumentada", y)
                y = draw_control_line("  (Mais rápido que outros)", y, (75, 200, 75))
                y = draw_control_line("- Barra verde: Energia", y)
                y = draw_control_line("  (Regenera com tempo)", y, (75, 200, 75))
            
            y += margin  # Add space between players
        
        # Draw the controls surface on the chosen side
        x_pos = 10 if self.controls_position == "left" else self.screen.get_width() - 260
        self.screen.blit(controls_surface, (x_pos, 40))  # Moved up to 80 from 200
    
    def load_character_portrait(self, character_type):
        """Load character portrait from frames_ image"""
        try:
            # First try to load the character preview image
            image_path = f"./imagens_characters/PNG/{character_type}/frame_{character_type.lower()}.png"
            image = pygame.image.load(image_path).convert_alpha()
            return pygame.transform.scale(image, (80, 80))
        except Exception as e:
            print(f"Error loading portrait for {character_type}: {str(e)}")
            return None
    
    def load_platform_images(self):
        """Carrega as imagens das plataformas"""
        platform_images = {}
        try:
            # Carrega a imagem da plataforma de pedra
            platform = pygame.image.load("./imagens_background/barra_castanha.png").convert_alpha()
            
            # Redimensiona as imagens para o tamanho correto
            platform_images["large"] = pygame.transform.scale(platform, (500, 40))
            platform_images["small"] = pygame.transform.scale(platform, (150, 40))
            
        except Exception as e:
            print(f"Erro ao carregar imagens das plataformas: {str(e)}")
            # Cria superfícies de fallback caso as imagens não sejam carregadas
            platform_images["large"] = self.create_fallback_platform(500, 40)
            platform_images["small"] = self.create_fallback_platform(150, 40)
            
        return platform_images
    
    def create_fallback_platform(self, width, height):
        """Cria uma imagem de plataforma de fallback caso as imagens não carreguem"""
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        # Desenha um retângulo com cor de madeira
        pygame.draw.rect(surface, (139, 69, 19), pygame.Rect(0, 0, width, height))
        # Adiciona alguns detalhes para parecer madeira
        for i in range(0, width, 30):
            pygame.draw.line(surface, (101, 67, 33), (i, 0), (i, height), 2)
        # Adiciona borda
        pygame.draw.rect(surface, (101, 67, 33), pygame.Rect(0, 0, width, height), 3)
        return surface
    
    def run(self):
        """Run the game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)