import time
import pyautogui
import pyperclip

print("⏳ Через 3 секунды я вставлю 'ТЕСТ-123' через буфер обмена...")
time.sleep(3)

# 👇 КОПИРУЕМ ТЕКСТ В БУФЕР ОБМЕНА — НЕ ЗАВИСИТ ОТ РАСКЛАДКИ!
pyperclip.copy("ТЕСТ-123")

# 👇 ВСТАВЛЯЕМ КАК Ctrl+V — РАБОТАЕТ ВЕЗДЕ!
pyautogui.hotkey('ctrl', 'v')

print("✅ Готово! Проверь Блокнот.")
