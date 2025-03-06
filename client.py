import pygame
import socketio
import json
import threading
import os

# Inicializar Pygame
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
pygame.display.set_caption("Stick Brawl")
clock = pygame.time.Clock()

# Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

COLOR_MAP = {
    "red": RED,
    "blue": BLUE,
    "green": GREEN,
    "yellow": YELLOW
}

class GameClient:
    def __init__(self):
        self.sio = socketio.Client()
        self.game_state = {
            'players': {},
            'weapons': [],
            'platforms': [],
            'projectiles': [],
            'buffs': [],
            'scores': {}
        }
        self.game_state_lock = threading.Lock()
        self.running = True
        self.show_class_selection = False
        self.selected_class = None
        self.load_images()

    def load_images(self):
        PLATFORM_SIZE = (200, 70)
        WEAPON_SIZE = (30, 30)
        SWORD_SIZE = (120, 120)
        PLAYER_SIZE = (40, 60)
        PROJECTILE_SIZE = (30, 30)
        BACKGROUND_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
        BUFF_SIZE = (30, 30)

        try:
            self.background_image = pygame.transform.scale(
                pygame.image.load("./imgs/background.png").convert_alpha(), 
                BACKGROUND_SIZE
            )
            self.platform_image = pygame.transform.scale(
                pygame.image.load("./imgs/platform.png").convert_alpha(), 
                PLATFORM_SIZE
            )
            self.sword_image = pygame.transform.scale(
                pygame.image.load("./imgs/sword.png").convert_alpha(), 
                SWORD_SIZE
            )
            self.gun_image = pygame.transform.scale(
                pygame.image.load("./imgs/gun.png").convert_alpha(), 
                WEAPON_SIZE
            )
            self.player_images = {
                "red": pygame.transform.scale(
                    pygame.image.load("./imgs/player_red.png").convert_alpha(), 
                    PLAYER_SIZE
                ),
                "blue": pygame.transform.scale(
                    pygame.image.load("./imgs/player_red.png").convert_alpha(), 
                    PLAYER_SIZE
                ),
            }
            self.projectile_image = pygame.transform.scale(
                pygame.image.load("./imgs/projectile.png").convert_alpha(), 
                PROJECTILE_SIZE
            )
            self.buff_images = {
                "damage": pygame.transform.scale(pygame.image.load("./imgs/damage_buff.png").convert_alpha(), BUFF_SIZE),
                "speed": pygame.transform.scale(pygame.image.load("./imgs/speed_buff.png").convert_alpha(), BUFF_SIZE),
                "heal": pygame.transform.scale(pygame.image.load("./imgs/heal_buff.png").convert_alpha(), BUFF_SIZE),
            }
        except FileNotFoundError as e:
            print(f"Erro: Não foi possível carregar uma imagem. Verifique o arquivo: {e}")
            self.running = False

    def setup_socket_events(self):
        @self.sio.event
        def connect():
            print("Connected to server!")

        @self.sio.event
        def game_state(data):
            with self.game_state_lock:
                self.game_state = data

        @self.sio.event
        def choose_class(data):
            self.show_class_selection = True
            self.selected_class = None

        @self.sio.event
        def game_over(data):
            winner = data['winner']
            print(f"Game Over! Player {winner} wins!")
            self.running = False

    def connect_to_server(self, url='http://localhost:5000'):
        try:
            self.sio.connect(url)
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            self.running = False

    def draw_stick_figure(self, x, y, color, weapon=None, facing_right=True, animation_state="idle"):
        player_image = self.player_images.get(color, self.player_images["red"])
        if not facing_right:
            player_image = pygame.transform.flip(player_image, True, False)
        screen.blit(player_image, (x - player_image.get_width() // 2, y - player_image.get_height()))

        if weapon:
            weapon_image = self.sword_image if weapon == "sword" else self.gun_image
            if not facing_right:
                weapon_image = pygame.transform.flip(weapon_image, True, False)
            weapon_offset_x = 20 if facing_right else -20
            screen.blit(weapon_image, (x + weapon_offset_x - weapon_image.get_width() // 2, 
                                       y - 30 - weapon_image.get_height() // 2))

    def draw_health_bar(self, x, y, health):
        bar_width = 50
        health_ratio = health / 100
        pygame.draw.rect(screen, (255, 0, 0), (x - 25, y - 50, bar_width, 5))
        pygame.draw.rect(screen, (0, 255, 0), (x - 25, y - 50, bar_width * health_ratio, 5))

    def draw_platform(self, platform):
        screen.blit(self.platform_image, (platform['x'], platform['y']))

    def draw_weapon(self, weapon):
        if weapon['type'] == 'sword':
            screen.blit(self.sword_image, (weapon['x'] - self.sword_image.get_width() // 2, 
                                           weapon['y'] - self.sword_image.get_height() // 2))
        else:
            screen.blit(self.gun_image, (weapon['x'] - self.gun_image.get_width() // 2, 
                                         weapon['y'] - self.gun_image.get_height() // 2))

    def draw_projectile(self, projectile):
        screen.blit(self.projectile_image, (int(projectile['x']) - self.projectile_image.get_width() // 2, 
                                            int(projectile['y']) - self.projectile_image.get_height() // 2))

    def draw_buff(self, buff):
        buff_image = self.buff_images.get(buff['type'], self.buff_images["damage"])
        screen.blit(buff_image, (int(buff['x']) - buff_image.get_width() // 2, 
                                 int(buff['y']) - buff_image.get_height() // 2))

    def draw_game(self):
        screen.blit(self.background_image, (0, 0))
        with self.game_state_lock:
            for platform in self.game_state['platforms']:
                self.draw_platform(platform)
            for weapon in self.game_state['weapons']:
                self.draw_weapon(weapon)
            for buff in self.game_state['buffs']:
                self.draw_buff(buff)
            for player_id, player in self.game_state['players'].items():
                self.draw_stick_figure(player['x'], player['y'], player['color'], player['weapon'], 
                                       player['facing_right'], player['animation_state'])
                self.draw_health_bar(player['x'], player['y'], player['health'])
            for projectile in self.game_state['projectiles']:
                self.draw_projectile(projectile)
            font = pygame.font.Font(None, 36)
            for pid, score in self.game_state['scores'].items():
                player_color = self.game_state['players'][pid]['color']
                score_text = font.render(f"{player_color}: {score}", True, WHITE)
                screen.blit(score_text, (10, 10 + list(self.game_state['scores'].keys()).index(pid) * 40))
        pygame.display.flip()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        input_data = {
            'left': keys[pygame.K_LEFT],
            'right': keys[pygame.K_RIGHT],
            'jump': keys[pygame.K_SPACE],
            'attack': keys[pygame.K_e],
            'dodge': keys[pygame.K_LSHIFT],
            'climb': keys[pygame.K_c]
        }
        self.sio.emit('player_input', input_data)

    def handle_class_selection(self):
        if self.show_class_selection:
            font = pygame.font.Font(None, 50)
            title_font = pygame.font.Font(None, 70)
            screen.fill(BLACK)
            
            title_text = title_font.render("Escolha Sua Classe", True, WHITE)
            screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 100))
            
            classes = ["Fighter", "Mage", "Archer"]
            button_rects = []
            
            for i, cls in enumerate(classes):
                text = font.render(cls, True, WHITE)
                text_rect = text.get_rect(center=(SCREEN_WIDTH//2, 200 + i*60))
                button_rect = text_rect.inflate(20, 10)
                button_rects.append((button_rect, cls))
                
                if button_rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(screen, YELLOW, button_rect, 2)
                else:
                    pygame.draw.rect(screen, WHITE, button_rect, 2)
                
                screen.blit(text, text_rect)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for rect, cls in button_rects:
                            if rect.collidepoint(event.pos):
                                self.selected_class = cls
                                self.sio.emit('class_choice', {'class_type': self.selected_class})
                                self.show_class_selection = False
                                break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.selected_class = "Fighter"
                    elif event.key == pygame.K_2:
                        self.selected_class = "Mage"
                    elif event.key == pygame.K_3:
                        self.selected_class = "Archer"
                    elif event.key == pygame.K_RETURN and self.selected_class:
                        self.sio.emit('class_choice', {'class_type': self.selected_class})
                        self.show_class_selection = False

    def run(self):
        while self.running:
            if self.show_class_selection:
                self.handle_class_selection()
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                if self.sio.connected:
                    self.handle_input()
                    self.draw_game()
            
            clock.tick(60)
        
        pygame.quit()
        if self.sio.connected:
            self.sio.disconnect()

if __name__ == '__main__':
    client = GameClient()
    client.setup_socket_events()
    client.connect_to_server()
    client.run()