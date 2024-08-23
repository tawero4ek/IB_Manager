#Какая же это все хуйня, миллион хэшей и суммы весов. Я ебал, но может потом userы будут добавлены, пока тока докидывает права и НАХУЙ ОБНОВЛЯЕТСЯ 

import os
import tkinter as tk
from tkinter import filedialog, messagebox
import hashlib
import zlib

def compute_crc16(data):
    """Computes CRC16 of the given data."""
    return zlib.crc32(data.encode('utf-8')) & 0xFFFF

def compute_sha256(data):
    """Computes SHA256 hash of the given data."""
    sha256 = hashlib.sha256()
    sha256.update(data.encode('utf-8'))
    return sha256.digest().decode('latin1')

def add_rights(users_file):
    new_rights = "CfgEvViewer,Control,Print,QuitAlarm,SetPoints,Simulate,ViewArj"
    existing_rights = set()

    try:
        # Read existing content and extract current rights list
        with open(users_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.splitlines()
        
        for line in lines:
            if '<RightsList Items="' in line:
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

        # Replace existing RightsList line and update hash and CRC16
        new_lines = []
        for line in lines:
            if '<RightsList Items="' in line:
                new_lines.append(rights_line)
            else:
                new_lines.append(line)
        
        new_content = "\n".join(new_lines)
        new_hash = compute_sha256(new_content)
        new_crc16 = compute_crc16(new_content)
        
        # Update the Hash and CRC16 values in the content
        new_content = new_content.replace(
            'Hash="N7fHKA51dH2qDBpP2XsNL9nEN4+xumBab8l0lLiMljQ="', f'Hash="{new_hash}"'
        ).replace(
            'CRC16="44024"', f'CRC16="{new_crc16}"'
        )
        
        # Write back to the file
        with open(users_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        messagebox.showinfo("Добавление прав", "Права добавлены в файл Users.usr и обновлены Hash и CRC16")

    except FileNotFoundError:
        messagebox.showerror("Ошибка", f"Файл {users_file} не найден.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")