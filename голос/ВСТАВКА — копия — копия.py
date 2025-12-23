from pynput import keyboard, mouse
from ahk import AHK
import time
import threading
import ctypes
from ctypes import wintypes

# Инициализируем AutoHotKey
ahk = AHK()

# Функции для работы с раскладкой через Windows API
user32 = ctypes.WinDLL('user32', use_last_error=True)

def get_foreground_window():
    """Получает handle активного окна"""
    return user32.GetForegroundWindow()

def get_keyboard_layout(window_handle):
    """Получает раскладку клавиатуры для указанного окна"""
    thread_id = user32.GetWindowThreadProcessId(window_handle, 0)
    layout_id = user32.GetKeyboardLayout(thread_id)
    return layout_id & 0xFFFF

def is_russian_layout():
    """Проверяет, является ли текущая раскладка русской"""
    try:
        hwnd = get_foreground_window()
        layout = get_keyboard_layout(hwnd)
        return layout == 0x419  # 0x419 - русская (RU)
    except Exception as e:
        print(f"Ошибка определения раскладки: {e}")
        return False

def switch_to_english():
    """Переключает на английскую раскладку"""
    try:
        ahk.send('{LWin down}{Space}{LWin up}')
        time.sleep(0.3)
        print("🌐 Переключено на английскую раскладку")
    except Exception as e:
        print(f"Ошибка переключения на английский: {e}")

def switch_to_russian():
    """Переключает на русскую раскладку"""
    try:
        ahk.send('{LWin down}{Space}{LWin up}')
        time.sleep(0.3)
        print("🌐 Переключено на русскую раскладку")
    except Exception as e:
        print(f"Ошибка переключения на русский: {e}")

def execute_copy_all():
    """Выполняет Ctrl+A → Ctrl+C с проверкой раскладки"""
    try:
        was_russian = is_russian_layout()
        
        if was_russian:
            switch_to_english()
            time.sleep(0.3)
        
        print("📋 Выполняем Ctrl+A → Ctrl+C")
        ahk.send('^a')
        time.sleep(0.2)
        ahk.send('^c')
        time.sleep(0.2)
        
        if was_russian:
            switch_to_russian()
            time.sleep(0.2)
            
    except Exception as e:
        print(f"❌ Ошибка в execute_copy_all: {e}")

def execute_replace_all():
    """Выполняет Ctrl+A → Delete → Ctrl+V с проверкой раскладки"""
    try:
        was_russian = is_russian_layout()
        
        if was_russian:
            switch_to_english()
            time.sleep(0.3)
        
        print("🔄 Выполняем Ctrl+A → Del → Ctrl+V")
        ahk.send('^a')
        time.sleep(0.2)
        ahk.send('{Del}')
        time.sleep(0.2)
        ahk.send('^v')
        time.sleep(0.2)
        
        if was_russian:
            switch_to_russian()
            time.sleep(0.2)
            
    except Exception as e:
        print(f"❌ Ошибка в execute_replace_all: {e}")

# Обработчики событий
def on_press_key(key):
    try:
        if key == keyboard.Key.page_up:
            execute_copy_all()
    except Exception as e:
        print(f"Ошибка обработки клавиши: {e}")

def on_release_key(key):
    if key == keyboard.Key.esc:
        print("✋ Завершение работы...")
        return False

def on_click(x, y, button, pressed):
    if pressed and button == mouse.Button.middle:
        execute_replace_all()

# Запуск слушателей
def start_keyboard_listener():
    with keyboard.Listener(on_press=on_press_key, on_release=on_release_key) as listener:
        listener.join()

def start_mouse_listener():
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

if __name__ == "__main__":
    print("🚀 Скрипт запущен!")
    print("⌨️  Page Up — выделить всё и скопировать")
    print("🖱️  Средняя кнопка мыши — выделить, удалить и вставить")
    print("✋ Esc — выход\n")
    
    keyboard_thread = threading.Thread(target=start_keyboard_listener, daemon=True)
    mouse_thread = threading.Thread(target=start_mouse_listener, daemon=True)

    keyboard_thread.start()
    mouse_thread.start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n✋ Завершено пользователем")
