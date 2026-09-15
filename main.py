import tkinter as tk
from tkinter import messagebox
import os
import pyperclip


def insert_text(entry):
    try:
        # Вставить текст из буфера обмена в поле ввода
        entry.insert(tk.END, pyperclip.paste())
    except pyperclip.PyperclipException:
        messagebox.showerror("Ошибка", "Не удалось получить текст из буфера обмена.")


def create_executable():
    user_id = user_id_entry.get()
    api_token = api_token_entry.get()

    if not user_id or not api_token:
        messagebox.showerror("Ошибка", "Введите ID пользователя и API токен.")
        return

    # Сохраните информацию в config.py с кодировкой utf-8
    with open('config.py', 'w', encoding='utf-8') as f:
        f.write(f"API_TOKEN = '{api_token}'\n")
        f.write(f"ALLOWED_USER_ID = {user_id}\n")


    # Используйте pyinstaller для создания исполняемого файла
    os.system('pyinstaller --onefile --noconsole --add-data "my_image.ico;." bot_script.py')

    messagebox.showinfo("Успех", "Исполняемый файл создан и сохранен в папке 'dist'.")



# Создайте графический интерфейс
root = tk.Tk()
root.title("Создание исполняемого файла для бота")

tk.Label(root, text="API токен:").grid(row=0, column=0, padx=10, pady=10)
api_token_entry = tk.Entry(root)
api_token_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Button(root, text="Вставить", command=lambda: insert_text(api_token_entry)).grid(row=0, column=2, padx=10, pady=10)

tk.Label(root, text="ID пользователя:").grid(row=1, column=0, padx=10, pady=10)
user_id_entry = tk.Entry(root)
user_id_entry.grid(row=1, column=1, padx=10, pady=10)

tk.Button(root, text="Вставить", command=lambda: insert_text(user_id_entry)).grid(row=1, column=2, padx=10, pady=10)

create_button = tk.Button(root, text="Создать файл", command=create_executable)
create_button.grid(row=2, column=0, columnspan=3, pady=20)

root.mainloop()