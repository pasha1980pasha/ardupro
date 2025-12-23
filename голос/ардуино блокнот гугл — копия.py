import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import pyperclip
import pyautogui
import keyboard
import queue
import os
import sys
import zipfile
import requests
from io import BytesIO

# =============================
# 🔧 АВТОМАТИЧЕСКАЯ УСТАНОВКА ЗАВИСИМОСТЕЙ
# =============================
def install_package(package):
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

required_packages = ["vosk", "pyaudio", "requests", "keyboard", "pyautogui", "pyperclip"]
for package in required_packages:
    try:
        __import__(package.replace("-", "_"))
    except ImportError:
        print(f"Устанавливаю {package}...")
        install_package(package)

# После установки импортируем
from vosk import Model, KaldiRecognizer
import pyaudio

# =============================
# 🌐 АВТОСКАЧИВАНИЕ И РАСПАКОВКА МОДЕЛИ VOSK
# =============================
MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip"
MODEL_DIR = "model"

def download_and_extract_model():
    if os.path.exists(MODEL_DIR) and os.path.exists(os.path.join(MODEL_DIR, "model.conf")):
        print("✅ Модель Vosk уже установлена.")
        return True
    
    try:
        print("🌐 Скачивание модели Vosk (русский, small)...")
        response = requests.get(MODEL_URL, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        chunk_size = 8192
        
        with BytesIO() as file_buffer:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    file_buffer.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = int(downloaded * 100 / total_size)
                        print(f"\r🔽 Скачано: {percent}%", end="")
            
            print("\n✅ Модель скачана. Распаковка...")
            file_buffer.seek(0)
            
            with zipfile.ZipFile(file_buffer) as z:
                # Извлекаем имя папки внутри архива
                folder_name = z.namelist()[0].split('/')[0]
                z.extractall()
                
                # Переименовываем папку в 'model'
                if os.path.exists(MODEL_DIR):
                    import shutil
                    shutil.rmtree(MODEL_DIR)
                os.rename(folder_name, MODEL_DIR)
        
        print("✅ Модель успешно установлена!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при скачивании модели: {e}")
        return False

# Скачиваем модель при запуске, если её нет
if not download_and_extract_model():
    raise Exception("❗ Не удалось установить модель Vosk. Проверьте интернет-соединение.")

# =============================
# 🔌 МОДУЛЬ: Обработчик текста
# =============================
class TextProcessor:
    def __init__(self, use_english_mode=False):
        self.use_english_mode = use_english_mode
        self.russian_to_latin = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh',
            'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
            'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts',
            'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        }

    def transliterate_word(self, word):
        if not self.use_english_mode:
            return word
        result = ""
        i = 0
        while i < len(word):
            char = word[i]
            if i < len(word) - 1:
                two_chars = word[i:i+2].lower()
                if two_chars in ('жи', 'ши', 'че', 'ще', 'ху'):
                    mapping = {'жи': 'zhi', 'ши': 'shi', 'че': 'che', 'ще': 'shche', 'ху': 'khu'}
                    result += mapping[two_chars]
                    i += 2
                    continue
            result += self.russian_to_latin.get(char, char)
            i += 1
        return result

    def process(self, text):
        if not text:
            return ""
        clean_text = text.lower()
        if self.use_english_mode:
            words = clean_text.split()
            transliterated_words = [self.transliterate_word(word) for word in words]
            clean_text = ' '.join(transliterated_words)
        return clean_text


# =============================
# 🔌 МОДУЛЬ: Вставщик текста (ультра-быстрый)
# =============================
class TextInserter:
    def __init__(self):
        self.ahk = None
        try:
            from ahk import AHK
            self.ahk = AHK()
        except Exception as e:
            print(f"⚠️ AHK не доступен: {e}")

    def insert(self, text):
        if text is None:
            text = ""
        try:
            if self.ahk:
                if text:
                    self.ahk.type(text)
                self.ahk.send("{Space}")
                return True
        except Exception as e:
            print(f"Ошибка AHK: {e}")
        try:
            pyperclip.copy(text)
            pyautogui.hotkey('ctrl', 'v')
            pyautogui.press('space')
            return True
        except Exception as e2:
            print(f"Ошибка вставки: {e2}")
            return False


# =============================
# 🔌 МОДУЛЬ: Распознаватель речи (VOSK — оффлайн, потоковый)
# =============================
class VoskSpeechRecognizer:
    def __init__(self):
        self.model = Model(MODEL_DIR)
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.listening = False

    def listen(self, result_queue, listening_flag):
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=8000
        )
        
        self.stream.start_stream()
        
        while listening_flag():
            try:
                data = self.stream.read(4000, exception_on_overflow=False)
                if self.recognizer.AcceptWaveform(data):
                    result = self.recognizer.Result()
                    import json
                    text = json.loads(result).get("text", "")
                    if text.strip():
                        result_queue.put(text)
            except Exception as e:
                print(f"Ошибка записи: {e}")
                break
        
        self.stream.stop_stream()
        self.stream.close()

    def stop(self):
        if self.stream:
            self.stream.close()


