import pygame
from entities.characters import Fighter, Mage, Rogue

class HUD:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.tiny_font = pygame.font.Font(None, 20)
        self.load_assets()
    
    def load_assets(self):
        """Carrega todos os assets do HUD"""
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
    
    def load_character_portrait(self, character_type):
        """Carrega o retrato do personagem"""
        try:
            image_path = f"./imagens_characters/PNG/{character_type}/frame_{character_type.lower()}.png"
            image = pygame.image.load(image_path).convert_alpha()
            return pygame.transform.scale(image, (80, 80))
        except Exception as e:
            print(f"Error loading portrait for {character_type}: {str(e)}")
            return None
    
    def draw(self):
        """Desenha todo o HUD"""
        # Draw time remaining
        minutes = self.game.current_time // (60 * 60)
        seconds = (self.game.current_time // 60) % 60
        time_text = f"Tempo: {minutes:02d}:{seconds:02d}"
        time_surface = self.font.render(time_text, True, (255, 255, 255))
        time_x = self.screen.get_width()//2 - time_surface.get_width()//2
        self.screen.blit(time_surface, (time_x, 20))
        
        # Draw level info below time
        level_text = f"Nível {self.game.level_manager.current_level + 1}/5"
        level_surface = self.font.render(level_text, True, (255, 255, 0))
        level_x = self.screen.get_width()//2 - level_surface.get_width()//2
        self.screen.blit(level_surface, (level_x, 60))
        
        # Draw player HUDs
        if self.hp_bar and self.mp_bar and self.heart_image:
            # Player 1 HUD (left side)
            self.draw_player_hud(
                self.game.player1,
                10,  # x position
                10,  # y position
                False  # not flipped
            )
            
            # Player 2 HUD (right side)
            self.draw_player_hud(
                self.game.player2,
                self.screen.get_width() - 310,  # x position
                10,  # y position
                True  # flipped
            )
        
        # Draw damage percentages
        self.draw_damage_percentage(self.game.player1)
        self.draw_damage_percentage(self.game.player2)
    
    def draw_player_hud(self, player, x, y, flip):
        """Desenha os elementos do HUD para um jogador"""
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
        elif isinstance(player, Rogue):
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
        lives_to_show = self.game.player1_lives if player == self.game.player1 else self.game.player2_lives
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
    
    def draw_controls_guide(self):
        """Desenha o guia de controles com novas habilidades"""
        # Create semi-transparent overlay for controls
        controls_surface = pygame.Surface((250, 800))  # Increased height from 400 to 600
        controls_surface.fill((0, 0, 0))
        controls_surface.set_alpha(self.game.controls_alpha)
        
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
            player = self.game.player1 if player_num == 1 else self.game.player2
            
            # Header with player class name
            class_name = "Cavaleiro" if isinstance(player, Fighter) else "Mago" if isinstance(player, Mage) else "Assasino"
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
            
            elif isinstance(player, Rogue):
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
        x_pos = 10 if self.game.controls_position == "left" else self.screen.get_width() - 260
        self.screen.blit(controls_surface, (x_pos, 40))  # Moved up to 80 from 200
    
    def draw_game_over(self):
        """Desenha a tela de fim de jogo"""
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(180)  # Mais opaco para melhor legibilidade
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Título "Fim de Jogo"
        title_text = self.font.render("FIM DE JOGO", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 100))
        self.screen.blit(title_text, title_rect)
        
        # Texto do vencedor
        if self.game.winner == "Empate! Um pombo roubou a Queijada!":
            text = self.game.winner
            color = (255, 255, 0)
        else:
            text = f"{self.game.winner} conquistou a Queijada!"
            color = (0, 255, 0)
        
        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 40))
        self.screen.blit(text_surface, text_rect)
        
        # Placar final
        score_text = self.font.render(
            f"Placar Final: {self.game.player1_name} {self.game.level_manager.player1_wins} x {self.game.level_manager.player2_wins} {self.game.player2_name}", 
            True, (255, 255, 255)
        )
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