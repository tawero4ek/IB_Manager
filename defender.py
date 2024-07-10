import os
import hashlib
from dotenv import load_dotenv
import platform
import sys

def get_base_path():
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.abspath(".")
# Загрузить переменные окружения из файла .env
base_path = get_base_path()
env_path = os.path.join(base_path, '.env')
load_dotenv(env_path)
# Получить значение KEY из .env
key = os.getenv("KEY")
hash_path = os.getenv("HASH_PATH")
hash_filename = os.getenv("HASH_FILE_NAME")
# Имена разрешенных компов
ALLOWED_COMPUTER_NAMES = ["SPB-CHEPUSOV1",
                          "SPB-DENISENKO",
                          "SPB-MYLOV",
                          "SPB-SHEGLOV",
                          "SPB-VERSHININ",
                          "SPB-ERSHOV",
                          "SPB-NIKITIN",
                          "SPB-VASILIEV",
                          "SPB-NIKITIN",]


# Функция проверки имени компа в списке разрешенных
def check_computer_access():
    def get_current_computer_name():
        return os.getenv('COMPUTERNAME')

    current_computer_name = get_current_computer_name()

    if current_computer_name:
        if current_computer_name in ALLOWED_COMPUTER_NAMES:
            return True
        else:
            return False
    else:
        return False


# Функция проверки наличия активирующего файла
def check_activator():
    if not key or not hash_path or not hash_filename:
        return False
    try:
        with open(os.path.join(hash_path, hash_filename), 'r') as file:
            stored_hashed_key = file.read().strip()
            hashed_key = hashlib.sha256(key.encode()).hexdigest()
            return stored_hashed_key == hashed_key
    except FileNotFoundError:
        return False
    except Exception as e:
        return False


# Заготовка для проверки даты и удаления файлов если она истекла
def check_data_demo():
    pass


# Проверочка что запускают скрипт из под винды
def check_windows():
    return platform.system() == 'Windows'


def isRun():
    return (check_activator() or check_computer_access()) and check_windows

def get_allowed_computer_name():
    if check_computer_access():
        return os.getenv('COMPUTERNAME')
    else:
        return None