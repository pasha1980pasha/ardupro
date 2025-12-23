import speech_recognition as sr
import pyautogui
import time
import threading
import pyperclip  # для работы с буфером обмена

recognizer = sr.Recognizer()
microphone = sr.Microphone(device_index=0)

listening = True
is_recording = False
current_phrase = ""

def type_text_alternative(text):
    """Альтернативный метод печати через буфер обмена"""
    if not text.strip():
        return False
        
    try:
        print(f"🖨️ ПЕЧАТАЮ через буфер: '{text}'")
        
        # Сохраняем текст в буфер обмена
        pyperclip.copy(text)
        
        # Вставляем из буфера (Ctrl+V)
        pyautogui.hotkey('ctrl', 'v')
        
        print("✅ Текст напечатан через буфер обмена!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка печати: {e}")
        # Пробуем старый метод как запасной вариант
        try:
            pyautogui.write(text, interval=0.05)
            print("✅ Текст напечатан обычным методом!")
            return True
        except:
            return False

def type_text_direct(text):
    """Прямая печать символов"""
    if not text.strip():
        return False
        
    try:
        print(f"🖨️ ПЕЧАТАЮ напрямую: '{text}'")
        
        # Печатаем каждый символ отдельно
        for char in text:
            pyautogui.press(char)
            time.sleep(0.01)
            
        print("✅ Текст напечатан напрямую!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка прямой печати: {e}")
        return False

def listen_and_type():
    global listening, is_recording, current_phrase

    print("🎙️ Голосовая клавиатура АКТИВНА!")
    print("📌 ОТКРОЙТЕ БЛОКНОТ И КЛИКНИТЕ В НЕГО!")
    print("🗣️ Команды: 'начало', 'отправка', 'стоп', 'очистка'")
    print("🔧 Используем альтернативные методы печати")
    print("\n⏳ Ожидаю команду...\n")

    while listening:
        try:
            print("🎤 ГОВОРИТЕ...")
            
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.3)
                audio = recognizer.listen(source, timeout=3, phrase_time_limit=4)

            text = recognizer.recognize_google(audio, language="ru-RU").lower()
            print(f"✅ Услышал: '{text}'")

            # Обрабатываем команды
            if "стоп" in text:
                print("🛑 Выход")
                listening = False
                break
                
            elif "начало" in text:
                print("🚀 Начинаю запись...")
                is_recording = True
                current_phrase = ""
                time.sleep(1)
                continue
                
            elif "очистка" in text:
                print("🧹 Текст очищен!")
                current_phrase = ""
                continue
                
            elif "отправка" in text:
                if current_phrase.strip():
                    print("🔄 Пробую разные методы печати...")
                    
                    # Пробуем разные методы
                    success = type_text_alternative(current_phrase)
                    if not success:
                        success = type_text_direct(current_phrase)
                    
                    if success:
                        current_phrase = ""
                    else:
                        print("⚠️ Все методы печати не сработали!")
                else:
                    print("❌ Нет текста для отправки")
                is_recording = False
                time.sleep(1)
                continue

            # Если идет запись - добавляем к тексту
            if is_recording:
                current_phrase += " " + text
                print(f"📝 Текст: {current_phrase}")
                time.sleep(0.5)

        except sr.WaitTimeoutError:
            continue
        except sr.UnknownValueError:
            print("❌ Не разобрал речь")
            continue
        except Exception as e:
            print(f"⚠️ Ошибка: {e}")
            time.sleep(1)

def stop_listening():
    global listening
    input("\nНажми ENTER для остановки...\n")
    listening = False

# Запускаем
listener_thread = threading.Thread(target=listen_and_type)
listener_thread.start()

stop_listening()
print("🛑 Стоп")