# =============================
# 🎛️ ОСНОВНОЙ КЛАСС — С VOSK + АВТОУСТАНОВКА
# =============================
class SmartInstantVoiceNotepad:
    def __init__(self, root):
        self.root = root
        self.root.title("🎤 АРДУ БЛОКНОТ ПРО")
        self.root.geometry("900x600")
        self.root.configure(bg='#2c3e50')
        
        self.text_processor = TextProcessor(use_english_mode=False)
        self.text_inserter = TextInserter()
        self.speech_recognizer = VoskSpeechRecognizer()
        
        self.listening = False
        self.current_text = ""
        self.result_queue = queue.Queue()
        self.last_status = ""
        
        try:
            keyboard.add_hotkey('f12', self.paste_text_global)
        except Exception as e:
            messagebox.showwarning("Предупреждение", f"Не удалось зарегистрировать F12: {str(e)}")

        self.setup_ui()

    def setup_ui(self):
        main_container = tk.Frame(self.root, bg='#2c3e50')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title_label = tk.Label(main_container, text="🎤 АРДУ БЛОКНОТ ПРО", 
                               font=('Arial', 18, 'bold'), bg='#2c3e50', fg='white')
        title_label.pack(pady=20)
        
        button_frame = tk.Frame(main_container, bg='#2c3e50')
        button_frame.pack(pady=15)

        self.start_btn = tk.Button(button_frame, text="🎤 Начать запись", command=self.toggle_recording,
                                   font=('Arial', 10, 'bold'), bg='#e74c3c', fg='white', 
                                   activebackground='#c0392b', relief=tk.RAISED, bd=3, padx=12, pady=8)
        self.start_btn.pack(side=tk.LEFT, padx=8)

        self.clear_btn = tk.Button(button_frame, text="🧹 Очистить", command=self.clear_text,
                                   font=('Arial', 10, 'bold'), bg='#f39c12', fg='white',
                                   activebackground='#d35400', relief=tk.RAISED, bd=3, padx=12, pady=8)
        self.clear_btn.pack(side=tk.LEFT, padx=8)

        self.copy_btn = tk.Button(button_frame, text="📋 Скопировать", command=self.copy_to_clipboard,
                                  font=('Arial', 10, 'bold'), bg='#27ae60', fg='white',
                                  activebackground='#229954', relief=tk.RAISED, bd=3, padx=12, pady=8)
        self.copy_btn.pack(side=tk.LEFT, padx=8)

        self.eng_btn = tk.Button(button_frame, text="🔤 Английский: ВЫКЛ", command=self.toggle_english_mode,
                                 font=('Arial', 10, 'bold'), bg='#3498db', fg='white',
                                 activebackground='#2980b9', relief=tk.RAISED, bd=3, padx=12, pady=8)
        self.eng_btn.pack(side=tk.LEFT, padx=8)
        
        self.record_indicator = tk.Label(main_container, text="🔴 НЕ ЗАПИСЫВАЕТ", 
                                        font=('Arial', 12, 'bold'), fg='red', bg='#2c3e50')
        self.record_indicator.pack(pady=10)
        
        text_label = tk.Label(main_container, text="Распознанный текст:", 
                             font=('Arial', 11, 'bold'), fg='#ffffff', bg='#2c3e50')
        text_label.pack(pady=(15, 5), anchor=tk.W)
        
        self.text_area = scrolledtext.ScrolledText(main_container, wrap=tk.WORD, width=100, height=15, 
                                                  font=('Consolas', 12, 'bold'),
                                                  bg='#1a1a1a', fg='#ffffff',
                                                  relief=tk.SUNKEN, bd=3, insertbackground='white')
        self.text_area.pack(pady=5, fill=tk.BOTH, expand=True)
        self.text_area.insert(tk.END, "Здесь появится текст...\n\n")
        
        self.stats_frame = tk.Frame(main_container, bg='#2c3e50')
        self.stats_frame.pack(pady=10, fill=tk.X)
        self.stats_label = tk.Label(self.stats_frame, text="Слов: 0 | Символов: 0", 
                                   font=('Arial', 9), fg='#bdc3c7', bg='#2c3e50')
        self.stats_label.pack()
        
        self.status_var = tk.StringVar()
        self.status_var.set("✅ Готов к работе! Нажмите 'Начать запись'")
        status_bar = tk.Label(main_container, textvariable=self.status_var, relief=tk.SUNKEN, 
                              anchor=tk.W, bg='#34495e', fg='#ffffff', font=('Arial', 9))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

    def set_status(self, msg):
        if msg != self.last_status:
            self.last_status = msg
            self.status_var.set(msg)

    def toggle_english_mode(self):
        self.text_processor.use_english_mode = not self.text_processor.use_english_mode
        if self.text_processor.use_english_mode:
            self.eng_btn.config(text="🔤 Английский: ВКЛ", bg='#2980b9')
            self.set_status("🔤 Режим: русская речь → латиница")
        else:
            self.eng_btn.config(text="🔤 Английский: ВЫКЛ", bg='#3498db')
            self.set_status("🔤 Режим: обычная русская печать")

    def paste_text_global(self):
        if not hasattr(self, 'current_text'):
            return
        try:
            self.text_inserter.insert(self.current_text)
            self.set_status("✅ Текст вставлен!")
        except Exception as e:
            self.set_status(f"❌ Ошибка вставки: {str(e)}")

    def process_results(self):
        try:
            while True:
                text = self.result_queue.get_nowait()
                if text.strip():
                    processed_text = self.text_processor.process(text)
                    success = self.text_inserter.insert(processed_text)
                    self.root.after(0, self.update_text, processed_text)
        except queue.Empty:
            pass
        finally:
            if self.listening:
                self.root.after(50, self.process_results)

    def toggle_recording(self):
        if not self.listening:
            self.start_listening()
        else:
            self.stop_listening()

    def start_listening(self):
        self.listening = True
        self.start_btn.config(text="⏹️ Остановить запись", bg='#c0392b')
        self.record_indicator.config(text="🟢 ЗАПИСЬ ИДЁТ... ГОВОРИТЕ", fg='green')
        self.set_status("🎤 Запись начата...")

        threading.Thread(target=self.speech_recognizer.listen, args=(self.result_queue, lambda: self.listening), daemon=True).start()
        self.root.after(50, self.process_results)

    def stop_listening(self):
        self.listening = False
        self.start_btn.config(text="🎤 Начать запись", bg='#e74c3c')
        self.record_indicator.config(text="🔴 НЕ ЗАПИСЫВАЕТ", fg='red')
        self.set_status("⏸️ Запись остановлена")

    def update_text(self, text):
        self.current_text += text
        if text:
            self.current_text += " "
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, self.current_text)
        self.copy_to_clipboard()
        self.update_stats()
        self.text_area.see(tk.END)

    def update_stats(self):
        text = self.current_text
        word_count = len(text.split()) if text.strip() else 0
        char_count = len(text)
        self.stats_label.config(text=f"Слов: {word_count} | Символов: {char_count}")

    def clear_text(self):
        self.current_text = ""
        self.text_area.delete(1.0, tk.END)
        pyperclip.copy("")
        self.update_stats()
        self.set_status("🧹 Текст очищен")

    def copy_to_clipboard(self):
        pyperclip.copy(self.current_text)

    def on_closing(self):
        self.listening = False
        try:
            keyboard.remove_hotkey('f12')
        except: pass
        if hasattr(self, 'speech_recognizer'):
            self.speech_recognizer.stop()
        self.root.destroy()


# =============================
# 🚀 ЗАПУСК — ВСЁ АВТОМАТИЧЕСКИ
# =============================
if __name__ == "__main__":
    root = tk.Tk()
    try:
        app = SmartInstantVoiceNotepad(root)
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Критическая ошибка", f"Не удалось запустить приложение:\n{str(e)}")
        sys.exit(1)
