import os

ALLOWED_COMPUTER_NAMES = ["SPB-CHEPUSOV1",
                          "SPB-DENISENKO",
                          "Computer3"]


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



