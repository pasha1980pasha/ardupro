from pynput import keyboard, mouse
from ahk import AHK
import time
import threading

# Инициализируем AutoHotKey
ahk = AHK()

def execute_copy_all():
    """Выполняет Ctrl+A → Ctrl+C"""
    print("📋 [КЛАВИАТУРА] Page Up → Ctrl+A → Ctrl+C")
    ahk.send('^a')
    time.sleep(0.1)
    ahk.send('^c')

def execute_replace_all():
    """Выполняет Ctrl+A → Delete → Ctrl+V"""
    print("🔄 [МЫШЬ] Средняя кнопка → Ctrl+A → Del → Ctrl+V")
    ahk.send('^a')
    time.sleep(0.1)
    ahk.send('{Del}')
    time.sleep(0.1)
    ahk.send('^v')

# Обработчик клавиатуры
def on_press_key(key):
    try:
        if key == keyboard.Key.page_up:
            execute_copy_all()
    except Exception as e:
        print(f"Ошибка клавиатуры: {e}")

def on_release_key(key):
    if key == keyboard.Key.esc:
        print("✋ ESC нажат — завершаем...")
        return False  # Остановит слушатель клавиатуры

# Обработчик мыши
def on_click(x, y, button, pressed):
    # Нас интересует только нажатие (не отпускание) средней кнопки
    if pressed and button == mouse.Button.middle:
        execute_replace_all()

# Запуск обоих слушателей в отдельных потоках
def start_keyboard_listener():
    with keyboard.Listener(on_press=on_press_key, on_release=on_release_key) as listener:
        listener.join()

def start_mouse_listener():
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

# Главный запуск
if __name__ == "__main__":
    print("🚀 Скрипт запущен!")
    print("⌨️  Page Up — выделить всё и скопировать (Ctrl+A → Ctrl+C)")
    print("🖱️  Средняя кнопка мыши — выделить, удалить и вставить (Ctrl+A → Del → Ctrl+V)")
    print("✋ Нажмите Esc — чтобы выйти\n")

    # Запускаем слушатели в фоновых потоках
    keyboard_thread = threading.Thread(target=start_keyboard_listener, daemon=True)
    mouse_thread = threading.Thread(target=start_mouse_listener, daemon=True)

    keyboard_thread.start()
    mouse_thread.start()

    # Ждём, пока основной поток не завершится (например, по нажатию Esc)
    try:
        while keyboard_thread.is_alive() or mouse_thread.is_alive():
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n✋ Принудительное завершение...")
