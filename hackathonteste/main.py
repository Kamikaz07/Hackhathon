import pygame
import pygame_menu
import sys
import os
from game import Game
from network import Network, Server
import threading
import random

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "Batalha Pela Queijada de Sintra"
THEME_COLOR = (139, 69, 19)  # Brown, like a Queijada

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# Global variables
player_name = "Jogador"
selected_class = 0
is_host = True
ip_address = "localhost"
port = 5555
server = None
server_thread = None

# Background images for each level
level_backgrounds = {
    0: None,  # Will be loaded in the load_assets function
    1: None,
    2: None,
    3: None,
    4: None
}

def load_assets():
    """Load all game assets"""
    # Placeholder background images (will be replaced with proper assets)
    level_backgrounds[0] = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    level_backgrounds[0].fill((255, 223, 186))  # Light brown for bakery
    
    level_backgrounds[1] = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    level_backgrounds[1].fill((150, 150, 150))  # Gray for station
    
    level_backgrounds[2] = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    level_backgrounds[2].fill((34, 139, 34))  # Forest green
    
    level_backgrounds[3] = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    level_backgrounds[3].fill((169, 169, 169))  # Gray for mountain
    
    level_backgrounds[4] = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    level_backgrounds[4].fill((218, 165, 32))  # Golden for palace

def start_server():
    """Start the game server"""
    global server, server_thread
    server = Server(port)
    server_thread = threading.Thread(target=server.start)
    server_thread.daemon = True
    server_thread.start()

def start_game():
    """Start the actual game"""
    global player_name, selected_class, is_host, ip_address, port
    
    # Select a random level
    level = random.randint(0, 4)
    
    # If we're hosting, start the server
    if is_host:
        start_server()
    
    # Create network connection
    network = Network(ip_address, port)
    
    # Send initial data
    network.send({
        'name': player_name,
        'class': selected_class
    })
    
    # Get initial game state
    initial_data = network.receive()
    if not initial_data:
        print("Could not connect to server")
        return
    
    # Create and start the game
    game = Game(screen, network, selected_class, player_name, level, level_backgrounds[level])
    game.run()

def create_main_menu():
    """Create the main menu"""
    global player_name, selected_class, is_host, ip_address, port
    
    def set_player_name(value):
        global player_name
        player_name = value
    
    def set_class(value, index):
        global selected_class
        selected_class = index
    
    def set_host(value, index):
        global is_host
        is_host = (index == 0)
        if is_host:
            for item in server_container.get_widgets():
                item.hide()
        else:
            for item in server_container.get_widgets():
                item.show()
    
    def set_ip_address(value):
        global ip_address
        ip_address = value
    
    def set_port(value):
        global port
        try:
            port = int(value)
        except ValueError:
            pass

    # Create the menu theme
    theme = pygame_menu.themes.THEME_DARK.copy()
    theme.background_color = THEME_COLOR
    theme.title_font = pygame_menu.font.FONT_MUNRO
    theme.widget_font = pygame_menu.font.FONT_MUNRO
    
    menu = pygame_menu.Menu(
        height=SCREEN_HEIGHT,
        theme=theme,
        title=TITLE,
        width=SCREEN_WIDTH
    )
    
    menu.add.text_input('Nome: ', default=player_name, onchange=set_player_name)
    
    menu.add.selector(
        'Classe: ',
        [('Pasteleiro Lutador (Fighter)', 0),
         ('Hipnotizador do Açúcar (Mage)', 1),
         ('Ladrão de Doces (Archer)', 2)],
        onchange=set_class
    )
    
    menu.add.selector(
        'Modo: ',
        [('Hospedar Jogo', 0),
         ('Conectar ao Jogo', 1)],
        onchange=set_host
    )
    
    server_container = menu.add.frame_v(width=SCREEN_WIDTH * 0.8, height=100, align=pygame_menu.locals.ALIGN_CENTER)
    
    server_container.pack(menu.add.text_input('IP: ', default=ip_address, onchange=set_ip_address))
    server_container.pack(menu.add.text_input('Porta: ', default=str(port), onchange=set_port))
    
    for item in server_container.get_widgets():
        item.hide()
    
    menu.add.button('Jogar', start_game)
    menu.add.button('Sair', pygame_menu.events.EXIT)
    
    return menu

def main():
    """Main function to run the game"""
    # Load assets
    load_assets()
    
    # Create main menu
    menu = create_main_menu()
    
    # Main game loop
    while True:
        # Handle events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        # Update menu
        menu.update(events)
        
        # Clear screen
        screen.fill((0, 0, 0))
        
        # Draw menu
        menu.draw(screen)
        
        # Update display
        pygame.display.update()
        
        # Cap the frame rate
        clock.tick(FPS)

if __name__ == "__main__":
    main() 