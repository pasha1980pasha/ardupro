import pyperclip
import os
import time
import subprocess

def smart_text_export():
    # Получаем текст
    try:
        text = pyperclip.paste()
        if not text.strip():
            text = "Текст не найден в буфере обмена"
    except:
        text = "Ошибка чтения буфера обмена"
    
    # Создаем временный файл
    temp_file = "последняя_запись.txt"
    
    # Записываем текст
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(text)
    
    print(f"📋 Текст сохранен в файл: {temp_file}")
    print("📖 Открываю блокнот...")
    
    # Открываем блокнот
    subprocess.Popen(['notepad.exe', temp_file])
    
    # Ждем немного и снова копируем текст в буфер
    time.sleep(2)
    pyperclip.copy(text)
    print("✅ Текст снова скопирован в буфер обмена!")
    print("🎯 Теперь можете вручную нажать Ctrl+V в нужном месте")

# Запускаем
smart_text_export()
