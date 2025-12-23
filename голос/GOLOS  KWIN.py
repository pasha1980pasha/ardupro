
import speech_recognition as sr
import time
import threading
import pyautogui

# --- Конфиг ---
RECOGNITION_LANG = "ru-RU"
MIC_INDEX = 0  # Проверьте через print(sr.Microphone.list_microphone_names())

recognizer = sr.Recognizer()
microphone = sr.Microphone(device_index=MIC_INDEX)

listening = True
is_recording = False
current_speech_buffer = ""

def listen_and_display():
    global listening, is_recording, current_speech_buffer

    print("\n🎙️ Голосовой блокнот АКТИВЕН!")
    print("📝 Я буду вставлять ваш текст ТАМ, где сейчас курсор")
    print("🗣️ Команды: 'начало', 'очистка', 'стоп'")
    print("💡 Скажите 'начало' → говорите → текст вставится автоматически")
    print("⚠️ ⚠️ ⚠️ КЛИКНИТЕ ЛЕВОЙ КНОПКОЙ МЫШИ В БЛОКНОТ, WORD, TELEGRAM — НЕ В ТЕРМИНАЛ! ⚠️ ⚠️ ⚠️")
    print("\n⏳ Ожидаю команду...\n")

    while listening:
        try:
            print("🎤 ГОВОРИТЕ... (макс. 8 сек)")

            with microphone as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.3)
                audio = recognizer.listen(source, timeout=3, phrase_time_limit=8)

            text = recognizer.recognize_google(audio, language=RECOGNITION_LANG).lower().strip()
            print(f"✅ Услышал: '{text}'")

            if "стоп" in text:
                print("🛑 Выход")
                listening = False
                break

            elif "начало" in text:
                print("🚀 Начинаю запись...")
                print("=" * 50)
                is_recording = True
                current_speech_buffer = ""
                continue

            elif "очистка" in text:
                print("🧹 Текст очищен!")
                print("=" * 50)
                current_speech_buffer = ""
                continue

            if is_recording:
                current_speech_buffer += (" " + text).strip()

                # 👇 КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ: ЖДЁМ 0.5 СЕКУНД — ДАЁМ ЧЕЛОВЕКУ ВРЕМЯ ПЕРЕКЛЮЧИТЬ ФОКУС
                time.sleep(0.5)

                # 👇 ВСТАВЛЯЕМ ТОЛЬКО ЕСЛИ БУФЕР НЕ ПУСТ
                if current_speech_buffer.strip():
                    print(f"\n📥 Вставляю в курсор: '{current_speech_buffer}'")
                    pyautogui.write(current_speech_buffer)
                    pyautogui.press('enter')  # Перевод строки — лучше для редакторов
                    current_speech_buffer = ""  # Сбрасываем буфер

                print("🗣️ Продолжайте говорить или скажите 'очистка' / 'стоп'")
                time.sleep(0.7)

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

    print("\n🎙️ Голосовой блокнот остановлен.")

def stop_program():
    global listening
    print("\n▶️ Нажмите ENTER, чтобы остановить программу...")
    input()  # Ждёт ввода — не мешает потоку слушания
    listening = False
    print("🛑 Остановка запрошена...")

# Запуск
listener_thread = threading.Thread(target=listen_and_display, daemon=True)
listener_thread.start()

stop_program()

# Корректное завершение
listener_thread.join(timeout=5)
if listener_thread.is_alive():
    print("⚠️ Поток не завершился — принудительно завершаем.")
else:
    print("✅ Программа завершена корректно.")
