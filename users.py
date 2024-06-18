# users.py
from tkinter import messagebox


def add_rights(users_file):
    new_rights = "CfgEvViewer,Control,Print,QuitAlarm,SetPoints,Simulate,ViewArj"
    existing_rights = set()

    try:
        # Read existing content and extract current rights list
        with open(users_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line in lines:
            if line.strip().startswith('<RightsList Items="'):
                items_start = line.index('"') + 1
                items_end = line.rindex('"')
                existing_items = line[items_start:items_end].split(',')
                existing_rights.update(existing_items)

        # Check if new rights are already present
        new_rights_list = new_rights.split(',')
        for item in new_rights_list:
            if item in existing_rights:
                continue
            existing_rights.add(item)

        # Generate the updated RightsList string
        updated_rights = ','.join(sorted(existing_rights))
        rights_line = f'<RightsList Items="{updated_rights}" />\n'

        # Write back to the file
        with open(users_file, 'w', encoding='utf-8') as f:
            for line in lines:
                if line.strip().startswith('<RightsList Items="'):
                    f.write(rights_line)
                else:
                    f.write(line)

        messagebox.showinfo("Добавление прав", "Права добавлены в файл Users.usr")

    except FileNotFoundError:
        messagebox.showerror("Ошибка", f"Файл {users_file} не найден.")


def modify_users_file(users_file):
    try:
        with open(users_file, 'r') as f:
            content = f.read()
        messagebox.showinfo("Изменение файла", f"Содержимое файла Users.usr:\n{content}")
        return content
    except FileNotFoundError:
        messagebox.showerror("Ошибка", f"Файл {users_file} не найден.")
        return None

# соси хуй Никита блять c этой конструкцией ебанной ты нахуя ее везде пихаешь как обезьяна
# if __name__ == "__main__":
#     # Example usage if running this script directly
#     users_file = 'Src/Users.usr'  # Adjust the path as per your project structure
#     add_rights(users_file)
#     modified_content = modify_users_file(users_file)
#     if modified_content:
#         print(f"Modified content of Users.usr:\n{modified_content}")



# [Куплет 1]
# Я тебя растопчу и уничтожу, и будешь ты сморкать свою небритую рожу
# Ебало тебе разобью, и закроешься ты, а мои текста ложатся ровно на биты
# И Вечный даст тебе пизды, а я ему помогу
# И ты будешь сморкаться полгода
# Дрочиться с этим Ваней, ты крип ебаный
# Рот бы поприкрыл, а то тебе ёбнем все мы
#
# [Припев]
# Закрой свой рот ебучий, уёбок, сын ты сучий
# Закрой свой рот, я его наоборот, йоу
# Закрой свой рот ебучий, уёбок, сын ты сучий
# Закрой свой рот, я его наоборот
#
# [Куплет 2]
# Сука боротая, побрейся, бомж ебанный
# Пизды я тебе, нах, дам и район спалю я вместе с хатой
# Уёбок волосатый, ты хуй, бля, ебаный, закрой рот свой и убейся, блохастый
# Ебать, что же ты читаешь? Ты позоришь русский рэп
# Таких уёбков, как ты, на свете нет
# Пора в рот тебя ебать или вообще на хуй суку такую посылать
#
# [Припев]
# Закрой свой рот ебучий, уёбок, сын ты сучий
# Закрой свой рот, я его наоборот, йоу
# Закрой свой рот ебучий, уёбок, сын ты сучий
# Закрой свой рот, качайтесь, я его наоборот ведь