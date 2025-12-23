import speech_recognition as sr
import time
import threading
import pyperclip  # Добавляем для работы с буфером обмена

recognizer = sr.Recognizer()
microphone = sr.Microphone(device_index=0)

listening = True
is_recording = False
current_phrase = ""

def listen_and_display():
    global listening, is_recording, current_phrase

    print("🎙️ Голосовой блокнот АКТИВЕН!")
    print("📝 Текст автоматически копируется в буфер обмена")
    print("🗣️ Команды: 'начало', 'очистка', 'стоп'")
    print("📋 Просто вставьте (Ctrl+V) текст куда нужно!")
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
                print("=" * 50)
                is_recording = True
                current_phrase = ""
                time.sleep(1)
                continue
                
            elif "очистка" in text:
                print("🧹 Текст очищен!")
                print("=" * 50)
                current_phrase = ""
                pyperclip.copy("")  # Очищаем буфер обмена
                continue

            # Если идет запись - добавляем к тексту и копируем в буфер
            if is_recording:
                current_phrase += " " + text
                
                # Копируем в буфер обмена
                pyperclip.copy(current_phrase.strip())
                
                print(f"\n📋 ТЕКСТ СКОПИРОВАН В БУФЕР ОБМЕНА:")
                print("=" * 50)
                print(current_phrase)
                print("=" * 50)
                print("📋 Теперь просто вставьте (Ctrl+V) куда нужно!")
                print("🗣️ Продолжайте говорить или скажите 'очистка'")
                time.sleep(0.5)
            else:
                print("⚠️ Сначала скажите 'начало' для начала записи")

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
listener_thread = threading.Thread(target=listen_and_display)
listener_thread.start()

stop_listening()
print("🛑 Стоп")
