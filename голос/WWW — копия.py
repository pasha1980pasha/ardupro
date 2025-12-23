import time
import pyautogui

def type_text():
    # Запрашиваем текст у пользователя
    text_to_write = input("Введите текст для печати: ")
    
    # Запрашиваем время ожидания
    wait_time = int(input("Время ожидания (секунды): "))
    
    print(f"⏳ Переключитесь на нужное окно в течение {wait_time} секунд...")
    time.sleep(wait_time)
    
    # Печатаем текст
    pyautogui.write(text_to_write)
    print(f"✅ Текст '{text_to_write}' напечатан!")

if __name__ == "__main__":
    type_text()
