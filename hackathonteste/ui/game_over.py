import pygame

class GameOver:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
    
    def draw(self):
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