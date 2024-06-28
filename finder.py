import re


def read_names_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file.readlines() if line.strip()]
    except IOError as e:
        print(f"Error opening file {file_path}: {e}")
        return []


def find_hid_to_hide(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            matches = []
            fb_type_name = None

            for line in lines:
                if 'Name="' in line:
                    match = re.search(r'Name="([^"]*)"( Comment="[^"]*")? ShowVarTypes="([^"]*)"', line)
                    if match:
                        fb_type_name = match.group(1)

                if '<Connection Source="' in line and '.hid" Destination="' in line and '.hide"' in line:
                    source_match = re.search(r'Source="([^"]+)"', line)
                    if source_match:
                        source_name = source_match.group(1).split('.')[0]  # Extract the block name before the '.hid'
                        if fb_type_name:
                            matches.append(f"Название окна = \"{fb_type_name}\" Имя блока = \"{source_name}\"")

            return matches
    except IOError as e:
        print(f"Error opening file: {e}")
        return None


def find_window_usage(file_path, graphics_label_file=None, subwindow_label_file=None):
    try:
        graphics_names = read_names_from_file(graphics_label_file) if graphics_label_file else []
        subwindow_names = read_names_from_file(subwindow_label_file) if subwindow_label_file else []
        all_names = graphics_names + subwindow_names

        matches = []
        fb_type_name = None
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                if 'Name="' in line:
                    match = re.search(r'Name="([^"]*)" ShowVarTypes=', line)
                    if match:
                        fb_type_name = match.group(1)
                for name in all_names:
                    if f'Type="{name}"' in line:
                        source_match = re.search(r'Type="([^"]*)" TypeUUID=', line)
                        if source_match:
                            source_name = source_match.group(1).split('.')[0]
                            if fb_type_name:
                                matches.append(f"Блок = \"{source_name}\" Используется в окне = \"{fb_type_name}\"")

        return matches
    except IOError as e:
        print(f"Error opening file: {e}")
        return None
    

import re

def find_unused_windows(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        windows_to_check = set(re.findall(r'Name="([^"]*)" ShowVarTypes=', content))
        used_windows = set(re.findall(r'Type="([^"]*)" TypeUUID=', content))

        # Определить неиспользуемые окна
        unused_windows = windows_to_check - used_windows

        return list(unused_windows)
    except IOError as e:
        print(f"Error opening file: {e}")
        return None

    