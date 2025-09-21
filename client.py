import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox


class ChatClient:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.nickname = ""

    def connect(self, host='localhost', port=5555):
        try:
            print(f"🔄 Пытаюсь подключиться к {host}:{port}...")
            self.client.connect((host, port))
            print("✅ Подключение к серверу установлено!")
            self.setup_gui()
            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            return True
        except Exception as e:
            error_msg = f"❌ Ошибка подключения: {e}"
            print(error_msg)
            messagebox.showerror("Ошибка подключения", f"Не удалось подключиться к серверу\n{e}")
            return False

    def setup_gui(self):
        self.window = tk.Tk()
        self.window.title("Локальный чат - Подключение...")
        self.window.geometry("600x500")

        # Создаем меню
        self.create_menu()

        # Область чата с контекстным меню
        self.chat_area = scrolledtext.ScrolledText(self.window, state='disabled', wrap=tk.WORD)
        self.chat_area.pack(padx=10, pady=5, fill='both', expand=True)

        # Привязываем контекстное меню к области чата
        self.chat_area.bind("<Button-3>", self.show_context_menu)  # Right-click
        self.chat_area.bind("<Control-c>", self.copy_text)  # Ctrl+C
        self.chat_area.bind("<Control-v>", self.paste_to_input)  # Ctrl+V
        self.chat_area.bind("<Control-a>", self.select_all_chat)  # Ctrl+A

        # Фрейм для ввода сообщения
        frame = tk.Frame(self.window)
        frame.pack(padx=10, pady=5, fill='x')

        self.msg_entry = tk.Entry(frame, width=40)
        self.msg_entry.pack(side='left', fill='x', expand=True)
        self.msg_entry.bind("<Return>", self.send_message)

        # Привязываем контекстное меню к полю ввода
        self.msg_entry.bind("<Button-3>", self.show_input_context_menu)
        self.msg_entry.bind("<Control-v>", self.paste_to_input)  # Ctrl+V
        self.msg_entry.bind("<Control-c>", self.copy_from_input)  # Ctrl+C
        self.msg_entry.bind("<Control-x>", self.cut_from_input)  # Ctrl+X
        self.msg_entry.bind("<Control-a>", self.select_all_input)  # Ctrl+A

        self.send_btn = tk.Button(frame, text="Отправить", command=self.send_message)
        self.send_btn.pack(side='right', padx=(5, 0))

        # Запрос никнейма после подключения
        self.get_nickname()

    def create_menu(self):
        """Создает меню с функциями копирования/вставки"""
        menubar = tk.Menu(self.window)

        # Меню Правка
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Копировать", command=self.copy_text, accelerator="Ctrl+C")
        edit_menu.add_command(label="Вставить", command=self.paste_to_input, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Выделить все", command=self.select_all_chat, accelerator="Ctrl+A")

        menubar.add_cascade(label="Правка", menu=edit_menu)
        self.window.config(menu=menubar)

    def show_context_menu(self, event):
        """Показывает контекстное меню для области чата"""
        context_menu = tk.Menu(self.window, tearoff=0)
        context_menu.add_command(label="Копировать", command=self.copy_text)
        context_menu.add_command(label="Выделить все", command=self.select_all_chat)
        context_menu.tk_popup(event.x_root, event.y_root)

    def show_input_context_menu(self, event):
        """Показывает контекстное меню для поля ввода"""
        context_menu = tk.Menu(self.window, tearoff=0)
        context_menu.add_command(label="Вставить", command=self.paste_to_input)
        context_menu.add_command(label="Вырезать", command=self.cut_from_input)
        context_menu.add_command(label="Копировать", command=self.copy_from_input)
        context_menu.add_separator()
        context_menu.add_command(label="Выделить все", command=self.select_all_input)
        context_menu.tk_popup(event.x_root, event.y_root)

    def copy_text(self, event=None):
        """Копирует выделенный текст из чата"""
        try:
            if self.chat_area.tag_ranges(tk.SEL):
                selected_text = self.chat_area.get(tk.SEL_FIRST, tk.SEL_LAST)
                self.window.clipboard_clear()
                self.window.clipboard_append(selected_text)
                print("📋 Текст скопирован в буфер обмена")
        except:
            pass
        return "break"  # Предотвращаем стандартное поведение

    def copy_from_input(self, event=None):
        """Копирует текст из поля ввода"""
        try:
            if self.msg_entry.selection_present():
                selected_text = self.msg_entry.selection_get()
                self.window.clipboard_clear()
                self.window.clipboard_append(selected_text)
        except:
            pass
        return "break"

    def cut_from_input(self, event=None):
        """Вырезает текст из поля ввода"""
        try:
            if self.msg_entry.selection_present():
                selected_text = self.msg_entry.selection_get()
                self.window.clipboard_clear()
                self.window.clipboard_append(selected_text)
                self.msg_entry.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except:
            pass
        return "break"

    def paste_to_input(self, event=None):
        """Вставляет текст в поле ввода"""
        try:
            clipboard_text = self.window.clipboard_get()
            if self.msg_entry.selection_present():
                self.msg_entry.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.msg_entry.insert(tk.INSERT, clipboard_text)
        except:
            pass
        return "break"

    def select_all_chat(self, event=None):
        """Выделяет весь текст в чате"""
        self.chat_area.config(state='normal')
        self.chat_area.tag_add(tk.SEL, "1.0", tk.END)
        self.chat_area.mark_set(tk.INSERT, "1.0")
        self.chat_area.see(tk.INSERT)
        self.chat_area.config(state='disabled')
        return "break"

    def select_all_input(self, event=None):
        """Выделяет весь текст в поле ввода"""
        self.msg_entry.select_range(0, tk.END)
        return "break"

    def get_nickname(self):
        self.nickname = simpledialog.askstring("Никнейм", "Выберите ваш никнейм:", parent=self.window)
        if not self.nickname:
            self.nickname = "Гость"
        self.window.title(f"Локальный чат - {self.nickname}")
        # Отправляем никнейм серверу
        try:
            self.client.send(self.nickname.encode('utf-8'))
        except:
            self.display_message("❌ Не удалось отправить никнейм")

    def receive_messages(self):
        while True:
            try:
                message = self.client.recv(1024).decode('utf-8')
                if message == "NICK":
                    # Сервер запрашивает никнейм
                    self.client.send(self.nickname.encode('utf-8'))
                else:
                    self.display_message(message)
            except Exception as e:
                error_msg = f"❌ Ошибка соединения: {e}"
                print(error_msg)
                self.display_message(error_msg)
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
            except Exception as e:
                error_msg = f"❌ Не удалось отправить сообщение: {e}"
                self.display_message(error_msg)

    def run(self):
        self.window.mainloop()


def main():
    # Сначала запросим хост для подключения
    root = tk.Tk()
    root.withdraw()

    host = simpledialog.askstring("Подключение", "Введите IP адрес сервера:",
                                  initialvalue="localhost",
                                  parent=root)

    if not host:
        print("❌ Отменено пользователем")
        return

    client = ChatClient()
    if client.connect(host):
        client.run()
    else:
        print("Не удалось подключиться к серверу")


if __name__ == "__main__":
    main()