import os
import hashlib
from dotenv import load_dotenv

# ОТДЕЛЬНЫЙ МОДУЛЬ ДЛЯ ГЕНЕАРЦИИ ФАЙЛА АКТИВАЦИИ
load_dotenv()
# Получить значения из .env
key = os.getenv("KEY")
hash_path = os.getenv("HASH_PATH")
hash_filename = os.getenv("HASH_FILE_NAME")

if key and hash_path and hash_filename:
    try:
        # Вычислить хеш ключа
        hashed_key = hashlib.sha256(key.encode()).hexdigest()

        # Создать путь к файлу
        file_path = os.path.join(hash_path, hash_filename)

        # Проверить доступность папки и создать, если её нет
        if not os.path.exists(hash_path):
            os.makedirs(hash_path)

        # Создать и записать в файл хешированное значение ключа
        with open(file_path, 'w') as file:
            file.write(hashed_key)

        print(f"Хешированное значение ключа успешно записано в файл: {file_path}")
    except Exception as e:
        print(f"Ошибка при создании файла: {e}")
else:
    print("Недостаточно информации в .env файле для создания файла.")
