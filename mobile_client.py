import socket
import threading


def mobile_client():
    nickname = input("Введите ваш никнейм: ")

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Укажите IP вашего компьютера-сервера
    server_ip = input("Введите IP сервера: ")

    try:
        client.connect((server_ip, 5555))
        print("✅ Подключено к серверу!")

        # Отправляем никнейм
        client.send(nickname.encode('utf-8'))

        # Поток для получения сообщений
        def receive_messages():
            while True:
                try:
                    message = client.recv(1024).decode('utf-8')
                    print(f"\n📨 {message}\n> ", end="")
                except:
                    print("\n❌ Соединение разорвано!")
                    break

        receive_thread = threading.Thread(target=receive_messages)
        receive_thread.daemon = True
        receive_thread.start()

        # Отправка сообщений
        while True:
            message = input("> ")
            if message.lower() == 'exit':
                break
            client.send(f"{nickname}: {message}".encode('utf-8'))

    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    mobile_client()