import pygame
import sys
import random
import math
from game import Game

# Initialize Pygame
pygame.init()

# Set up the display
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 820
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
        self.font = pygame.font.Font(None, 48)  # Larger main font
        self.title_font = pygame.font.Font(None, 72)  # New font for title
        self.small_font = pygame.font.Font(None, 24)
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Menu states
        self.current_state = "intro"  # States: intro, character_select, controls
        self.intro_alpha = 0  # For fade effect
        self.fade_in = True
        
        # Story text
        self.story_text = [
            "Em uma terra distante de Portugal...",
            "Uma lendária Queijada de Sintra foi criada com poderes místicos.",
            "Dizem que quem a provar terá poderes inimagináveis...",
            "Três guerreiros se apresentam para o desafio:",
            "",
            "O Cavaleiro de Óbidos",
            "O Mago de Tomar",
            "O Arqueiro de Sagres",
            "",
            "Pressione ESPAÇO para começar a batalha!"
        ]
        
        # Player selection
        self.player1_name = "Jogador 1"
        self.player2_name = "Jogador 2"
        self.player1_class = 0  # 0: Fighter, 1: Mage, 2: Archer
        self.player2_class = 0
        
        # Class descriptions with more lore
        self.class_descriptions = {
            0: "Cavaleiro de Óbidos: Treinado nas muralhas do castelo, domina a arte do combate próximo",
            1: "Mago de Tomar: Guardião dos segredos dos Templários, mestre das artes arcanas",
            2: "Arqueiro de Sagres: Discípulo da escola de navegação, preciso como as estrelas"
        }
        
        # Load character preview images
        self.class_icons = {
            0: self.load_character_preview("Knight"),    # Fighter/Knight
            1: self.load_character_preview("Mage"),      # Mage
            2: self.load_character_preview("Rogue")      # Archer/Rogue
        }
        
        try:
            self.menu_background = pygame.image.load("./imagens_background/menu_background.png").convert()
            self.menu_background = pygame.transform.scale(self.menu_background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            self.menu_background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.menu_background.fill((30, 30, 50))  # Darker blue-ish background
    
    def load_character_preview(self, character_type):
        """Load and scale character preview image from idle animation"""
        try:
            # Try to load the first frame of the idle animation
            base_path = "./imagens_characters/PNG"
            character_path = f"{base_path}/{character_type}/Idle"
            
            # Print debug info
            print(f"Trying to load character from: {character_path}")
            
            # List available files
            import os
            if os.path.exists(character_path):
                files = sorted([f for f in os.listdir(character_path) if f.endswith('.png')])
                if files:
                    image_path = os.path.join(character_path, files[0])
                    print(f"Loading image from: {image_path}")
                    image = pygame.image.load(image_path).convert_alpha()
                    # Scale the image to be larger for preview
                    scaled_image = pygame.transform.scale(image, (200, 200))  # Made preview bigger
                    return scaled_image
                else:
                    print(f"No PNG files found in {character_path}")
            else:
                print(f"Directory not found: {character_path}")
            
            raise FileNotFoundError(f"Could not load character preview for {character_type}")
            
        except Exception as e:
            print(f"Error loading {character_type} preview: {str(e)}")
            # Fallback to colored rectangle if image fails to load
            icon = pygame.Surface((200, 200))  # Made fallback bigger too
            icon.fill(RED if character_type == "Knight" else BLUE if character_type == "Mage" else GREEN)
            return icon
    
    def draw_button(self, text, x, y, width, height, color, hover=False):
        """Draw a stylized button and return its rect"""
        button_rect = pygame.Rect(x, y, width, height)
        
        # Draw button shadow
        shadow_rect = pygame.Rect(x + 3, y + 3, width, height)
        pygame.draw.rect(self.screen, (0, 0, 0, 128), shadow_rect)
        
        # Draw main button
        pygame.draw.rect(self.screen, color, button_rect)
        if hover:
            pygame.draw.rect(self.screen, WHITE, button_rect, 3)
        else:
            pygame.draw.rect(self.screen, BLACK, button_rect, 2)
        
        # Draw text with shadow
        text_surface = self.font.render(text, True, BLACK)
        text_shadow = self.font.render(text, True, (50, 50, 50))
        text_rect = text_surface.get_rect(center=button_rect.center)
        self.screen.blit(text_shadow, (text_rect.x + 2, text_rect.y + 2))
        self.screen.blit(text_surface, text_rect)
        return button_rect
    
    def draw_intro(self):
        """Draw the story intro screen"""
        # Draw background
        self.screen.blit(self.menu_background, (0, 0))
        
        # Create semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        self.screen.blit(overlay, (0, 0))
        
        # Draw title
        title = self.title_font.render("Batalha pela Queijada", True, (255, 215, 0))  # Golden color
        title_shadow = self.title_font.render("Batalha pela Queijada", True, (100, 84, 0))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title_shadow, (title_rect.x + 3, title_rect.y + 3))
        self.screen.blit(title, title_rect)
        
        # Draw story text with fade effect
        for i, line in enumerate(self.story_text):
            text_surface = self.small_font.render(line, True, WHITE)
            text_surface.set_alpha(self.intro_alpha)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 200 + i * 30))
            self.screen.blit(text_surface, text_rect)
        
        # Update fade effect
        if self.fade_in:
            self.intro_alpha = min(255, self.intro_alpha + 3)
        
        # Draw "Press SPACE" with pulsing effect
        if self.intro_alpha >= 255:
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 255
            space_text = self.font.render("Pressione ESPAÇO", True, (pulse, pulse, pulse))
            space_rect = space_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
            self.screen.blit(space_text, space_rect)
    
    def draw_character_select(self):
        """Draw the character selection screen"""
        # Draw background
        self.screen.blit(self.menu_background, (0, 0))
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(150)
        self.screen.blit(overlay, (0, 0))
        
        # Calculate dynamic spacing
        vertical_space = SCREEN_HEIGHT - 150  # Reduced space reserve
        section_height = vertical_space // 4  # Divide space in 4 sections for better distribution
        
        # Draw title at the top
        title = self.title_font.render("Escolha seu Guerreiro", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 60))  # Fixed position for title
        self.screen.blit(title, title_rect)
        
        # Draw player selections in their own sections with adjusted spacing
        player1_y = section_height + 80  # Moved up
        player2_y = section_height * 2 + 80  # More space between players
        
        # Draw player selections
        self.player1_buttons = self.draw_class_selection(1, player1_y, self.player1_class)
        self.player2_buttons = self.draw_class_selection(2, player2_y, self.player2_class)
        
        # Draw start button at the bottom
        self.start_button = self.draw_button(
            "Começar Batalha", 
            SCREEN_WIDTH // 2 - 150,
            SCREEN_HEIGHT - 80,
            300, 50,
            (255, 215, 0),  # Golden color
            self.start_button.collidepoint(pygame.mouse.get_pos()) if hasattr(self, 'start_button') else False
        )
    
    def draw_class_selection(self, player_num, y_pos, current_class):
        """Draw class selection for a player with icons and descriptions"""
        # Calculate dynamic sizes and spacing
        content_width = SCREEN_WIDTH * 0.7  # Reduced from 0.8 to 0.7
        margin_x = (SCREEN_WIDTH - content_width) // 2
        
        # Calculate button and spacing dimensions based on content width
        button_width = int(content_width * 0.15)  # Reduced from 0.2 to 0.15
        button_height = 40  # Fixed height instead of proportional
        spacing = (content_width - (button_width * 3)) // 4
        
        # Player title with golden trim
        title = self.font.render(f"Jogador {player_num}", True, (255, 215, 0))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, y_pos - 30))  # Reduced spacing
        self.screen.blit(title, title_rect)
        
        buttons = []
        classes = ["Cavaleiro", "Mago", "Arqueiro"]
        colors = [(200, 50, 50), (50, 50, 200), (50, 200, 50)]
        
        # Calculate preview image size
        preview_size = 140  # Fixed size instead of proportional
        
        for i, (class_name, color) in enumerate(zip(classes, colors)):
            # Calculate position for this character
            x_pos = margin_x + spacing + (i * (button_width + spacing))
            
            # Highlight selected class
            if i == current_class:
                color = tuple(min(c + 100, 255) for c in color)
            
            # Draw character preview image
            icon = self.class_icons[i]
            scaled_icon = pygame.transform.scale(icon, (preview_size, preview_size))
            icon_rect = scaled_icon.get_rect(center=(x_pos + button_width//2, y_pos))
            self.screen.blit(scaled_icon, icon_rect)
            
            # Draw selection border if selected
            if i == current_class:
                border_rect = icon_rect.inflate(8, 8)
                pygame.draw.rect(self.screen, (255, 215, 0), border_rect, 4)
            
            # Draw button below preview
            button_y = y_pos + preview_size//2 + 10  # Reduced spacing
            button = self.draw_button(
                class_name,
                x_pos,
                button_y,
                button_width,
                button_height,
                color
            )
            buttons.append(button)
        
        # Draw class description centered below buttons
        desc = self.small_font.render(self.class_descriptions[current_class], True, WHITE)
        desc_rect = desc.get_rect(center=(SCREEN_WIDTH // 2, y_pos + preview_size//2 + button_height + 40))
        self.screen.blit(desc, desc_rect)
        
        return buttons
    
    def run(self):
        """Run the menu"""
        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.current_state == "intro":
                        self.current_state = "character_select"
                
                if event.type == pygame.MOUSEBUTTONDOWN and self.current_state == "character_select":
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
            
            # Draw current menu state
            if self.current_state == "intro":
                self.draw_intro()
            elif self.current_state == "character_select":
                self.draw_character_select()
            
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