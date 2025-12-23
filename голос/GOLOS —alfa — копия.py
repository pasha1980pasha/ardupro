import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import speech_recognition as sr
import threading
import pyperclip
import time
import re
from collections import deque

class VoiceNotepadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎤 Голосовой Блокнот - С умной пунктуацией")
        self.root.geometry("900x650")
        self.root.configure(bg='#f0f0f0')
        
        self.recognizer = sr.Recognizer()
        self.listening = False
        self.current_text = ""
        self.last_words = deque(maxlen=5)  # Для анализа последних слов
        
        # Настройка распознавателя
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 1.2
        
        # Стиль
        style = ttk.Style()
        style.configure('TButton', font=('Arial', 10), padding=6)
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#f0f0f0')
        
        # Заголовок
        title_label = ttk.Label(root, text="🎤 УМНЫЙ ГОЛОСОВОЙ БЛОКНОТ", style='Title.TLabel')
        title_label.pack(pady=10)
        
        # Фрейм для кнопок
        button_frame = ttk.Frame(root)
        button_frame.pack(pady=10)
        
        # Кнопки
        self.start_btn = ttk.Button(button_frame, text="🎤 Начать запись", command=self.toggle_recording)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(button_frame, text="🧹 Очистить", command=self.clear_text)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        self.copy_btn = ttk.Button(button_frame, text="📋 Скопировать", command=self.copy_to_clipboard)
        self.copy_btn.pack(side=tk.LEFT, padx=5)
        
        self.fix_btn = ttk.Button(button_frame, text="✨ Исправить текст", command=self.auto_correct)
        self.fix_btn.pack(side=tk.LEFT, padx=5)
        
        # Индикатор записи
        self.record_indicator = ttk.Label(root, text="🔴 НЕ ЗАПИСЫВАЕТ", font=('Arial', 12, 'bold'), foreground='red')
        self.record_indicator.pack(pady=5)
        
        # Метка для текста
        text_label = ttk.Label(root, text="Распознанный текст (автоматическая пунктуация):", font=('Arial', 10, 'bold'))
        text_label.pack(pady=(10, 5))
        
        # Текстовое поле
        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=100, height=20, 
                                                  font=('Arial', 11), bg='white', relief=tk.SUNKEN, bd=2)
        self.text_area.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        self.text_area.insert(tk.END, "Здесь появится текст с автоматическими знаками препинания...\n\n")
        
        # Статус бар
        self.status_var = tk.StringVar()
        self.status_var.set("✅ Готов к работе! Нажмите 'Начать запись'")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Инструкция
        instruction_text = """💡 КАК ИСПОЛЬЗОВАТЬ:
1. Нажмите 'Начать запись' - говорите естественно
2. Программа сама добавит точки, запятые и исправит ошибки
3. Скажите 'точка' или 'запятая' для ручной пунктуации
4. Используйте 'Исправить текст' для финальной коррекции
5. Скопируйте готовый текст в любое приложение"""
        
        instruction = ttk.Label(root, text=instruction_text, font=('Arial', 9), 
                               background='#e8f4f8', wraplength=850, justify=tk.LEFT)
        instruction.pack(pady=10, padx=10)
        
        # Проверяем микрофон
        try:
            self.microphone = sr.Microphone(device_index=0)
            mic_list = sr.Microphone.list_microphone_names()
            if mic_list:
                self.status_var.set(f"✅ Микрофон: {mic_list[0]}")
            else:
                self.microphone = None
                self.start_btn.config(state='disabled')
                self.status_var.set("❌ Микрофон не найден!")
        except Exception as e:
            self.microphone = None
            self.start_btn.config(state='disabled')
            self.status_var.set(f"❌ Ошибка микрофона: {str(e)}")
    
    def add_punctuation(self, text):
        """Автоматическая расстановка знаков препинания"""
        text = text.lower().strip()
        
        # Команды для пунктуации
        punctuation_commands = {
            'точка': '.', 'точку': '.', 'точки': '.',
            'запятая': ',', 'запятую': ',', 'запятые': ',',
            'восклицательный знак': '!', 'вопросительный знак': '?',
            'двоеточие': ':', 'тире': ' - ', 'новая строка': '\n',
            'кавычки': '"', 'скобки': '()', 'точка с запятой': ';'
        }
        
        # Проверяем команды пунктуации
        for command, symbol in punctuation_commands.items():
            if command in text:
                return symbol
        
        # Автоматическая пунктуация на основе содержания
        question_words = {'кто', 'что', 'где', 'когда', 'почему', 'как', 'сколько', 'чей', 'какой'}
        words = text.split()
        
        if len(words) > 0:
            # Вопросы
            if any(word in question_words for word in words[:2]):
                return '?'
            
            # Восклицания
            if any(word in {'ого', 'ух', 'ах', 'вау', 'здорово'} for word in words):
                return '!'
            
            # Длинные фразы - запятая
            if len(words) > 6 and text[-1] not in {'.', '!', '?'}:
                return ','
        
        return ''
    
    def auto_correct_text(self, text):
        """Автоматическое исправление распространенных ошибок"""
        corrections = {
            'скопироаноо': 'скопировано',
            'привет': 'привет',
            'какдела': 'как дела',
            'спасибо': 'спасибо',
            'пожалуйста': 'пожалуйста',
            'здравствуйте': 'здравствуйте',
            'извините': 'извините',
            'хорошо': 'хорошо',
            'плохо': 'плохо',
            'нормально': 'нормально'
        }
        
        # Исправляем слитные слова
        for wrong, correct in corrections.items():
            text = text.replace(wrong, correct)
        
        return text
    
    def process_text(self, text):
        """Обработка и улучшение текста"""
        text = text.lower().strip()
        
        # Исправляем орфографию
        text = self.auto_correct_text(text)
        
        # Добавляем пунктуацию
        punctuation = self.add_punctuation(text)
        
        # Убираем команды пунктуации из текста
        for command in {'точка', 'запятая', 'восклицательный', 'вопросительный', 
                       'двоеточие', 'тире', 'новая строка', 'кавычки', 'скобки'}:
            text = text.replace(command, '')
        
        text = text.strip()
        
        if punctuation:
            if punctuation in {'.', '!', '?', ';', ':'}:
                return text + punctuation + ' '
            elif punctuation == ',':
                return text + punctuation + ' '
            else:
                return punctuation + text + ' '
        else:
            return text + ' '
    
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
        
        self.thread = threading.Thread(target=self.continuous_listen)
        self.thread.daemon = True
        self.thread.start()
    
    def stop_listening(self):
        self.listening = False
        self.start_btn.config(text="🎤 Начать запись")
        self.record_indicator.config(text="🔴 НЕ ЗАПИСЫВАЕТ", foreground='red')
        self.status_var.set("⏸️ Запись остановлена")
    
    def continuous_listen(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            while self.listening:
                try:
                    audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=8)
                    text = self.recognizer.recognize_google(audio, language="ru-RU")
                    
                    # Обрабатываем текст
                    processed_text = self.process_text(text)
                    
                    self.root.after(0, self.update_text, processed_text)
                    self.root.after(0, lambda: self.status_var.set(f"✅ Обработано: {text}"))
                    
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    self.root.after(0, lambda: self.status_var.set("❌ Речь не распознана"))
                    continue
                except Exception as e:
                    self.root.after(0, lambda: self.status_var.set(f"⚠️ Ошибка: {str(e)}"))
                    time.sleep(1)
    
    def update_text(self, text):
        self.current_text += text
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, self.current_text.capitalize())
        self.copy_to_clipboard()
        self.text_area.see(tk.END)
    
    def auto_correct(self):
        """Дополнительная коррекция текста"""
        if self.current_text:
            # Делаем первую букву заглавной
            if self.current_text and self.current_text[0].islower():
                self.current_text = self.current_text[0].upper() + self.current_text[1:]
            
            # Добавляем точку в конце если нет пунктуации
            if self.current_text.strip() and self.current_text[-1] not in {'.', '!', '?', ',', ';', ':'}:
                self.current_text = self.current_text.strip() + '.'
            
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, self.current_text)
            self.copy_to_clipboard()
            self.status_var.set("✨ Текст автоматически исправлен!")
    
    def clear_text(self):
        self.current_text = ""
        self.text_area.delete(1.0, tk.END)
        pyperclip.copy("")
        self.status_var.set("🧹 Текст очищен")
    
    def copy_to_clipboard(self):
        if self.current_text.strip():
            pyperclip.copy(self.current_text.strip())
            self.status_var.set("📋 Текст скопирован в буфер обмена!")
    
    def on_closing(self):
        self.listening = False
        time.sleep(0.5)
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceNotepadApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
