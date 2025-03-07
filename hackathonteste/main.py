import pygame
import sys
import random
import math
from game import Game
import json
import os
from PIL import Image
import io

# Initialize Pygame and Pygame Mixer
pygame.init()
pygame.mixer.init()

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
GOLD = (255, 215, 0)

class GifBackground:
    def __init__(self, gif_path, size):
        self.frames = []
        self.current_frame = 0
        self.frame_timer = 0
        self.size = size
        
        try:
            # Open and load the GIF
            gif = Image.open(gif_path)
            
            # Get frame duration (in milliseconds)
            self.frame_duration = gif.info.get('duration', 100)  # Default to 100ms if not specified
            
            # Convert frame duration to seconds for pygame
            self.frame_duration = self.frame_duration / 1000.0
            
            # Load all frames
            for frame_index in range(gif.n_frames):
                gif.seek(frame_index)
                # Convert to RGBA if necessary
                if gif.mode != 'RGBA':
                    frame = gif.convert('RGBA')
                else:
                    frame = gif
                
                # Convert PIL image to pygame surface
                frame_str = frame.tobytes()
                frame_size = frame.size
                py_frame = pygame.image.fromstring(frame_str, frame_size, 'RGBA')
                
                # Scale the frame
                py_frame = pygame.transform.scale(py_frame, size)
                self.frames.append(py_frame)
            
        except Exception as e:
            print(f"Error loading GIF background: {str(e)}")
            # Create a fallback surface
            fallback = pygame.Surface(size)
            fallback.fill((30, 30, 50))
            self.frames = [fallback]
            self.frame_duration = 0.1
    
    def update(self, dt):
        """Update the current frame based on elapsed time"""
        self.frame_timer += dt
        if self.frame_timer >= self.frame_duration:
            self.frame_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
    
    def get_current_frame(self):
        """Return the current frame surface"""
        return self.frames[self.current_frame]

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 48)
        self.title_font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 24)
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Menu states
        self.current_state = "main_menu"  # States: main_menu, intro, character_select, options, rankings
        self.intro_alpha = 0
        self.fade_in = True
        self.transition_alpha = 0
        self.transitioning_to = None
        
        # Load and play background music
        try:
            pygame.mixer.music.load("./imagens_background/menu_music.mp3")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)  # Loop indefinitely
        except:
            print("Could not load menu music")
        
        # Load sound effects
        self.sounds = {
            "select": self.load_sound("select.wav"),
            "confirm": self.load_sound("confirm.wav"),
            "back": self.load_sound("back.wav"),
            "hover": self.load_sound("hover.wav")
        }
        
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
        self.player1_class = 0
        self.player2_class = 0
        
        # Options
        self.load_options()
        
        # Rankings
        self.load_rankings()
        
        # Menu buttons
        self.main_menu_buttons = [
            ("Jogar", lambda: self.transition_to("intro")),
            ("Opções", lambda: self.transition_to("options")),
            ("Rankings", lambda: self.transition_to("rankings")),
            ("Sair", lambda: self.quit_game())
        ]
        
        # Class descriptions
        self.class_descriptions = {
            0: "Cavaleiro de Óbidos: Treinado nas muralhas do castelo, domina a arte do combate próximo",
            1: "Mago de Tomar: Guardião dos segredos dos Templários, mestre das artes arcanas",
            2: "Arqueiro de Sagres: Discípulo da escola de navegação, preciso como as estrelas"
        }
        
        # Load character preview images
        self.class_icons = {
            0: self.load_character_preview("Knight"),
            1: self.load_character_preview("Mage"),
            2: self.load_character_preview("Rogue")
        }
        
        # Load animated background
        try:
            self.menu_background = GifBackground("./imagens_background/menu.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            print("Could not load animated background, trying static background...")
            try:
                static_bg = pygame.image.load("./imagens_background/menu_background.png").convert()
                self.menu_background = GifBackground("", (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.menu_background.frames = [pygame.transform.scale(static_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))]
            except:
                print("Using fallback background color")
                fallback = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                fallback.fill((30, 30, 50))
                self.menu_background = GifBackground("", (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.menu_background.frames = [fallback]

    def load_sound(self, filename):
        """Load a sound effect"""
        try:
            sound = pygame.mixer.Sound(f"./imagens_background/sounds/{filename}")
            sound.set_volume(0.3)
            return sound
        except:
            print(f"Could not load sound: {filename}")
            return None

    def load_options(self):
        """Load game options from file"""
        self.options = {
            "music_volume": 0.5,
            "sound_volume": 0.3,
            "fullscreen": False,
            "show_fps": False
        }
        
        try:
            with open("options.json", "r") as f:
                self.options.update(json.load(f))
        except:
            self.save_options()

    def save_options(self):
        """Save game options to file"""
        try:
            with open("options.json", "w") as f:
                json.dump(self.options, f)
        except:
            print("Could not save options")

    def load_rankings(self):
        """Load rankings from file"""
        self.rankings = []
        try:
            with open("rankings.json", "r") as f:
                self.rankings = json.load(f)
        except:
            self.save_rankings()

    def save_rankings(self):
        """Save rankings to file"""
        try:
            with open("rankings.json", "w") as f:
                json.dump(self.rankings, f)
        except:
            print("Could not save rankings")

    def add_ranking(self, winner, loser, winner_class, time):
        """Add a new ranking entry"""
        self.rankings.append({
            "winner": winner,
            "winner_class": winner_class,
            "loser": loser,
            "time": time,
            "date": pygame.time.get_ticks()
        })
        self.rankings.sort(key=lambda x: x["time"])
        self.rankings = self.rankings[:10]  # Keep only top 10
        self.save_rankings()

    def transition_to(self, new_state):
        """Start transition to a new menu state"""
        if self.sounds["confirm"]:
            self.sounds["confirm"].play()
        self.transitioning_to = new_state
        self.fade_in = False

    def update_transition(self):
        """Update menu transition effects"""
        if self.transitioning_to:
            if self.fade_in:
                self.transition_alpha = max(0, self.transition_alpha - 10)
                if self.transition_alpha == 0:
                    self.transitioning_to = None
            else:
                self.transition_alpha = min(255, self.transition_alpha + 10)
                if self.transition_alpha == 255:
                    self.current_state = self.transitioning_to
                    self.fade_in = True

    def draw_transition(self):
        """Draw transition overlay"""
        if self.transition_alpha > 0:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.fill(BLACK)
            overlay.set_alpha(self.transition_alpha)
            self.screen.blit(overlay, (0, 0))

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
        # Update and draw animated background
        self.menu_background.update(self.clock.get_time() / 1000.0)
        self.screen.blit(self.menu_background.get_current_frame(), (0, 0))
        
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
        # Update and draw animated background
        self.menu_background.update(self.clock.get_time() / 1000.0)
        self.screen.blit(self.menu_background.get_current_frame(), (0, 0))
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(150)
        self.screen.blit(overlay, (0, 0))
        
        # Calculate dynamic spacing
        vertical_space = SCREEN_HEIGHT - 150
        
        # Draw title at the top
        title = self.title_font.render("Escolha seu Guerreiro", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 60))
        self.screen.blit(title, title_rect)
        
        # Calculate player sections
        player1_y = 180  # Fixed position for better control
        player2_y = 480  # Fixed position with good separation
        
        # Draw player selections
        self.player1_buttons = self.draw_class_selection(1, player1_y, self.player1_class)
        self.player2_buttons = self.draw_class_selection(2, player2_y, self.player2_class)
        
        # Calculate the actual space needed for each player section (preview + button + description)
        player_section_height = 120 + 40 + 60  # preview_size + button_height + extra_space
        
        # Calculate the divider position to be exactly between the bottom of player 1's section and top of player 2's section
        player1_bottom = player1_y + player_section_height
        player2_top = player2_y - 145  # Subtract the title spacing
        divider_y = (player1_bottom + player2_top) // 2
        
        divider_width = SCREEN_WIDTH * 0.7
        divider_x = (SCREEN_WIDTH - divider_width) // 2
        
        # Draw decorative divider
        pygame.draw.line(self.screen, (255, 215, 0), 
                        (divider_x, divider_y), 
                        (divider_x + divider_width, divider_y), 
                        2)  # Golden line
        
        # Add decorative elements to the divider
        circle_radius = 4
        for x in range(int(divider_x), int(divider_x + divider_width), 100):
            pygame.draw.circle(self.screen, (255, 215, 0), (x, divider_y), circle_radius)
        
        # Draw "VS" text in the middle of the divider
        vs_font = pygame.font.Font(None, 60)
        vs_text = vs_font.render("VS", True, (255, 215, 0))
        vs_rect = vs_text.get_rect(center=(SCREEN_WIDTH // 2, divider_y))
        # Draw shadow for VS text
        vs_shadow = vs_font.render("VS", True, (100, 84, 0))
        self.screen.blit(vs_shadow, (vs_rect.x + 2, vs_rect.y + 2))
        self.screen.blit(vs_text, vs_rect)
        
        # Draw start button at the bottom
        self.start_button = self.draw_button(
            "Começar Batalha", 
            SCREEN_WIDTH // 2 - 150,
            SCREEN_HEIGHT - 80,
            300, 50,
            (255, 215, 0),
            self.start_button.collidepoint(pygame.mouse.get_pos()) if hasattr(self, 'start_button') else False
        )
    
    def draw_class_selection(self, player_num, y_pos, current_class):
        """Draw class selection for a player with icons and descriptions"""
        # Calculate dynamic sizes and spacing
        content_width = SCREEN_WIDTH * 0.7
        margin_x = (SCREEN_WIDTH - content_width) // 2
        
        # Calculate button and spacing dimensions
        button_width = int(content_width * 0.25)
        button_height = 40
        spacing = (content_width - (button_width * 3)) // 4
        
        buttons = []
        classes = ["Cavaleiro", "Mago", "Arqueiro"]
        colors = [(200, 50, 50), (50, 50, 200), (50, 200, 50)]
        
        # Calculate preview image size
        preview_size = 120  # Slightly smaller preview size
        
        for i, (class_name, color) in enumerate(zip(classes, colors)):
            x_pos = margin_x + spacing + (i * (button_width + spacing))
            
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
                
                # Draw player indicator (P1/P2) above the selected character
                player_text = self.font.render(f"P{player_num}", True, (255, 215, 0))
                # Add a black outline/shadow for better visibility
                player_shadow = self.font.render(f"P{player_num}", True, (0, 0, 0))
                text_rect = player_text.get_rect(center=(x_pos + button_width//2, y_pos - preview_size//2 - 20))
                
                # Draw shadow/outline
                for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
                    self.screen.blit(player_shadow, (text_rect.x + dx, text_rect.y + dy))
                # Draw main text
                self.screen.blit(player_text, text_rect)
            
            # Draw button below preview
            button_y = y_pos + preview_size//2 + 10
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
        desc_rect = desc.get_rect(center=(SCREEN_WIDTH // 2, y_pos + preview_size//2 + button_height + 30))
        self.screen.blit(desc, desc_rect)
        
        return buttons
    
    def draw_main_menu(self):
        """Draw the main menu screen"""
        # Update and draw animated background
        self.menu_background.update(self.clock.get_time() / 1000.0)
        self.screen.blit(self.menu_background.get_current_frame(), (0, 0))
        
        # Create semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))
        
        # Draw title with shadow
        title = self.title_font.render("Batalha pela Queijada", True, GOLD)
        title_shadow = self.title_font.render("Batalha pela Queijada", True, (100, 84, 0))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(title_shadow, (title_rect.x + 3, title_rect.y + 3))
        self.screen.blit(title, title_rect)
        
        # Draw menu buttons
        button_y = 300
        mouse_pos = pygame.mouse.get_pos()
        
        for text, action in self.main_menu_buttons:
            button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, button_y, 300, 60)
            hover = button_rect.collidepoint(mouse_pos)
            
            if hover and not hasattr(self, 'last_hover'):
                if self.sounds["hover"]:
                    self.sounds["hover"].play()
                self.last_hover = text
            elif not hover and hasattr(self, 'last_hover') and self.last_hover == text:
                delattr(self, 'last_hover')
            
            # Draw button with shadow
            pygame.draw.rect(self.screen, (0, 0, 0), button_rect.inflate(6, 6))
            pygame.draw.rect(self.screen, GOLD if hover else (200, 200, 200), button_rect)
            
            # Draw text with shadow
            text_surf = self.font.render(text, True, BLACK)
            text_rect = text_surf.get_rect(center=button_rect.center)
            self.screen.blit(text_surf, text_rect)
            
            button_y += 80

    def draw_options(self):
        """Draw the options screen"""
        # Update and draw animated background
        self.menu_background.update(self.clock.get_time() / 1000.0)
        self.screen.blit(self.menu_background.get_current_frame(), (0, 0))
        
        # Create semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))
        
        # Draw title
        title = self.title_font.render("Opções", True, GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(title, title_rect)
        
        # Draw options
        option_y = 250
        mouse_pos = pygame.mouse.get_pos()
        
        # Volume controls
        for text, value in [
            ("Música", "music_volume"),
            ("Sons", "sound_volume")
        ]:
            text_surf = self.font.render(text, True, WHITE)
            text_rect = text_surf.get_rect(midright=(SCREEN_WIDTH // 2 - 50, option_y))
            self.screen.blit(text_surf, text_rect)
            
            # Draw volume slider
            slider_rect = pygame.Rect(SCREEN_WIDTH // 2, option_y, 200, 20)
            pygame.draw.rect(self.screen, (100, 100, 100), slider_rect)
            pygame.draw.rect(self.screen, GOLD, 
                           (slider_rect.x, slider_rect.y, 
                            slider_rect.width * self.options[value], slider_rect.height))
            
            if slider_rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
                self.options[value] = (mouse_pos[0] - slider_rect.x) / slider_rect.width
                self.options[value] = max(0, min(1, self.options[value]))
                
                # Update volumes
                if value == "music_volume":
                    pygame.mixer.music.set_volume(self.options[value])
                else:
                    for sound in self.sounds.values():
                        if sound:
                            sound.set_volume(self.options[value])
            
            option_y += 60
        
        # Toggle options
        for text, value in [
            ("Tela Cheia", "fullscreen"),
            ("Mostrar FPS", "show_fps")
        ]:
            text_surf = self.font.render(text, True, WHITE)
            text_rect = text_surf.get_rect(midright=(SCREEN_WIDTH // 2 - 50, option_y))
            self.screen.blit(text_surf, text_rect)
            
            # Draw toggle button
            toggle_rect = pygame.Rect(SCREEN_WIDTH // 2, option_y, 40, 20)
            pygame.draw.rect(self.screen, GOLD if self.options[value] else (100, 100, 100), toggle_rect)
            pygame.draw.circle(self.screen, WHITE,
                             (toggle_rect.right - 10 if self.options[value] else toggle_rect.left + 10,
                              toggle_rect.centery), 8)
            
            if toggle_rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0] and not hasattr(self, 'toggle_cooldown'):
                self.options[value] = not self.options[value]
                if self.sounds["select"]:
                    self.sounds["select"].play()
                self.toggle_cooldown = pygame.time.get_ticks()
                
                # Apply fullscreen change
                if value == "fullscreen":
                    pygame.display.toggle_fullscreen()
            
            option_y += 60
        
        # Back button
        back_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 50)
        hover = back_rect.collidepoint(mouse_pos)
        pygame.draw.rect(self.screen, GOLD if hover else (200, 200, 200), back_rect)
        
        back_text = self.font.render("Voltar", True, BLACK)
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 75))
        self.screen.blit(back_text, back_rect)
        
        # Handle toggle cooldown
        if hasattr(self, 'toggle_cooldown') and pygame.time.get_ticks() - self.toggle_cooldown > 200:
            delattr(self, 'toggle_cooldown')

    def draw_rankings(self):
        """Draw the rankings screen"""
        # Update and draw animated background
        self.menu_background.update(self.clock.get_time() / 1000.0)
        self.screen.blit(self.menu_background.get_current_frame(), (0, 0))
        
        # Create semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))
        
        # Draw title
        title = self.title_font.render("Rankings", True, GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(title, title_rect)
        
        if not self.rankings:
            # Draw "No rankings yet" message
            text = self.font.render("Nenhum ranking ainda!", True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(text, text_rect)
        else:
            # Draw rankings table
            y = 200
            headers = ["Pos.", "Vencedor", "Classe", "Tempo"]
            x_positions = [SCREEN_WIDTH // 2 - 300, SCREEN_WIDTH // 2 - 150, 
                         SCREEN_WIDTH // 2 + 50, SCREEN_WIDTH // 2 + 200]
            
            # Draw headers
            for header, x in zip(headers, x_positions):
                text = self.font.render(header, True, GOLD)
                text_rect = text.get_rect(midleft=(x, y))
                self.screen.blit(text, text_rect)
            
            y += 40
            
            # Draw entries
            for i, entry in enumerate(self.rankings):
                color = GOLD if i == 0 else WHITE
                
                # Position
                pos_text = self.font.render(f"#{i+1}", True, color)
                self.screen.blit(pos_text, (x_positions[0], y))
                
                # Winner
                winner_text = self.font.render(entry["winner"], True, color)
                self.screen.blit(winner_text, (x_positions[1], y))
                
                # Class
                class_names = ["Cavaleiro", "Mago", "Arqueiro"]
                class_text = self.font.render(class_names[entry["winner_class"]], True, color)
                self.screen.blit(class_text, (x_positions[2], y))
                
                # Time
                minutes = entry["time"] // (60 * 60)
                seconds = (entry["time"] // 60) % 60
                time_text = self.font.render(f"{minutes:02d}:{seconds:02d}", True, color)
                self.screen.blit(time_text, (x_positions[3], y))
                
                y += 40
        
        # Back button
        mouse_pos = pygame.mouse.get_pos()
        back_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 50)
        hover = back_rect.collidepoint(mouse_pos)
        pygame.draw.rect(self.screen, GOLD if hover else (200, 200, 200), back_rect)
        
        back_text = self.font.render("Voltar", True, BLACK)
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 75))
        self.screen.blit(back_text, back_rect)

    def start_game(self):
        """Start a new game with the selected characters"""
        # Stop menu music
        pygame.mixer.music.stop()
        
        # Create new game instance
        game = Game(
            self.screen,
            self.player1_class,
            self.player1_name,
            self.player2_class,
            self.player2_name,
            1,  # Level 1 by default
            self.menu_background.get_current_frame()  # Use menu background for now
        )
        
        # Run the game
        game.run()
        
        # Restart menu music when returning
        try:
            pygame.mixer.music.load("./imagens_background/menu_music.mp3")
            pygame.mixer.music.set_volume(self.options["music_volume"])
            pygame.mixer.music.play(-1)
        except:
            print("Could not reload menu music")
        
        return True  # Return to menu after game ends

    def run(self):
        """Run the menu"""
        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        if self.current_state == "main_menu":
                            button_y = 300
                            for text, action in self.main_menu_buttons:
                                button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, button_y, 300, 60)
                                if button_rect.collidepoint(mouse_pos):
                                    action()
                                button_y += 80
                        
                        elif self.current_state == "options":
                            back_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 50)
                            if back_rect.collidepoint(mouse_pos):
                                self.transition_to("main_menu")
                                self.save_options()
                        
                        elif self.current_state == "rankings":
                            back_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 50)
                            if back_rect.collidepoint(mouse_pos):
                                self.transition_to("main_menu")
                        
                        elif self.current_state == "character_select":
                            # Player 1 class selection
                            for i, button in enumerate(self.player1_buttons):
                                if button.collidepoint(mouse_pos):
                                    if self.sounds["select"]:
                                        self.sounds["select"].play()
                                    self.player1_class = i
                            
                            # Player 2 class selection
                            for i, button in enumerate(self.player2_buttons):
                                if button.collidepoint(mouse_pos):
                                    if self.sounds["select"]:
                                        self.sounds["select"].play()
                                    self.player2_class = i
                            
                            # Start game button
                            if self.start_button.collidepoint(mouse_pos):
                                if self.sounds["confirm"]:
                                    self.sounds["confirm"].play()
                                return self.start_game()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.current_state in ["options", "rankings"]:
                            self.transition_to("main_menu")
                            if self.current_state == "options":
                                self.save_options()
                        elif self.current_state == "main_menu":
                            self.quit_game()
                    
                    elif event.key == pygame.K_SPACE and self.current_state == "intro":
                        self.transition_to("character_select")
            
            # Draw current menu state
            if self.current_state == "main_menu":
                self.draw_main_menu()
            elif self.current_state == "intro":
                self.draw_intro()
            elif self.current_state == "character_select":
                self.draw_character_select()
            elif self.current_state == "options":
                self.draw_options()
            elif self.current_state == "rankings":
                self.draw_rankings()
            
            # Update and draw transition effects
            self.update_transition()
            self.draw_transition()
            
            pygame.display.flip()
            self.clock.tick(60)
    
    def quit_game(self):
        """Quit the game"""
        if self.sounds["back"]:
            self.sounds["back"].play()
            pygame.time.wait(500)  # Wait for sound to play
        pygame.quit()
        sys.exit()

def main():
    while True:
        menu = Menu(screen)
        menu.run()

if __name__ == "__main__":
    main() 