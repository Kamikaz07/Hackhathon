import socket
import pickle
import json
import threading
import time

class Network:
    def __init__(self, host, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.addr = (self.host, self.port)
        self.connect()
    
    def connect(self):
        """Connect to the server"""
        try:
            self.client.connect(self.addr)
            return True
        except:
            return False
    
    def send(self, data):
        """Send data to the server and receive response"""
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
            print(f"Network error: {e}")
            return None
    
    def receive(self):
        """Receive data from the server"""
        try:
            data = self.client.recv(4096).decode()
            return json.loads(data)
        except:
            return None
    
    def close(self):
        """Close the connection"""
        self.client.close()


class Server:
    def __init__(self, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.host = ''  # Empty string means listen on all available interfaces
        self.port = port
        self.server.bind((self.host, self.port))
        self.server.listen(2)  # Allow up to 2 connections
        self.clients = []
        self.client_data = [None, None]
        self.running = True
        print(f"Server started on port {port}")
    
    def handle_client(self, conn, client_id):
        """Handle client connection"""
        print(f"Client {client_id} connected")
        
        # Get initial data from client
        try:
            data = conn.recv(4096).decode()
            self.client_data[client_id] = json.loads(data)
            
            # Send initial data back to client
            if client_id == 0:
                # First player has to wait for second player
                while self.client_data[1] is None and self.running:
                    time.sleep(0.1)
                
                if not self.running:
                    return
                
                response = {
                    "name": self.client_data[1].get("name", "Player 2"),
                    "class": self.client_data[1].get("class", 0)
                }
            else:
                # Second player gets first player's data immediately
                response = {
                    "name": self.client_data[0].get("name", "Player 1"),
                    "class": self.client_data[0].get("class", 0)
                }
            
            conn.send(json.dumps(response).encode())
        except:
            self.client_data[client_id] = None
            self.clients.remove(conn)
            conn.close()
            return
        
        # Main client loop
        while self.running:
            try:
                # Receive data from client
                data = conn.recv(4096).decode()
                if not data:
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
            except:
                break
        
        print(f"Client {client_id} disconnected")
        self.client_data[client_id] = None
        self.clients.remove(conn)
        conn.close()
    
    def start(self):
        """Start the server"""
        print("Waiting for connections...")
        client_id = 0
        
        while self.running and len(self.clients) < 2:
            try:
                self.server.settimeout(1.0)  # 1 second timeout to check if we're still running
                conn, addr = self.server.accept()
                self.clients.append(conn)
                
                # Start a new thread to handle this client
                thread = threading.Thread(target=self.handle_client, args=(conn, client_id))
                thread.daemon = True
                thread.start()
                
                client_id += 1
            except socket.timeout:
                continue
            except:
                break
        
        print("Server stopped")
    
    def stop(self):
        """Stop the server"""
        self.running = False
        self.server.close()
        
        # Close all client connections
        for conn in self.clients:
            try:
                conn.close()
            except:
                pass 