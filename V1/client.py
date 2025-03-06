import pygame
import socketio
import json
import threading
import os
import math

# Inicializar Pygame
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
pygame.display.set_caption("A Queijada Real de Sintra")
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
        self.round_info = {"round": 1, "max_rounds": 10, "current_level": "pastelaria"}
        self.load_images()

    def load_images(self):
        WEAPON_SIZE = (30, 30)
        SWORD_SIZE = (120, 120)
        PLAYER_SIZE = (40, 60)
        PROJECTILE_SIZE = (30, 30)
        BACKGROUND_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
        BUFF_SIZE = (30, 30)
        QUEIJADA_SIZE = (50, 50)

        try:
            self.background_image = pygame.transform.scale(
                pygame.image.load("./imgs/background.png").convert_alpha(), 
                BACKGROUND_SIZE
            )
            self.platform_image_base = pygame.image.load("./imgs/platform.png").convert_alpha()
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
                "invencivel": pygame.transform.scale(pygame.image.load("./imgs/damage_buff.png").convert_alpha(), BUFF_SIZE),
                "mordida": pygame.transform.scale(pygame.image.load("./imgs/damage_buff.png").convert_alpha(), BUFF_SIZE),
                "queijada": self.create_queijada_image(QUEIJADA_SIZE)
            }
        except FileNotFoundError as e:
            print(f"Erro: Não foi possível carregar uma imagem. Verifique o arquivo: {e}")
            self.running = False

    def create_queijada_image(self, size):
        """Cria uma imagem para a Queijada"""
        queijada = pygame.Surface(size, pygame.SRCALPHA)
        
        # Desenha a base (amarela)
        pygame.draw.circle(queijada, (255, 220, 100), (size[0]//2, size[1]//2), size[0]//2)
        
        # Desenha detalhes (marrom claro)
        pygame.draw.circle(queijada, (200, 150, 50), (size[0]//2, size[1]//2), size[0]//3)
        
        # Adiciona brilho
        pygame.draw.circle(queijada, (255, 255, 200), (size[0]//3, size[1]//3), size[0]//8)
        
        # Adiciona efeito pulsante dourado ao redor
        glow = pygame.Surface(size, pygame.SRCALPHA)
        for i in range(5, 0, -1):
            alpha = 50 - i * 10
            color = (255, 215, 0, alpha)  # Dourado com transparência
            pygame.draw.circle(glow, color, (size[0]//2, size[1]//2), size[0]//2 + i*2)
        
        queijada.blit(glow, (0, 0))
        return queijada

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
            
        @self.sio.event
        def round_change(data):
            self.round_info = {
                "round": data['round'],
                "max_rounds": data['max_rounds'],
                "current_level": data['next_level']
            }
            
        @self.sio.event
        def queijada_spawned(data):
            print("A Queijada Real de Sintra apareceu!")
            
        @self.sio.event
        def pombo_roubou(data):
            print(data['message'])
            
        @self.sio.event
        def easter_egg(data):
            print(data['event'])

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
        # Escalar a imagem da plataforma para corresponder às dimensões físicas
        platform_image = pygame.transform.scale(
            self.platform_image_base, (int(platform['width']), int(platform['height']))
        )
        # Centralizar a imagem no ponto (x, y) recebido do servidor
        screen.blit(platform_image, (
            platform['x'] - platform_image.get_width() // 2,
            platform['y'] - platform_image.get_height() // 2
        ))
        
        # Desenhar contorno para melhor visualização
        rect = pygame.Rect(
            platform['x'] - platform['width'] // 2,
            platform['y'] - platform['height'] // 2,
            platform['width'],
            platform['height']
        )
        pygame.draw.rect(screen, (255, 255, 255), rect, 1)

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
        
        # Efeito especial para a Queijada
        if buff['type'] == 'queijada':
            # Fazer a queijada pulsar
            pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) * 0.1 + 1.0
            size = int(buff_image.get_width() * pulse)
            scaled_image = pygame.transform.scale(buff_image, (size, size))
            
            screen.blit(scaled_image, (
                int(buff['x']) - scaled_image.get_width() // 2, 
                int(buff['y']) - scaled_image.get_height() // 2
            ))
            
            # Desenhar texto "Queijada Real" acima
            font = pygame.font.Font(None, 24)
            text = font.render("Queijada Real!", True, (255, 215, 0))
            screen.blit(text, (
                int(buff['x']) - text.get_width() // 2,
                int(buff['y']) - scaled_image.get_height() // 2 - 20
            ))
        else:
            screen.blit(buff_image, (
                int(buff['x']) - buff_image.get_width() // 2, 
                int(buff['y']) - buff_image.get_height() // 2
            ))

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
            
            # Desenhar placares
            font = pygame.font.Font(None, 36)
            title_font = pygame.font.Font(None, 24)
            
            # Título do jogo
            title_text = title_font.render("A Queijada Real de Sintra", True, WHITE)
            screen.blit(title_text, (SCREEN_WIDTH - title_text.get_width() - 10, 10))
            
            # Informação do round e nível
            round_text = title_font.render(f"Round: {self.round_info['round']}/{self.round_info['max_rounds']} - {self.round_info['current_level'].capitalize()}", True, WHITE)
            screen.blit(round_text, (SCREEN_WIDTH - round_text.get_width() - 10, 30))
            
            # Placar
            for pid, score in self.game_state['scores'].items():
                player_color = self.game_state['players'][pid]['color']
                class_type = self.game_state['players'][pid]['class_type']
                class_names = {
                    "Fighter": "Pasteleiro",
                    "Mage": "Hipnotizador",
                    "Archer": "Ladrão"
                }
                display_name = class_names.get(class_type, class_type)
                score_text = font.render(f"{display_name}: {score}", True, COLOR_MAP[player_color])
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
            
            classes = ["Pasteleiro Lutador", "Hipnotizador do Açúcar", "Ladrão de Doces"]
            descriptions = [
                "Usa tabuleiros e rolos da massa como armas",
                "Cega inimigos com açúcar em pó",
                "Rouba buffs dos adversários com ataques rápidos"
            ]
            button_rects = []
            
            for i, cls in enumerate(classes):
                text = font.render(cls, True, WHITE)
                text_rect = text.get_rect(center=(SCREEN_WIDTH//2, 200 + i*80))
                button_rect = text_rect.inflate(20, 10)
                button_rects.append((button_rect, cls))
                
                if button_rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(screen, YELLOW, button_rect, 2)
                else:
                    pygame.draw.rect(screen, WHITE, button_rect, 2)
                
                screen.blit(text, text_rect)
                
                # Adicionar descrição
                desc_font = pygame.font.Font(None, 30)
                desc_text = desc_font.render(descriptions[i], True, WHITE)
                desc_rect = desc_text.get_rect(center=(SCREEN_WIDTH//2, 230 + i*80))
                screen.blit(desc_text, desc_rect)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for rect, cls in button_rects:
                            if rect.collidepoint(event.pos):
                                self.selected_class = cls
                                class_map = {
                                    "Pasteleiro Lutador": "Fighter",
                                    "Hipnotizador do Açúcar": "Mage",
                                    "Ladrão de Doces": "Archer"
                                }
                                self.sio.emit('class_choice', {'class_type': class_map[self.selected_class]})
                                self.show_class_selection = False
                                break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.selected_class = "Pasteleiro Lutador"
                        self.sio.emit('class_choice', {'class_type': "Fighter"})
                        self.show_class_selection = False
                    elif event.key == pygame.K_2:
                        self.selected_class = "Hipnotizador do Açúcar"
                        self.sio.emit('class_choice', {'class_type': "Mage"})
                        self.show_class_selection = False
                    elif event.key == pygame.K_3:
                        self.selected_class = "Ladrão de Doces"
                        self.sio.emit('class_choice', {'class_type': "Archer"})
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