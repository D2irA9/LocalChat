import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext

class ChatClient:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.nickname = ""
        
    def connect(self, host='localhost', port=5555):
        try:
            self.client.connect((host, port))
            print("✅ Подключение к серверу установлено!")
            self.setup_gui()
            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.daemon = True
            self.receive_thread.start()
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
    
    def setup_gui(self):
        self.window = tk.Tk()
        self.window.title("Локальный чат")
        self.window.geometry("500x400")
        
        # Область чата
        self.chat_area = scrolledtext.ScrolledText(self.window, state='disabled')
        self.chat_area.pack(padx=10, pady=5, fill='both', expand=True)
        
        # Фрейм для ввода сообщения
        frame = tk.Frame(self.window)
        frame.pack(padx=10, pady=5, fill='x')
        
        self.msg_entry = tk.Entry(frame, width=40)
        self.msg_entry.pack(side='left', fill='x', expand=True)
        self.msg_entry.bind("<Return>", self.send_message)
        
        self.send_btn = tk.Button(frame, text="Отправить", command=self.send_message)
        self.send_btn.pack(side='right', padx=(5, 0))
        
        # Запрос никнейма
        self.get_nickname()
    
    def get_nickname(self):
        self.nickname = simpledialog.askstring("Никнейм", "Выберите ваш никнейм:", parent=self.window)
        if not self.nickname:
            self.nickname = "Гость"
        self.window.title(f"Локальный чат - {self.nickname}")
    
    def receive_messages(self):
        while True:
            try:
                message = self.client.recv(1024).decode('utf-8')
                if message == "NICK":
                    self.client.send(self.nickname.encode('utf-8'))
                else:
                    self.display_message(message)
            except:
                print("❌ Соединение разорвано!")
                self.display_message("❌ Соединение с сервером потеряно")
                self.client.close()
                break
    
    def display_message(self, message):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, message + "\n")
        self.chat_area.config(state='disabled')
        self.chat_area.see(tk.END)
    
    def send_message(self, event=None):
        message = self.msg_entry.get()
        if message:
            full_message = f"{self.nickname}: {message}"
            try:
                self.client.send(full_message.encode('utf-8'))
                self.msg_entry.delete(0, tk.END)
            except:
                self.display_message("❌ Не удалось отправить сообщение")
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    client = ChatClient()
    client.connect('localhost')
    client.run()