import socket
import pickle
import json
import threading
import time

class Network:
    def __init__(self, host, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(30)
        self.host = host
        self.port = port
        self.addr = (self.host, self.port)
        self.connected = self.connect()
    
    def connect(self):
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
            # Send length first
            json_data = json.dumps(data)
            length = len(json_data)
            self.client.send(str(length).zfill(8).encode())  # Fixed length header
            
            # Send actual data
            self.client.send(json_data.encode())
            
            # Receive response length
            length = int(self.client.recv(8).decode())
            
            # Receive actual response
            response = ""
            while len(response) < length:
                chunk = self.client.recv(min(4096, length - len(response))).decode()
                if not chunk:
                    break
                response += chunk
                
            return json.loads(response)
        except socket.timeout:
            print("Timeout ao enviar/receber dados - tentando reconectar...")
            self.client.close()
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.settimeout(30)
            self.connected = self.connect()
            return None
        except Exception as e:
            print(f"Erro de rede ao enviar/receber dados: {e}")
            self.connected = False
            return None
    
    def receive(self):
        """Receive data from the server"""
        if not self.connected:
            return None
            
        try:
            # Receive length first
            length = int(self.client.recv(8).decode())
            
            # Receive actual data
            data = ""
            while len(data) < length:
                chunk = self.client.recv(min(4096, length - len(data))).decode()
                if not chunk:
                    return None
                data += chunk
                
            return json.loads(data)
        except socket.timeout:
            print("Timeout ao receber dados - tentando reconectar...")
            self.client.close()
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.settimeout(30)
            self.connected = self.connect()
            return None
        except Exception as e:
            print(f"Erro ao receber dados: {e}")
            self.connected = False
            return None
    
    def close(self):
        try:
            self.client.close()
            print("Conexão fechada")
        except:
            pass


class Server:
    def __init__(self, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.host = ''
        self.port = port
        
        try:
            self.server.bind((self.host, self.port))
            self.server.listen(2)
            self.clients = []
            self.client_data = [None, None]
            self.running = True
            
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            print(f"Servidor iniciado na porta {port}")
            print(f"IP local para conexão: {local_ip}")
            print(f"Se estiver na mesma rede, outros jogadores podem se conectar usando este IP.")
        except Exception as e:
            print(f"Erro ao iniciar servidor: {e}")
            self.running = False
    
    def send_data(self, conn, data):
        """Helper function to send data with length prefix"""
        try:
            json_data = json.dumps(data)
            length = len(json_data)
            conn.send(str(length).zfill(8).encode())
            conn.send(json_data.encode())
            return True
        except:
            return False
    
    def receive_data(self, conn):
        """Helper function to receive data with length prefix"""
        try:
            length = int(conn.recv(8).decode())
            data = ""
            while len(data) < length:
                chunk = conn.recv(min(4096, length - len(data))).decode()
                if not chunk:
                    return None
                data += chunk
            return json.loads(data)
        except:
            return None
    
    def handle_client(self, conn, client_id):
        """Handle client connection"""
        print(f"Cliente {client_id} conectado")
        conn.settimeout(30)
        
        # Get initial data from client
        try:
            data = self.receive_data(conn)
            if not data:
                print(f"Dados iniciais inválidos do cliente {client_id}")
                self.client_data[client_id] = None
                self.clients.remove(conn)
                conn.close()
                return
                
            self.client_data[client_id] = data
            print(f"Dados recebidos do cliente {client_id}: {self.client_data[client_id]}")
            
            # Send initial data back to client
            if client_id == 0:
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
                print("Enviando dados do primeiro jogador para o segundo jogador.")
                response = {
                    "name": self.client_data[0].get("name", "Player 1"),
                    "class": self.client_data[0].get("class", 0)
                }
            
            if not self.send_data(conn, response):
                raise Exception("Falha ao enviar dados iniciais")
                
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
                data = self.receive_data(conn)
                if not data:
                    print(f"Conexão perdida com cliente {client_id}")
                    break
                
                self.client_data[client_id] = data
                
                other_client_id = 1 if client_id == 0 else 0
                response = self.client_data[other_client_id] if self.client_data[other_client_id] is not None else {}
                
                if not self.send_data(conn, response):
                    break
                    
            except socket.timeout:
                if not self.send_data(conn, {}):
                    break
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