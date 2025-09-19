import socket
import threading

class ChatServer:
    def __init__(self, host='0.0.0.0', port=5555):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.nicknames = []
    
    def start(self):
        self.server.bind((self.host, self.port))
        self.server.listen()
        print(f"✅ Сервер запущен на {self.host}:{self.port}")
        print("📍 Ожидаем подключения клиентов...")
        
        while True:
            client, address = self.server.accept()
            print(f"🔗 Подключение от {address}")
            
            client.send("NICK".encode('utf-8'))
            nickname = client.recv(1024).decode('utf-8')
            
            self.nicknames.append(nickname)
            self.clients.append(client)
            
            print(f"👤 Никнейм клиента: {nickname}")
            self.broadcast(f"{nickname} присоединился к чату!".encode('utf-8'))
            
            thread = threading.Thread(target=self.handle_client, args=(client,))
            thread.start()
    
    def broadcast(self, message):
        for client in self.clients:
            try:
                client.send(message)
            except:
                self.remove_client(client)
    
    def handle_client(self, client):
        while True:
            try:
                message = client.recv(1024)
                if message:
                    self.broadcast(message)
            except:
                self.remove_client(client)
                break
    
    def remove_client(self, client):
        if client in self.clients:
            index = self.clients.index(client)
            self.clients.remove(client)
            nickname = self.nicknames[index]
            self.nicknames.remove(nickname)
            self.broadcast(f"{nickname} покинул чат".encode('utf-8'))
            client.close()
            print(f"❌ {nickname} отключился")

if __name__ == "__main__":
    server = ChatServer()
    server.start()