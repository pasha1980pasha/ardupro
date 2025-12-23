import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import speech_recognition as sr
import threading
import pyperclip
import time

class VoiceNotepadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎤 Голосовой Блокнот - Непрерывная запись")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        self.recognizer = sr.Recognizer()
        self.listening = False
        self.current_text = ""
        self.is_speaking = False
        
        # Настройка распознавателя для лучшего качества
        self.recognizer.energy_threshold = 300  # Чувствительность к голосу
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 1.5   # Пауза для окончания фразы
        
        # Стиль
        style = ttk.Style()
        style.configure('TButton', font=('Arial', 10), padding=6)
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#f0f0f0')
        
        # Заголовок
        title_label = ttk.Label(root, text="🎤 ГОЛОСОВОЙ БЛОКНОТ (НЕПРЕРЫВНЫЙ)", style='Title.TLabel')
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
        
        # Индикатор записи
        self.record_indicator = ttk.Label(root, text="🔴 НЕ ЗАПИСЫВАЕТ", font=('Arial', 12, 'bold'), foreground='red')
        self.record_indicator.pack(pady=5)
        
        # Метка для текста
        text_label = ttk.Label(root, text="Распознанный текст:", font=('Arial', 10, 'bold'))
        text_label.pack(pady=(10, 5))
        
        # Текстовое поле
        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=90, height=18, 
                                                  font=('Arial', 11), bg='white', relief=tk.SUNKEN, bd=2)
        self.text_area.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        self.text_area.insert(tk.END, "Здесь появится распознанный текст...\n\n")
        
        # Статус бар
        self.status_var = tk.StringVar()
        self.status_var.set("✅ Готов к работе! Нажмите 'Начать запись'")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Инструкция
        instruction_text = """💡 КАК ИСПОЛЬЗОВАТЬ:
1. Нажмите 'Начать запись' 
2. ГОВОРИТЕ непрерывно - запись будет идти пока вы говорите
3. Когда закончите фразу - сделайте паузу 1-2 секунды
4. Текст автоматически появится здесь и скопируется в буфер
5. Чтобы остановить запись - нажмите 'Остановить'"""
        
        instruction = ttk.Label(root, text=instruction_text, font=('Arial', 9), 
                               background='#e8f4f8', wraplength=750, justify=tk.LEFT)
        instruction.pack(pady=10, padx=10)
        
        # Проверяем микрофон
        try:
            self.microphone = sr.Microphone(device_index=0)
            mic_list = sr.Microphone.list_microphone_names()
            if mic_list:
                print(f"Используется микрофон: {mic_list[0]}")
                self.status_var.set(f"✅ Микрофон: {mic_list[0]}")
            else:
                self.microphone = None
                self.start_btn.config(state='disabled')
                self.status_var.set("❌ Микрофон не найден!")
        except Exception as e:
            self.microphone = None
            self.start_btn.config(state='disabled')
            self.status_var.set(f"❌ Ошибка микрофона: {str(e)}")
    
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
        self.status_var.set("🎤 Запись начата... Говорите непрерывно!")
        
        self.thread = threading.Thread(target=self.continuous_listen)
        self.thread.daemon = True
        self.thread.start()
    
    def stop_listening(self):
        self.listening = False
        self.start_btn.config(text="🎤 Начать запись")
        self.record_indicator.config(text="🔴 НЕ ЗАПИСЫВАЕТ", foreground='red')
        self.status_var.set("⏸️ Запись остановлена")
    
    def continuous_listen(self):
        """Непрерывное прослушивание с автоматическим определением конца речи"""
        with self.microphone as source:
            # Настройка для уменьшения шума
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            while self.listening:
                try:
                    # Слушаем с более длинным временем паузы для непрерывной речи
                    audio = self.recognizer.listen(source, timeout=None, 
                                                 phrase_time_limit=10)  # Макс 10 секунд на фразу
                    
                    # Распознаем речь
                    text = self.recognizer.recognize_google(audio, language="ru-RU")
                    
                    # Обновляем интерфейс в основном потоке
                    self.root.after(0, self.update_text, text)
                    self.root.after(0, lambda: self.status_var.set(f"✅ Распознано: {text}"))
                    
                except sr.WaitTimeoutError:
                    # Таймаут - просто продолжаем слушать
                    continue
                except sr.UnknownValueError:
                    # Не удалось распознать - продолжаем
                    self.root.after(0, lambda: self.status_var.set("❌ Не удалось распознать речь"))
                    continue
                except Exception as e:
                    self.root.after(0, lambda: self.status_var.set(f"⚠️ Ошибка: {str(e)}"))
                    time.sleep(1)
    
    def update_text(self, text):
        # Добавляем новую распознанную фразу
        if self.current_text:
            self.current_text += " " + text
        else:
            self.current_text = text
        
        # Обновляем текстовое поле
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, self.current_text)
        
        # Автоматически копируем в буфер
        self.copy_to_clipboard()
        
        # Прокручиваем вниз
        self.text_area.see(tk.END)
    
    def clear_text(self):
        self.current_text = ""
        self.text_area.delete(1.0, tk.END)
        pyperclip.copy("")
        self.status_var.set("🧹 Текст очищен")
        self.text_area.insert(tk.END, "Текст очищен. Начните запись снова...")
    
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
