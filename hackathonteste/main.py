import pygame
import sys
from core.level_manager import LevelManager
from core.game_core import Game

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 72)
        
        # Menu state
        self.state = "main"  # main, character_select, controls, credits
        
        # Character selection
        self.player1_class = 0  # 0: Fighter, 1: Mage, 2: Archer
        self.player2_class = 0
        self.player1_name = "Jogador 1"
        self.player2_name = "Jogador 2"
        
        # Character preview images
        self.character_images = self.load_character_images()
        
        # Background
        self.background = self.load_background()
    
    def load_background(self):
        try:
            bg = pygame.image.load("./imagens_background/menu_bg.png").convert()
            return pygame.transform.scale(bg, (self.screen.get_width(), self.screen.get_height()))
        except:
            # Fallback background
            bg = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
            bg.fill((50, 50, 100))
            return bg
    
    def load_character_images(self):
        images = []
        character_types = ["Knight", "Mage", "Rogue"]
        
        for char_type in character_types:
            try:
                image_path = f"./imagens_characters/PNG/{char_type}/frame_{char_type.lower()}.png"
                image = pygame.image.load(image_path).convert_alpha()
                images.append(pygame.transform.scale(image, (150, 150)))
            except:
                # Fallback image
                img = pygame.Surface((150, 150))
                img.fill((200, 200, 200))
                images.append(img)
        
        return images
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == "main":
                        self.running = False
                    else:
                        self.state = "main"
                
                if self.state == "main":
                    if event.key == pygame.K_RETURN:
                        self.state = "character_select"
                    elif event.key == pygame.K_c:
                        self.state = "controls"
                    elif event.key == pygame.K_q:
                        self.running = False
                
                elif self.state == "character_select":
                    if event.key == pygame.K_LEFT:
                        self.player1_class = (self.player1_class - 1) % 3
                    elif event.key == pygame.K_RIGHT:
                        self.player1_class = (self.player1_class + 1) % 3
                    elif event.key == pygame.K_a:
                        self.player2_class = (self.player2_class - 1) % 3
                    elif event.key == pygame.K_d:
                        self.player2_class = (self.player2_class + 1) % 3
                    elif event.key == pygame.K_RETURN:
                        return self.start_game()
    
    def draw(self):
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        if self.state == "main":
            self.draw_main_menu()
        elif self.state == "character_select":
            self.draw_character_select()
        elif self.state == "controls":
            self.draw_controls()
        
        pygame.display.flip()
    
    def draw_main_menu(self):
        # Draw title
        title = self.title_font.render("Batalha pela Queijada", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen.get_width() // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Draw menu options
        options = [
            ("Pressione ENTER para jogar", (255, 255, 255)),
            ("Pressione C para ver controles", (200, 200, 200)),
            ("Pressione Q para sair", (200, 200, 200))
        ]
        
        for i, (text, color) in enumerate(options):
            option = self.font.render(text, True, color)
            option_rect = option.get_rect(center=(self.screen.get_width() // 2, 250 + i * 50))
            self.screen.blit(option, option_rect)
    
    def draw_character_select(self):
        # Draw title
        title = self.font.render("Selecione os Personagens", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen.get_width() // 2, 50))
        self.screen.blit(title, title_rect)
        
        # Draw player 1 selection
        p1_text = self.font.render("Jogador 1 (Setas)", True, (255, 255, 255))
        p1_rect = p1_text.get_rect(center=(self.screen.get_width() // 4, 100))
        self.screen.blit(p1_text, p1_rect)
        
        # Draw player 2 selection
        p2_text = self.font.render("Jogador 2 (A/D)", True, (255, 255, 255))
        p2_rect = p2_text.get_rect(center=(self.screen.get_width() * 3 // 4, 100))
        self.screen.blit(p2_text, p2_rect)
        
        # Draw character images
        self.screen.blit(self.character_images[self.player1_class], 
                         (self.screen.get_width() // 4 - 75, 150))
        self.screen.blit(self.character_images[self.player2_class], 
                         (self.screen.get_width() * 3 // 4 - 75, 150))
        
        # Draw character names
        char_names = ["Cavaleiro", "Mago", "Arqueiro"]
        
        p1_char = self.font.render(char_names[self.player1_class], True, (255, 255, 255))
        p1_char_rect = p1_char.get_rect(center=(self.screen.get_width() // 4, 320))
        self.screen.blit(p1_char, p1_char_rect)
        
        p2_char = self.font.render(char_names[self.player2_class], True, (255, 255, 255))
        p2_char_rect = p2_char.get_rect(center=(self.screen.get_width() * 3 // 4, 320))
        self.screen.blit(p2_char, p2_char_rect)
        
        # Draw start instruction
        start_text = self.font.render("Pressione ENTER para iniciar", True, (255, 255, 0))
        start_rect = start_text.get_rect(center=(self.screen.get_width() // 2, 400))
        self.screen.blit(start_text, start_rect)
    
    def draw_controls(self):
        # Draw title
        title = self.font.render("Controles", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen.get_width() // 2, 50))
        self.screen.blit(title, title_rect)
        
        # Draw controls for player 1
        p1_text = self.font.render("Jogador 1", True, (255, 255, 255))
        p1_rect = p1_text.get_rect(center=(self.screen.get_width() // 4, 100))
        self.screen.blit(p1_text, p1_rect)
        
        p1_controls = [
            "Movimento: WASD",
            "Ataque: F",
            "Defesa: G",
            "Especial: H"
        ]
        
        for i, control in enumerate(p1_controls):
            text = self.small_font.render(control, True, (200, 200, 200))
            rect = text.get_rect(center=(self.screen.get_width() // 4, 150 + i * 30))
            self.screen.blit(text, rect)
        
        # Draw controls for player 2
        p2_text = self.font.render("Jogador 2", True, (255, 255, 255))
        p2_rect = p2_text.get_rect(center=(self.screen.get_width() * 3 // 4, 100))
        self.screen.blit(p2_text, p2_rect)
        
        p2_controls = [
            "Movimento: Setas",
            "Ataque: K",
            "Defesa: L",
            "Especial: M"
        ]
        
        for i, control in enumerate(p2_controls):
            text = self.small_font.render(control, True, (200, 200, 200))
            rect = text.get_rect(center=(self.screen.get_width() * 3 // 4, 150 + i * 30))
            self.screen.blit(text, rect)
        
        # Draw back instruction
        back_text = self.font.render("Pressione ESC para voltar", True, (255, 255, 0))
        back_rect = back_text.get_rect(center=(self.screen.get_width() // 2, 400))
        self.screen.blit(back_text, back_rect)
    
    def start_game(self):
        """Inicia o jogo com os personagens selecionados"""
        level_manager = LevelManager()
        game = Game(
            self.screen,
            self.player1_class,
            self.player2_class,
            self.player1_name,
            self.player2_name,
            level_manager
        )
        game.run()
        return True
    
    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            pygame.time.delay(30)

def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Batalha pela Queijada")
    
    menu = Menu(screen)
    menu.run()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 