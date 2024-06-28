import os
import hashlib
from dotenv import load_dotenv
import platform

# ПЕРЕД РЕЛИЗОМ УДАЛИТЬ НАХУЙ ВСЕ PRINT ОТСЮДА


# Загрузить переменные окружения из файла .env
load_dotenv()
# Получить значение KEY из .env
key = os.getenv("KEY")
hash_path = os.getenv("HASH_PATH")
hash_filename = os.getenv("HASH_FILE_NAME")
# Имена разрешенных компов
ALLOWED_COMPUTER_NAMES = ["SPB-CHEPUSOV1",
                          "SPB-DENISENKO",
                          "LAPTO"]


# Функция проверки имени компа в списке разрешенных
def check_computer_access():
    def get_current_computer_name():
        return os.getenv('COMPUTERNAME')

    current_computer_name = get_current_computer_name()

    if current_computer_name:
        print("Имя текущего компьютера:", current_computer_name)

        if current_computer_name in ALLOWED_COMPUTER_NAMES:
            return True
        else:
            print("Имя компьютера не в списке доступа.")
            return False
    else:
        print("Не удалось получить имя компьютера.")
        return False


# Функция проверки наличия активирующего файла
def check_activator():
    if not key or not hash_path or not hash_filename:
        print("Недостаточно информации в .env файле или отсутствует файл с хешем.")
        return False
    try:
        with open(os.path.join(hash_path, hash_filename), 'r') as file:
            stored_hashed_key = file.read().strip()
            hashed_key = hashlib.sha256(key.encode()).hexdigest()
            return stored_hashed_key == hashed_key
    except FileNotFoundError:
        print("Файл с хешем не найден.")
        return False
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return False


# Заготовка для проверки даты и удаления файлов если она истекла
def check_data_demo():
    pass


# Проверочка что скуфы запускают скрипт из под винды
def check_windows():
    return platform.system() == 'Windows'


def isRun():
    return (check_activator() or check_computer_access()) and check_windows