import socket
import threading
import datetime
import os


class ChatServer:
    def __init__(self, host='0.0.0.0', port=5555):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.nicknames = []
        self.chat_log = "chat_history.txt"
        self.current_date = datetime.date.today().strftime("%d.%m.%Y")

        # Создаем файл лога если его нет
        self.initialize_log_file()

    def initialize_log_file(self):
        """Инициализирует файл лога с заголовком"""
        if not os.path.exists(self.chat_log):
            with open(self.chat_log, 'w', encoding='utf-8') as f:
                f.write("=== ИСТОРИЯ ЧАТА ===\n")
                f.write(f"Чат создан: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}\n")
                f.write("=" * 20 + "\n\n")

    def save_message(self, nickname, message):
        """Сохраняет сообщение в файл"""
        timestamp = datetime.datetime.now().strftime("%H:%M")

        # Проверяем, сменилась ли дата
        today = datetime.date.today().strftime("%d.%m.%Y")
        if today != self.current_date:
            self.current_date = today
            with open(self.chat_log, 'a', encoding='utf-8') as f:
                f.write(f"\nдата: {self.current_date}\n")

        # Сохраняем сообщение
        with open(self.chat_log, 'a', encoding='utf-8') as f:
            # Убираем никнейм из сообщения если он уже есть
            if message.startswith(f"{nickname}:"):
                clean_message = message[len(nickname) + 1:].strip()
            else:
                clean_message = message

            f.write(f"{nickname}: {clean_message} ({timestamp})\n")

        print(f"💾 Сохранено: {nickname} - {message}")

    def start(self):
        self.server.bind((self.host, self.port))
        self.server.listen()
        print(f"✅ Сервер запущен на {self.host}:{self.port}")
        print(f"📝 Лог чата сохраняется в: {self.chat_log}")
        print("📍 Ожидаем подключения клиентов...")

        # Записываем начало сессии
        with open(self.chat_log, 'a', encoding='utf-8') as f:
            f.write(f"\n--- Сессия начата: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')} ---\n")

        while True:
            client, address = self.server.accept()
            print(f"🔗 Подключение от {address}")

            client.send("NICK".encode('utf-8'))
            nickname = client.recv(1024).decode('utf-8')

            self.nicknames.append(nickname)
            self.clients.append(client)

            print(f"👤 Никнейм клиента: {nickname}")
            join_message = f"{nickname} присоединился к чату!"
            self.broadcast(join_message.encode('utf-8'))

            # Сохраняем в лог присоединение
            self.save_message("Система", join_message)

            thread = threading.Thread(target=self.handle_client, args=(client, nickname))
            thread.start()

    def broadcast(self, message):
        for client in self.clients:
            try:
                client.send(message)
            except:
                self.remove_client(client)

    def handle_client(self, client, nickname):
        while True:
            try:
                message = client.recv(1024)
                if message:
                    message_str = message.decode('utf-8')
                    self.broadcast(message)
                    # Сохраняем сообщение в лог
                    self.save_message(nickname, message_str)
            except:
                self.remove_client(client, nickname)
                break

    def remove_client(self, client, nickname):
        if client in self.clients:
            index = self.clients.index(client)
            self.clients.remove(client)
            self.nicknames.remove(nickname)
            leave_message = f"{nickname} покинул чат"
            self.broadcast(leave_message.encode('utf-8'))

            # Сохраняем в лог отключение
            self.save_message("Система", leave_message)

            client.close()
            print(f"❌ {nickname} отключился")

    def __del__(self):
        """Сохраняем окончание сессии при закрытии сервера"""
        try:
            with open(self.chat_log, 'a', encoding='utf-8') as f:
                f.write(f"--- Сессия завершена: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')} ---\n\n")
        except:
            pass


if __name__ == "__main__":
    try:
        server = ChatServer()
        server.start()
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен")
    except Exception as e:
        print(f"❌ Ошибка: {e}")