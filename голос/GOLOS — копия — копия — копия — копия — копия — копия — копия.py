import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import speech_recognition as sr
import threading
import pyperclip
import time

class VoiceNotepadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎤 Голосовой Блокнот")
        self.root.geometry("700x550")
        self.root.configure(bg='#f0f0f0')
        
        self.recognizer = sr.Recognizer()
        self.listening = False
        self.current_text = ""
        
        # Стиль
        style = ttk.Style()
        style.configure('TButton', font=('Arial', 10), padding=6)
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#f0f0f0')
        
        # Заголовок
        title_label = ttk.Label(root, text="🎤 ГОЛОСОВОЙ БЛОКНОТ", style='Title.TLabel')
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
        
        # Метка для текста
        text_label = ttk.Label(root, text="Распознанный текст:", font=('Arial', 10, 'bold'))
        text_label.pack(pady=(20, 5))
        
        # Текстовое поле
        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=15, 
                                                  font=('Arial', 11), bg='white', relief=tk.SUNKEN, bd=2)
        self.text_area.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        self.text_area.insert(tk.END, "Здесь появится распознанный текст...")
        
        # Статус бар
        self.status_var = tk.StringVar()
        self.status_var.set("✅ Готов к работе! Нажмите 'Начать запись'")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Инструкция
        instruction = ttk.Label(root, text="💡 Как использовать: 1. Нажмите 'Начать запись' → 2. Говорите → 3. Текст появится здесь и скопируется в буфер",
                              font=('Arial', 9), background='#f8f9fa', wraplength=650)
        instruction.pack(pady=10, padx=10)
        
        # Проверяем микрофон
        try:
            self.microphone = sr.Microphone(device_index=0)
            mic_list = sr.Microphone.list_microphone_names()
            if mic_list:
                print(f"Используется микрофон: {mic_list[0]}")
            else:
                self.microphone = None
                self.start_btn.config(state='disabled')
                self.status_var.set("❌ Микрофон не найден!")
        except:
            self.microphone = None
            self.start_btn.config(state='disabled')
            self.status_var.set("❌ Ошибка микрофона!")
    
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
        self.start_btn.config(text="⏹️ Остановить")
        self.status_var.set("🎤 Запись начата... Говорите!")
        
        self.thread = threading.Thread(target=self.listen_loop)
        self.thread.daemon = True
        self.thread.start()
    
    def stop_listening(self):
        self.listening = False
        self.start_btn.config(text="🎤 Начать запись")
        self.status_var.set("⏸️ Запись остановлена")
    
    def listen_loop(self):
        while self.listening:
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=5)
                
                text = self.recognizer.recognize_google(audio, language="ru-RU")
                self.update_text(text)
                self.status_var.set(f"✅ Распознано: {text}")
                
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                self.status_var.set("❌ Не удалось распознать речь")
            except Exception as e:
                self.status_var.set(f"⚠️ Ошибка: {str(e)}")
    
    def update_text(self, text):
        self.current_text += " " + text
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, self.current_text.strip())
        self.copy_to_clipboard()
    
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
