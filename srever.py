import socket
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
import socket
import threading
import json

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


class WebChatHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('index.html', 'rb') as f:
                self.wfile.write(f.read())
        else:
            super().do_GET()


# HTML файл для телефона
html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Мобильный чат</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial; margin: 0; padding: 10px; }
        #chat { border: 1px solid #ccc; height: 300px; overflow-y: scroll; padding: 10px; margin-bottom: 10px; }
        input, button { padding: 10px; margin: 5px; }
    </style>
</head>
<body>
    <h2>Локальный чат</h2>
    <div id="chat"></div>
    <input type="text" id="message" placeholder="Сообщение...">
    <button onclick="sendMessage()">Отправить</button>

    <script>
        const ws = new WebSocket('ws://ВАШ_IP:5556');

        ws.onmessage = function(event) {
            const chat = document.getElementById('chat');
            chat.innerHTML += event.data + '<br>';
            chat.scrollTop = chat.scrollHeight;
        };

        function sendMessage() {
            const message = document.getElementById('message').value;
            if(message) {
                ws.send(message);
                document.getElementById('message').value = '';
            }
        }

        document.getElementById('message').addEventListener('keypress', function(e) {
            if(e.key === 'Enter') sendMessage();
        });
    </script>
</body>
</html>
"""

# Сохраните как index.html
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

if __name__ == "__main__":
    server = ChatServer()
    server.start()