import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import speech_recognition as sr
import threading
import pyperclip
import time
import pyautogui
import keyboard
import re
import queue
import sys
import subprocess
import platform

# ========================
# УСТАНОВКА ЗАВИСИМОСТЕЙ
# ========================
def install_dependencies():
    deps = ["pyautogui", "keyboard", "speechrecognition", "pyperclip"]
    for dep in deps:
        try:
            __import__(dep)
        except ImportError:
            print(f"Устанавливаю {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])

install_dependencies()

# После установки импортируем заново (на всякий случай)
import speech_recognition as sr
import pyautogui
import keyboard
import pyperclip


class SmartInstantVoiceNotepad:
    def __init__(self, root):
        self.root = root
        self.root.title("🎤 АРДУ БЛОКНОТ ПРО")
        self.root.geometry("900x700")
        self.root.configure(bg='#2c3e50')
        
        self.recognizer = sr.Recognizer()
        self.listening = False
        self.current_text = ""
        self.audio_queue = queue.Queue()
        self.english_mode = False  # Флаг для английского режима

        # Настройка распознавателя
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 1.0
        
        # Словари для улучшенной обработки текста
        self.punctuation_commands = {
            'точка': '.', 'точку': '.', 'точки': '.',
            'запятая': ',', 'запятую': ',', 'запятые': ',',
            'восклицательный знак': '!', 'вопросительный знак': '?',
            'двоеточие': ':', 'тире': ' - ', 'новая строка': '\n',
            'кавычки': '"', 'скобки': '()', 'точка с запятой': ';',
            'многоточие': '...', 'открывающая скобка': '(', 'закрывающая скобка': ')',
            'открывающая кавычка': '"', 'закрывающая кавычка': '"',
            'вопрос': '?', 'восклицание': '!', 'конец': '.'
        }
        
        self.common_errors = {
            'здраствуйте': 'здравствуйте', 'здрасти': 'здравствуйте',
            'извеняйте': 'извиняйте', 'извиняйте': 'извините',
            'привед': 'привет', 'приветик': 'привет',
            'какдила': 'как дела', 'какдели': 'как дела',
            'спсибо': 'спасибо', 'спасиб': 'спасибо',
            'пожайлуста': 'пожалуйста', 'пожалуста': 'пожалуйста',
            'пажалуста': 'пожалуйста', 'пажалуйста': 'пожалуйста',
            'щас': 'сейчас', 'сейчай': 'сейчас',
            'чё': 'что', 'че': 'что',
            'ничо': 'ничего', 'ниче': 'ничего',
            'ага': 'да', 'угу': 'да',
            'ща': 'сейчас', 'щаща': 'сейчас',
            'спс': 'спасибо', 'пасиб': 'спасибо',
            'скоко': 'сколько', 'скока': 'сколько',
            'када': 'когда', 'кода': 'когда',
            'здеся': 'здесь', 'тута': 'тут',
            'хош': 'хочешь', 'хошь': 'хочешь',
            'щастье': 'счастье', 'счастье': 'счастье',
            'йес': 'yes', 'нот': 'not', 'ту': 'to', 'фор': 'for'
        }

        # Вопросные слова для автоматической пунктуации
        self.question_words = {
            'кто', 'что', 'где', 'когда', 'почему', 'как', 
            'сколько', 'чей', 'какой', 'какая', 'какое', 
            'какие', 'зачем', 'откуда', 'куда', 'кому', 
            'кого', 'чем', 'насколько', 'why', 'what', 'where', 'when', 'how'
        }
        
        # Восклицательные слова
        self.exclamation_words = {
            'ого', 'ух', 'ах', 'вау', 'здорово', 'круто',
            'прекрасно', 'отлично', 'замечательно', 'супер',
            'боже', 'господи', 'черт', 'блин', 'огонь',
            'wow', 'cool', 'nice', 'great', 'awesome'
        }

        # Стили
        style = ttk.Style()
        style.configure('Start.TButton', font=('Arial', 10, 'bold'), padding=8, background='#e74c3c', foreground='white')
        style.configure('Clear.TButton', font=('Arial', 10, 'bold'), padding=8, background='#f39c12', foreground='white')
        style.configure('Copy.TButton', font=('Arial', 10, 'bold'), padding=8, background='#27ae60', foreground='white')
        style.configure('Fix.TButton', font=('Arial', 10, 'bold'), padding=8, background='#9b59b6', foreground='white')
        style.configure('Lang.TButton', font=('Arial', 10, 'bold'), padding=8, background='#3498db', foreground='white')
        style.configure('Title.TLabel', font=('Arial', 18, 'bold'), background='#2c3e50', foreground='white')
        style.configure('TFrame', background='#2c3e50')
        style.configure('TLabel', background='#2c3e50', foreground='white')
        
        # Главный контейнер
        main_container = ttk.Frame(root, style='TFrame')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Заголовок
        title_label = ttk.Label(main_container, text="🎤 АРДУ БЛОКНОТ ПРО", style='Title.TLabel')
        title_label.pack(pady=20)
        
        # Фрейм для кнопок
        button_frame = ttk.Frame(main_container, style='TFrame')
        button_frame.pack(pady=15)
        
        # Кнопки
        self.start_btn = ttk.Button(button_frame, text="🎤 Начать запись", command=self.toggle_recording, style='Start.TButton')
        self.start_btn.pack(side=tk.LEFT, padx=8)
        
        self.clear_btn = ttk.Button(button_frame, text="🧹 Очистить", command=self.clear_text, style='Clear.TButton')
        self.clear_btn.pack(side=tk.LEFT, padx=8)
        
        self.copy_btn = ttk.Button(button_frame, text="📋 Скопировать", command=self.copy_to_clipboard, style='Copy.TButton')
        self.copy_btn.pack(side=tk.LEFT, padx=8)
        
        self.fix_btn = ttk.Button(button_frame, text="✨ Умное исправление", command=self.smart_correct, style='Fix.TButton')
        self.fix_btn.pack(side=tk.LEFT, padx=8)
        
        self.lang_btn = ttk.Button(button_frame, text="🔤 Англ. режим: ВЫКЛ", command=self.toggle_english, style='Lang.TButton')
        self.lang_btn.pack(side=tk.LEFT, padx=8)
        
        # Индикатор записи
        self.record_indicator = ttk.Label(main_container, text="🔴 НЕ ЗАПИСЫВАЕТ", 
                                        font=('Arial', 12, 'bold'), foreground='red')
        self.record_indicator.pack(pady=10)
        
        # Метка для текста
        text_label = ttk.Label(main_container, text="Распознанный текст:", 
                             font=('Arial', 11, 'bold'), foreground='#ecf0f1')
        text_label.pack(pady=(15, 5), anchor=tk.W)
        
        # Текстовое поле
        self.text_area = scrolledtext.ScrolledText(main_container, wrap=tk.WORD, width=100, height=18, 
                                                  font=('Arial', 11), bg='#34495e', fg='#ecf0f1', 
                                                  relief=tk.FLAT, bd=2, insertbackground='white')
        self.text_area.pack(pady=5, fill=tk.BOTH, expand=True)
        self.text_area.insert(tk.END, "Здесь появится текст...\n\n")
        
        # Статистика
        self.stats_frame = ttk.Frame(main_container, style='TFrame')
        self.stats_frame.pack(pady=10, fill=tk.X)
        
        self.stats_label = ttk.Label(self.stats_frame, text="Слов: 0 | Символов: 0", 
                                   font=('Arial', 9), foreground='#bdc3c7')
        self.stats_label.pack()
        
        # Инструкция
        instruction_frame = ttk.Frame(main_container, style='TFrame')
        instruction_frame.pack(pady=20, fill=tk.X)
        
        instruction_text = """💡 КАК ИСПОЛЬЗОВАТЬ:
1. Поставьте курсор в нужное поле (чат, Word, Excel, браузер).
2. Нажмите 'Начать запись' — начните говорить.
3. 💥 Текст мгновенно вставится туда, где курсор!
4. Используйте команды: 'точка', 'запятая', 'вопрос', 'восклицание'
5. 'Умное исправление' улучшит пунктуацию и орфографию
6. Кнопка 'Англ. режим' переключает ввод на английские буквы"""

        instruction = ttk.Label(instruction_frame, text=instruction_text, font=('Arial', 10), 
                               background='#34495e', foreground='#bdc3c7', wraplength=850, 
                               justify=tk.LEFT, padding=15)
        instruction.pack(fill=tk.X)
        
        # Индикатор состояния
        self.status_var = tk.StringVar()
        self.status_var.set("✅ Готов к работе! Нажмите 'Начать запись'")
        status_bar = ttk.Label(main_container, textvariable=self.status_var, relief=tk.SUNKEN, 
                              anchor=tk.W, background='#34495e', foreground='#ecf0f1')
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
        # Проверяем микрофон
        try:
            mic_list = sr.Microphone.list_microphone_names()
            if mic_list:
                self.microphone = sr.Microphone(device_index=0)
                self.status_var.set(f"✅ Микрофон: {mic_list[0]}")
            else:
                self.microphone = None
                self.start_btn.config(state='disabled')
                self.status_var.set("❌ Микрофон не найден!")
        except Exception as e:
            self.microphone = None
            self.start_btn.config(state='disabled')
            self.status_var.set(f"❌ Ошибка микрофона: {str(e)}")

        # Регистрируем глобальную клавишу F12
        try:
            keyboard.add_hotkey('f12', self.paste_text_global)
            print("✅ Глобальная клавиша F12 зарегистрирована!")
        except Exception as e:
            print(f"❌ Ошибка регистрации F12: {e}")
            messagebox.showwarning("Предупреждение", f"Не удалось зарегистрировать F12: {str(e)}")

    def instant_paste(self, text):
        """Мгновенная вставка текста (кроссплатформенно)"""
        try:
            pyperclip.copy(text)
            time.sleep(0.05)
            if platform.system() == "Darwin":  # macOS
                pyautogui.hotkey('command', 'v')
            else:  # Windows, Linux
                pyautogui.hotkey('ctrl', 'v')
            return True
        except Exception as e:
            print(f"Ошибка вставки: {e}")
            return False

    def paste_text_global(self):
        """Глобальная функция для F12"""
        if not self.current_text.strip():
            return
        
        try:
            pyperclip.copy(self.current_text.strip())
            time.sleep(0.1)
            if platform.system() == "Darwin":
                pyautogui.hotkey('command', 'v')
            else:
                pyautogui.hotkey('ctrl', 'v')
            if self.root.winfo_exists():
                self.status_var.set("✅ Текст вставлен!")
        except Exception as e:
            if self.root.winfo_exists():
                self.status_var.set(f"❌ Ошибка вставки: {str(e)}")

    def add_punctuation(self, text):
        """Умная расстановка знаков препинания"""
        text_lower = text.lower()
        
        for command, symbol in self.punctuation_commands.items():
            if command in text_lower:
                return symbol
        
        words = text_lower.split()
        
        if len(words) > 0:
            if any(word in self.question_words for word in words[:2]):
                return '?'
            if any(word in self.exclamation_words for word in words):
                return '!'
            if len(words) > 5 and not any(punc in text for punc in '.!?'):
                return '.'
        
        return ''

    def correct_spelling(self, text):
        """Исправление орфографии по словарю"""
        words = text.split()
        corrected_words = []
        
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word.lower())
            if clean_word in self.common_errors:
                corrected = self.common_errors[clean_word]
                if word and word[0].isupper():
                    corrected = corrected.capitalize()
                if word.endswith(('.', ',', '!', '?', ';', ':')):
                    corrected += word[-1]
                corrected_words.append(corrected)
            else:
                corrected_words.append(word)
        
        return ' '.join(corrected_words)

    def smart_punctuation(self, text):
        """Умная расстановка пунктуации в готовом тексте"""
        text = re.sub(r'([,.!?;:])([а-яa-zА-ЯA-Z])', r'\1 \2', text)
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\s([,.!?;:])', r'\1', text)
        return text.strip()

    def capitalize_sentences(self, text):
        """Начинать каждое предложение с заглавной буквы"""
        sentences = re.split(r'([.!?] )', text)
        capitalized = []
        for i, part in enumerate(sentences):
            if i % 2 == 0 and part:
                part = part[0].upper() + part[1:] if len(part) > 1 else part.upper()
            capitalized.append(part)
        return ''.join(capitalized)

    def transliterate_to_english(self, text):
        """Простая замена кириллицы на латиницу"""
        mapping = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '',
            'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
            'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
            'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
            'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
            'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch', 'Ъ': '',
            'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
        }
        for rus, eng in mapping.items():
            text = text.replace(rus, eng)
        return text

    def process_text(self, text):
        """Обработка текста: исправление, пунктуация, заглавные буквы"""
        if not text.strip():
            return ""
        
        original_text = text.lower().strip()
        punctuation = self.add_punctuation(original_text)
        
        for command in self.punctuation_commands.keys():
            original_text = original_text.replace(command, '')
        
        original_text = original_text.strip()
        original_text = self.correct_spelling(original_text)
        
        if punctuation:
            if punctuation in {'.', '!', '?'}:
                original_text += punctuation
            else:
                original_text += punctuation if punctuation != '\n' else '\n'
        
        if self.english_mode:
            original_text = self.transliterate_to_english(original_text)
        
        original_text = self.smart_punctuation(original_text)
        original_text = self.capitalize_sentences(original_text)
        
        return original_text + ' '

    def update_stats(self):
        text = self.current_text
        word_count = len(text.split()) if text else 0
        char_count = len(text) if text else 0
        self.stats_label.config(text=f"Слов: {word_count} | Символов: {char_count}")

    def toggle_recording(self):
        if not self.listening:
            self.start_listening()
        else:
            self.stop_listening()

    def start_listening(self):
        if self.microphone is None:
            messagebox.showerror("Ошибка", "Микрофон не доступен!")
            return
            
        self.listening = True
        self.start_btn.config(text="⏹️ Остановить запись")
        self.record_indicator.config(text="🟢 ЗАПИСЬ ИДЁТ... ГОВОРИТЕ", foreground='green')
        self.status_var.set("🎤 Запись начата... Говорите естественно!")
        
        self.record_thread = threading.Thread(target=self.record_audio)
        self.record_thread.daemon = True
        self.record_thread.start()
        
        self.process_thread = threading.Thread(target=self.process_audio)
        self.process_thread.daemon = True
        self.process_thread.start()

    def stop_listening(self):
        self.listening = False
        self.start_btn.config(text="🎤 Начать запись")
        self.record_indicator.config(text="🔴 НЕ ЗАПИСЫВАЕТ", foreground='red')
        self.status_var.set("⏸️ Запись остановлена")

    def record_audio(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            while self.listening:
                try:
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    self.audio_queue.put(audio)
                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    if self.listening:
                        self.root.after(0, lambda e=e: self.status_var.set(f"⚠️ Ошибка записи: {str(e)}"))
                    continue

    def process_audio(self):
        while self.listening:
            try:
                audio = self.audio_queue.get(timeout=1)
                text = self.recognizer.recognize_google(audio, language="ru-RU")
                processed_text = self.process_text(text)
                
                if self.instant_paste(processed_text.strip()):
                    self.root.after(0, lambda t=text: self.status_var.set(f"✅ Вставлено: {t}"))
                else:
                    self.root.after(0, lambda: self.status_var.set("⚠️ Не удалось вставить — используйте Ctrl+V"))
                
                self.root.after(0, self.update_text, processed_text)
                
            except sr.UnknownValueError:
                self.root.after(0, lambda: self.status_var.set("❌ Речь не распознана"))
            except sr.RequestError as e:
                self.root.after(0, lambda e=e: self.status_var.set(f"❌ Ошибка сервиса: {str(e)}"))
            except Exception as e:
                self.root.after(0, lambda e=e: self.status_var.set(f"⚠️ Ошибка обработки: {str(e)}"))
            except queue.Empty:
                continue

    def update_text(self, text):
        self.current_text += text
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, self.current_text)
        self.copy_to_clipboard()
        self.update_stats()
        self.text_area.see(tk.END)

    def smart_correct(self):
        if not self.current_text.strip():
            return
        
        text = self.current_text.strip()
        text = self.correct_spelling(text)
        text = self.smart_punctuation(text)
        text = self.capitalize_sentences(text)
        if text and text[-1] not in '.!?':
            text += '.'
        text = re.sub(r'\s+', ' ', text).strip()
        
        self.current_text = text
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, self.current_text)
        self.copy_to_clipboard()
        self.update_stats()
        self.status_var.set("✨ Текст автоматически исправлен!")

    def clear_text(self):
        self.current_text = ""
        self.text_area.delete(1.0, tk.END)
        pyperclip.copy("")
        self.update_stats()
        self.status_var.set("🧹 Текст очищен")

    def copy_to_clipboard(self):
        if self.current_text.strip():
            pyperclip.copy(self.current_text.strip())
            self.status_var.set("📋 Текст скопирован в буфер обмена!")

    def toggle_english(self):
        self.english_mode = not self.english_mode
        status = "ВКЛ" if self.english_mode else "ВЫКЛ"
        self.lang_btn.config(text=f"🔤 Англ. режим: {status}")
        mode_name = "Английский" if self.english_mode else "Русский"
        self.status_var.set(f"🔤 Режим ввода: {mode_name}")

    def on_closing(self):
        self.listening = False
        try:
            keyboard.remove_hotkey('f12')
        except:
            pass
        time.sleep(0.5)
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = SmartInstantVoiceNotepad(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
