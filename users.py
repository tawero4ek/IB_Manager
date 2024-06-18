# users.py
import tkinter as tk
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

if __name__ == "__main__":
    # Example usage if running this script directly
    users_file = 'Src/Users.usr'  # Adjust the path as per your project structure
    add_rights(users_file)
    modified_content = modify_users_file(users_file)
    if modified_content:
        print(f"Modified content of Users.usr:\n{modified_content}")
