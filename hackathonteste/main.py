import pygame
import sys
import random
from game import Game

# Initialize Pygame
pygame.init()

# Set up the display
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Batalha pela Queijada")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Load background
try:
    background = pygame.image.load("./imagens_background/background.png").convert()
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
except:
    # Fallback to a colored background if image fails to load
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background.fill((50, 50, 50))

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Player selection
        self.player1_name = "Jogador 1"
        self.player2_name = "Jogador 2"
        self.player1_class = 0  # 0: Fighter, 1: Mage, 2: Archer
        self.player2_class = 0
        
        # Class descriptions
        self.class_descriptions = {
            0: "Lutador: Alto dano corpo a corpo, muita vida",
            1: "Mago: Dano mágico à distância, pouca vida",
            2: "Arqueiro: Dano físico à distância, vida média"
        }
    
    def draw_button(self, text, x, y, width, height, color, hover=False):
        """Draw a button and return its rect"""
        button_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, color, button_rect)
        if hover:
            pygame.draw.rect(self.screen, WHITE, button_rect, 3)
        else:
            pygame.draw.rect(self.screen, BLACK, button_rect, 2)
        
        text_surface = self.font.render(text, True, BLACK)
        text_rect = text_surface.get_rect(center=button_rect.center)
        self.screen.blit(text_surface, text_rect)
        return button_rect
    
    def draw_class_selection(self, player_num, x, y, current_class):
        """Draw class selection for a player"""
        # Player title
        title = self.font.render(f"Jogador {player_num}", True, WHITE)
        self.screen.blit(title, (x, y))
        
        # Class buttons
        button_width = 120
        button_height = 40
        button_spacing = 20
        
        classes = ["Lutador", "Mago", "Arqueiro"]
        buttons = []
        
        for i, class_name in enumerate(classes):
            color = RED if i == 0 else BLUE if i == 1 else GREEN
            if i == current_class:
                color = (min(color[0] + 100, 255), min(color[1] + 100, 255), min(color[2] + 100, 255))
            
            button_x = x + i * (button_width + button_spacing)
            button_y = y + 50
            button = self.draw_button(class_name, button_x, button_y, button_width, button_height, color)
            buttons.append(button)
        
        # Draw class description
        desc = self.small_font.render(self.class_descriptions[current_class], True, WHITE)
        self.screen.blit(desc, (x, y + 120))
        
        return buttons
    
    def run(self):
        """Run the menu"""
        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Player 1 class selection
                    for i, button in enumerate(self.player1_buttons):
                        if button.collidepoint(mouse_pos):
                            self.player1_class = i
                    
                    # Player 2 class selection
                    for i, button in enumerate(self.player2_buttons):
                        if button.collidepoint(mouse_pos):
                            self.player2_class = i
                    
                    # Start game button
                    if self.start_button.collidepoint(mouse_pos):
                        return self.start_game()
            
            # Draw menu
            self.screen.fill(BLACK)
            
            # Title
            title = self.font.render("Batalha pela Queijada", True, WHITE)
            title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
            self.screen.blit(title, title_rect)
            
            # Player 1 selection
            self.player1_buttons = self.draw_class_selection(1, 50, 150, self.player1_class)
            
            # Player 2 selection
            self.player2_buttons = self.draw_class_selection(2, 50, 300, self.player2_class)
            
            # Start button
            self.start_button = self.draw_button(
                "Começar Jogo", 
                SCREEN_WIDTH // 2 - 100,
                SCREEN_HEIGHT - 100,
                200, 50,
                (0, 255, 0),
                self.start_button.collidepoint(mouse_pos) if hasattr(self, 'start_button') else False
            )
            
            pygame.display.flip()
            self.clock.tick(60)
    
    def start_game(self):
        """Start the game with selected options"""
        game = Game(
            screen=self.screen,
            player1_class=self.player1_class,
            player1_name=self.player1_name,
            player2_class=self.player2_class,
            player2_name=self.player2_name,
            level=0,
            background=background
        )
        game.run()

def main():
    while True:
        menu = Menu(screen)
        menu.run()

if __name__ == "__main__":
    main() 