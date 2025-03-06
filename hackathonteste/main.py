import pygame
import pygame_menu
import sys
import os
from game import Game
from network import Network, Server
import threading
import random
import socket

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
connection_status = "Não conectado"
error_message = ""

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
    global server, server_thread, connection_status, error_message
    
    try:
        connection_status = "Iniciando servidor..."
        server = Server(port)
        if not server.running:
            error_message = "Não foi possível iniciar o servidor. Tente outra porta."
            connection_status = "Erro"
            return False
            
        connection_status = "Servidor iniciado"
        server_thread = threading.Thread(target=server.start)
        server_thread.daemon = True
        server_thread.start()
        return True
    except Exception as e:
        error_message = f"Erro ao iniciar servidor: {e}"
        connection_status = "Erro"
        return False

def get_local_ip():
    """Get local IP address for easier connection"""
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return local_ip
    except:
        return "Não disponível"

def start_game():
    """Start the actual game"""
    global player_name, selected_class, is_host, ip_address, port, connection_status, error_message
    
    try:
        # Select a random level
        level = random.randint(0, 4)
        
        # If we're hosting, start the server
        if is_host:
            if not start_server():
                return
        
        # Create network connection
        connection_status = "Conectando ao servidor..."
        network = Network(ip_address, port)
        
        if not network.connected:
            connection_status = "Erro de conexão"
            error_message = "Não foi possível conectar ao servidor. Verifique o IP e a porta."
            return
        
        connection_status = "Conectado! Enviando dados iniciais..."
        
        # Send initial data
        initial_data = {
            'name': player_name,
            'class': selected_class
        }
        
        # Send data and get response
        response = network.send(initial_data)
        
        if response is None:
            connection_status = "Erro de conexão"
            error_message = "Falha ao enviar dados iniciais."
            return
        
        # Create and start the game
        connection_status = "Iniciando jogo..."
        game = Game(screen, network, selected_class, player_name, level, level_backgrounds[level])
        
        # Main game loop
        while True:
            game.handle_events()
            game.update()
            game.draw()
            
            if not game.running:
                break
            
            pygame.display.flip()
            clock.tick(FPS)
        
        # After game ends, reset connection status
        connection_status = "Não conectado"
        error_message = ""
        
    except Exception as e:
        connection_status = "Erro"
        error_message = f"Erro ao iniciar jogo: {str(e)}"
        print(f"Erro ao iniciar jogo: {str(e)}")

def create_main_menu():
    """Create the main menu"""
    global player_name, selected_class, is_host, ip_address, port, connection_status, error_message
    
    def set_player_name(value):
        global player_name
        player_name = value
    
    def set_class(value, index):
        global selected_class
        selected_class = index
    
    def set_host(value, index):
        global is_host, connection_status, error_message
        is_host = (index == 0)
        connection_status = "Não conectado"
        error_message = ""
        if is_host:
            for item in server_container.get_widgets():
                item.hide()
            ip_label.show()
        else:
            for item in server_container.get_widgets():
                item.show()
            ip_label.hide()
    
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
    
    # Display local IP when hosting
    local_ip = get_local_ip()
    ip_label = menu.add.label(f"Seu IP local: {local_ip} (Outros jogadores usam este IP para conectar)")
    
    # Server connection frame
    server_container = menu.add.frame_v(width=SCREEN_WIDTH * 0.8, height=150, align=pygame_menu.locals.ALIGN_CENTER)
    server_container._relax = True
    server_container.pack(menu.add.text_input('IP: ', default=ip_address, onchange=set_ip_address))
    server_container.pack(menu.add.text_input('Porta: ', default=str(port), onchange=set_port))
    
    for item in server_container.get_widgets():
        item.hide()
    
    # Status display frame
    status_container = menu.add.frame_v(width=SCREEN_WIDTH * 0.8, height=150, align=pygame_menu.locals.ALIGN_CENTER)
    status_container._relax = True
    
    # Create labels with padding
    status_label = menu.add.label("Status: Não conectado", padding=(0, 10))
    error_label = menu.add.label("", padding=(0, 10))
    
    # Add labels to container
    status_container.pack(status_label)
    status_container.pack(error_label)
    
    # Add buttons
    menu.add.button('Jogar', start_game)
    menu.add.button('Sair', pygame_menu.events.EXIT)
    
    def update_status():
        """Update status and error messages in the menu"""
        status_label.set_title(f"Status: {connection_status}")
        error_label.set_title(error_message)
    
    return menu, update_status

def main():
    """Main function to run the game"""
    # Load assets
    load_assets()
    
    # Create main menu
    menu, update_status_func = create_main_menu()
    
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
        
        # Update status labels
        update_status_func()
        
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