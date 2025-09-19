from http.server import SimpleHTTPRequestHandler, HTTPServer
import threading


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


def start_web_server():
    web_server = HTTPServer(('0.0.0.0', 8000), WebChatHandler)
    print("🌐 Веб-сервер запущен на порту 8000")
    web_server.serve_forever()


if __name__ == "__main__":
    # Создаем HTML файл
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Мобильный чат</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial; margin: 0; padding: 10px; background: #f0f0f0; }
        #chat { border: 1px solid #ccc; height: 300px; overflow-y: scroll; padding: 10px; 
                margin-bottom: 10px; background: white; border-radius: 5px; }
        input { padding: 10px; margin: 5px; width: 70%; border-radius: 5px; border: 1px solid #ccc; }
        button { padding: 10px; background: #007bff; color: white; border: none; border-radius: 5px; }
    </style>
</head>
<body>
    <h2>📱 Мобильный чат</h2>
    <div id="chat"></div>
    <div>
        <input type="text" id="message" placeholder="Введите сообщение...">
        <button onclick="sendMessage()">Отправить</button>
    </div>

    <script>
        // Эта версия пока только показывает статическую страницу
        // WebSocket потребует дополнительной настройки на сервере
        document.getElementById('chat').innerHTML = 
            '⚠️ Веб-версия в разработке. Используйте Termux или desktop клиент.<br>' +
            '✅ Сервер socket чата работает на порту 5555<br>' +
            '📞 Для подключения с телефона используйте mobile_client.py в Termux';

        function sendMessage() {
            alert('WebSocket версия в разработке. Используйте мобильный клиент.');
        }
    </script>
</body>
</html>"""

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    start_web_server()