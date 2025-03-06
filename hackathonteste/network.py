import socket
import pickle
import json
import threading
import time

class Network:
    def __init__(self, host, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(5)  # 5 second timeout for connections
        self.host = host
        self.port = port
        self.addr = (self.host, self.port)
        self.connected = self.connect()
    
    def connect(self):
        """Connect to the server"""
        try:
            print(f"Tentando conectar ao servidor {self.host}:{self.port}...")
            self.client.connect(self.addr)
            print("Conectado com sucesso!")
            return True
        except Exception as e:
            print(f"Erro ao conectar: {e}")
            return False
    
    def send(self, data):
        """Send data to the server and receive response"""
        if not self.connected:
            return None
            
        try:
            # Convert data to JSON
            json_data = json.dumps(data)
            # Send data
            self.client.send(json_data.encode())
            # Receive response
            response = self.client.recv(4096).decode()
            # Parse JSON response
            return json.loads(response)
        except Exception as e:
            print(f"Erro de rede ao enviar/receber dados: {e}")
            self.connected = False
            return None
    
    def receive(self):
        """Receive data from the server"""
        if not self.connected:
            return None
            
        try:
            data = self.client.recv(4096).decode()
            return json.loads(data)
        except Exception as e:
            print(f"Erro ao receber dados: {e}")
            self.connected = False
            return None
    
    def close(self):
        """Close the connection"""
        try:
            self.client.close()
            print("Conexão fechada")
        except:
            pass


class Server:
    def __init__(self, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.host = ''  # Empty string means listen on all available interfaces
        self.port = port
        
        try:
            self.server.bind((self.host, self.port))
            self.server.listen(2)  # Allow up to 2 connections
            self.clients = []
            self.client_data = [None, None]
            self.running = True
            
            # Get local IP for easier connection
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            print(f"Servidor iniciado na porta {port}")
            print(f"IP local para conexão: {local_ip}")
            print(f"Se estiver na mesma rede, outros jogadores podem se conectar usando este IP.")
        except Exception as e:
            print(f"Erro ao iniciar servidor: {e}")
            self.running = False
    
    def handle_client(self, conn, client_id):
        """Handle client connection"""
        print(f"Cliente {client_id} conectado")
        
        # Get initial data from client
        try:
            data = conn.recv(4096).decode()
            if not data:
                print(f"Dados iniciais inválidos do cliente {client_id}")
                self.client_data[client_id] = None
                self.clients.remove(conn)
                conn.close()
                return
                
            self.client_data[client_id] = json.loads(data)
            print(f"Dados recebidos do cliente {client_id}: {self.client_data[client_id]}")
            
            # Send initial data back to client
            if client_id == 0:
                # First player has to wait for second player
                print("Aguardando segundo jogador se conectar...")
                while self.client_data[1] is None and self.running:
                    time.sleep(0.1)
                
                if not self.running:
                    return
                
                print("Segundo jogador conectado. Enviando dados para o primeiro jogador.")
                response = {
                    "name": self.client_data[1].get("name", "Player 2"),
                    "class": self.client_data[1].get("class", 0)
                }
            else:
                # Second player gets first player's data immediately
                print("Enviando dados do primeiro jogador para o segundo jogador.")
                response = {
                    "name": self.client_data[0].get("name", "Player 1"),
                    "class": self.client_data[0].get("class", 0)
                }
            
            conn.send(json.dumps(response).encode())
            print(f"Dados enviados com sucesso para o cliente {client_id}")
        except Exception as e:
            print(f"Erro ao inicializar cliente {client_id}: {e}")
            self.client_data[client_id] = None
            if conn in self.clients:
                self.clients.remove(conn)
            conn.close()
            return
        
        # Main client loop
        while self.running:
            try:
                # Receive data from client
                data = conn.recv(4096).decode()
                if not data:
                    print(f"Conexão perdida com cliente {client_id}")
                    break
                
                # Update client data
                self.client_data[client_id] = json.loads(data)
                
                # Send other client's data
                other_client_id = 1 if client_id == 0 else 0
                if self.client_data[other_client_id] is not None:
                    conn.send(json.dumps(self.client_data[other_client_id]).encode())
                else:
                    # If other client hasn't sent data yet, send empty data
                    conn.send(json.dumps({}).encode())
            except Exception as e:
                print(f"Erro na comunicação com cliente {client_id}: {e}")
                break
        
        print(f"Cliente {client_id} desconectado")
        self.client_data[client_id] = None
        if conn in self.clients:
            self.clients.remove(conn)
        conn.close()
    
    def start(self):
        """Start the server"""
        if not self.running:
            print("O servidor não pôde ser iniciado devido a um erro anterior.")
            return
            
        print("Aguardando conexões...")
        client_id = 0
        
        while self.running and len(self.clients) < 2:
            try:
                self.server.settimeout(1.0)  # 1 second timeout to check if we're still running
                conn, addr = self.server.accept()
                print(f"Nova conexão de {addr}")
                self.clients.append(conn)
                
                # Start a new thread to handle this client
                thread = threading.Thread(target=self.handle_client, args=(conn, client_id))
                thread.daemon = True
                thread.start()
                
                client_id += 1
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Erro ao aceitar conexão: {e}")
                break
        
        print("Servidor parado")
    
    def stop(self):
        """Stop the server"""
        self.running = False
        try:
            self.server.close()
            print("Servidor fechado")
        except:
            pass
        
        # Close all client connections
        for conn in self.clients:
            try:
                conn.close()
            except:
                pass 