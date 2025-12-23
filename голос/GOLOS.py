import speech_recognition as sr
import pyautogui
import time
import threading

recognizer = sr.Recognizer()
microphone = sr.Microphone()

listening = True
current_phrase = ""  # Храним собранный текст до завершения фразы

def listen_and_type():
    global listening, current_phrase

    print("🎙️ Готов к прослушиванию...")
    print("📌 КЛИКНИ МЫШКОЙ В ЛЮБОЕ ПОЛЕ ВВОДА (Блокнот, Chrome, Telegram)")
    print("🗣️ Говори нормально — я буду слушать, пока ты не замолчишь")
    print("✅ Когда закончишь — я автоматически введу всё, что ты сказал")
    print("🛑 Нажми ENTER в этой консоли, чтобы остановить\n")

    while listening:
        try:
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("⏳ Слушаю... (говори, не торопись)")

                # Слушаем, пока не будет 1+ секунды тишины
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=15)

            # Распознаём речь
            text = recognizer.recognize_google(audio, language="ru-RU")
            print(f"👂 Распознано: '{text}'")

            # Добавляем новую фразу к накопленной
            if current_phrase:
                current_phrase += " " + text
            else:
                current_phrase = text

            # 👇 ЭТО ВАЖНО: НЕ ВВОДИМ СРАЗУ! ЖДЕМ, ПОКА ТЫ НЕ ЗАМОЛЧИШЬ
            print(f"📝 Накоплено: {current_phrase}")
            print("💬 Продолжай говорить... или просто помолчи 2 сек — я введу текст.")

            # Ждём 2 секунды молчания — если ничего не пришло — считаем, что фраза закончилась
            time.sleep(2)

            # Если за 2 секунды ничего не услышали — вводим накопленный текст
            # Но только если он не пустой
            if current_phrase.strip():
                print(f"\n✅ ФРАЗА ЗАВЕРШЕНА! ВВОЖУ: {current_phrase}\n")
                pyautogui.write(current_phrase + " ", interval=0.05)
                current_phrase = ""  # Очищаем буфер

        except sr.WaitTimeoutError:
            # Если микрофон ничего не услышал — продолжаем слушать
            print("💤 Ничего не услышано — продолжаю слушать...")
            continue
        except sr.UnknownValueError:
            print("❌ Не смог разобрать речь — попробуй ещё раз.")
            continue
        except sr.RequestError as e:
            print(f"🌐 Ошибка сервиса Google: {e}")
            continue
        except Exception as e:
            print(f"⚠️ Ошибка: {e}")

def stop_listening():
    global listening
    input("\nНажми ENTER, чтобы выйти...\n")
    listening = False
    print("\n🛑 Программа остановлена.")

# Запускаем фоновый поток
listener_thread = threading.Thread(target=listen_and_type, daemon=True)
listener_thread.start()

# Ждём команду на выход
stop_listening()
