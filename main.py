import re
import argparse
import glob
import os
import sys

def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()

def write_file(filename, content):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

def extract_var_decl(window_block, var_name):
    pattern = re.compile(fr'<VarDeclaration Name="{var_name}".*?/>', re.DOTALL)
    match = pattern.search(window_block)
    return match.group() if match else None

def merge_var_decl(existing_var, new_var):
    # Извлекаем InitialValue из существующей переменной
    initial_value_pattern = re.compile(r'InitialValue="(.*?)"')
    initial_value_match = initial_value_pattern.search(existing_var)
    initial_value = initial_value_match.group(1) if initial_value_match else None

    if initial_value:
        # Вставляем InitialValue в новую переменную
        new_var = re.sub(r'InitialValue=".*?"', f'InitialValue="{initial_value}"', new_var)

    return new_var

def get_tabulation():
    return ' ' * 24  # Возвращаем 24 пробела для нужной табуляции

# Блок замены на GraphicsComposite
def process_graphics(iec_hmi_content, graphics_composite_content):
    # Получаем названия окон из GraphicsCompositeType.txt
    window_names = graphics_composite_content.strip().split('\n')

    for window_name in window_names:
        # Ищем блоки WindowFBType и GraphicsCompositeFBType
        window_pattern = re.compile(fr'<WindowFBType Name="{window_name}".*?</WindowFBType>', re.DOTALL)
        graphics_pattern = re.compile(r'<GraphicsCompositeFBType Name="TNewGraphicsCompositeType".*?</GraphicsCompositeFBType>', re.DOTALL)

        window_match = window_pattern.search(iec_hmi_content)
        graphics_match = graphics_pattern.search(iec_hmi_content)

        if window_match and graphics_match:
            window_block = window_match.group()
            graphics_block = graphics_match.group()

            # Замена WindowFBType на GraphicsCompositeFBType
            updated_window_block = window_block.replace('<WindowFBType', '<GraphicsCompositeFBType').replace('</WindowFBType>', '</GraphicsCompositeFBType>')
            # Удаление старых строк <VarDeclaration Name="pos", <VarDeclaration Name="visible", <VarDeclaration Name="size"
            updated_window_block = re.sub(r'<VarDeclaration Name="(pos|visible|size)".*?/>', '', updated_window_block, count=3)
            # Извлекаем содержимое <EventOutputs> из GraphicsCompositeFBType
            graphics_event_outputs = re.search(r'<EventOutputs>(.*?)</EventOutputs>', graphics_block, re.DOTALL).group(1)

            # Добавляем содержимое <EventOutputs> из GraphicsCompositeFBType в <EventOutputs> из WindowFBType
            updated_window_block = re.sub(r'(<EventOutputs>)(.*?)(</EventOutputs>)', fr'\1\n{graphics_event_outputs}\2\3', updated_window_block, count=1, flags=re.DOTALL)

            # Извлекаем необходимые VarDeclaration из GraphicsCompositeFBType
            new_vars_pattern = re.compile(r'(<VarDeclaration Name="(zValue|hint|moveable|enabled|angle)".*?/>|<VarDeclaration Name="(pos|visible|size)".*?InitialValue=".*?".*?/>|<VarDeclaration Name="(pos|visible|size)".*?/>)(?!<VarDeclaration Name="(initialValue)".*?)', re.DOTALL)
            new_vars = new_vars_pattern.findall(graphics_block)
            new_vars_text = ''
            tabulation = get_tabulation()
            for match in new_vars:
                var = match[0]
                # Для переменных pos, visible, и size мы сохраняем существующий InitialValue
                if 'Name="pos"' in var or 'Name="visible"' in var or 'Name="size"' in var:
                    existing_var = extract_var_decl(window_block, re.search(r'Name="(.*?)"', var).group(1))
                    if existing_var:
                        var = merge_var_decl(existing_var, var)
                # Добавляем VarDeclaration с нужной табуляцией  
                new_vars_text += f'{tabulation}{var.strip()}\n'
            # Вставляем новые VarDeclaration в первый блок <InputVars>
            updated_window_block = re.sub(r'(<GraphicsCompositeFBType .*?<InputVars>)(.*?)(</InputVars>)', fr'\1\n{new_vars_text}{tabulation}\2\3', updated_window_block, count=1, flags=re.DOTALL)

            # Замена старого блока на обновленный
            iec_hmi_content = iec_hmi_content.replace(window_block, updated_window_block)

    return iec_hmi_content

# Блок замены на SubWindow
def process_subwindow(iec_hmi_content, sub_window_content):
    # Получаем названия окон из TType.txt
    window_names = sub_window_content.strip().split('\n')

    for window_name in window_names:
        # Ищем блоки WindowFBType и SubWindowFBType
        window_pattern = re.compile(fr'<WindowFBType Name="{window_name}".*?</WindowFBType>', re.DOTALL)
        graphics_pattern = re.compile(r'<SubWindowFBType Name="TNewSubWindow".*?</SubWindowFBType>', re.DOTALL)

        window_match = window_pattern.search(iec_hmi_content)
        graphics_match = graphics_pattern.search(iec_hmi_content)

        if window_match and graphics_match:
            window_block = window_match.group()
            graphics_block = graphics_match.group()

            # Замена WindowFBType на SubWindowFBType
            updated_window_block = window_block.replace('<WindowFBType', '<SubWindowFBType').replace('</WindowFBType>', '</SubWindowFBType>')
            # Удаление старых строк <VarDeclaration Name="pos", <VarDeclaration Name="visible", <VarDeclaration Name="size"
            updated_window_block = re.sub(r'<VarDeclaration Name="(pos|visible|size)".*?/>', '', updated_window_block, count=3)
            # Извлекаем содержимое <EventOutputs> из SubWindowFBType
            graphics_event_outputs = re.search(r'<EventOutputs>(.*?)</EventOutputs>', graphics_block, re.DOTALL).group(1)

            # Добавляем содержимое <EventOutputs> из SubWindowFBType в <EventOutputs> из WindowFBType
            updated_window_block = re.sub(r'(<EventOutputs>)(.*?)(</EventOutputs>)', fr'\1\n{graphics_event_outputs}\2\3', updated_window_block, count=1, flags=re.DOTALL)

            # Извлекаем необходимые VarDeclaration из SubWindowFBType
            new_vars_pattern = re.compile(r'(<VarDeclaration Name="(zValue|hint|moveable|enabled|angle|frame_color|caption_font|closable)".*?/>|<VarDeclaration Name="(pos|visible|size)".*?InitialValue=".*?".*?/>|<VarDeclaration Name="(pos|visible|size)".*?/>)(?!<VarDeclaration Name="(initialValue)".*?)', re.DOTALL)
            new_vars = new_vars_pattern.findall(graphics_block)
            new_vars_text = ''
            tabulation = get_tabulation()
            for match in new_vars:
                var = match[0]
                # Для переменных pos, visible, и size мы сохраняем существующий InitialValue
                if 'Name="pos"' in var or 'Name="visible"' in var or 'Name="size"' in var:
                    existing_var = extract_var_decl(window_block, re.search(r'Name="(.*?)"', var).group(1))
                    if existing_var:
                        var = merge_var_decl(existing_var, var)
                        # Если переменная size, то добавляем 12 к width и 29 к height
                        if 'Name="size"' in var:
                            width_match = re.search(r'width:=(\d+)', var)
                            height_match = re.search(r'height:=(\d+)', var)
                            if width_match and height_match:
                                width = int(width_match.group(1)) + 12
                                height = int(height_match.group(1)) + 29
                                var = re.sub(r'width:=\d+', f'width:={width}', var)
                                var = re.sub(r'height:=\d+', f'height:={height}', var)
                # Устанавливаем InitialValue для moveable и closable как "TRUE"
                elif 'Name="moveable"' in var or 'Name="closable"' in var:
                    var = re.sub(r'InitialValue=".*?"', 'InitialValue="TRUE"', var)

                # Добавляем VarDeclaration с нужной табуляцией  
                new_vars_text += f'{tabulation}{var.strip()}\n'
            # Вставляем новые VarDeclaration в первый блок <InputVars>
            updated_window_block = re.sub(r'(<SubWindowFBType .*?<InputVars>)(.*?)(</InputVars>)', fr'\1\n{new_vars_text}{tabulation}\2\3', updated_window_block, count=1, flags=re.DOTALL)

            # Замена старого блока на обновленный
            iec_hmi_content = iec_hmi_content.replace(window_block, updated_window_block)

    return iec_hmi_content

def main():
    parser = argparse.ArgumentParser(description="Process .iec_hmi files.")
    parser.add_argument('iec_hmi_file', help='The .iec_hmi file to process.')
    parser.add_argument('--graphics', help='The GraphicsCompositeType.txt file.', default='GraphicsCompositeType.txt')
    parser.add_argument('--subwindow', help='The TSubWindowType.txt file.', default='TSubWindowType.txt')

    args = parser.parse_args()

    if not os.path.exists(args.iec_hmi_file):
        print(f"File {args.iec_hmi_file} not found.")
        return

    iec_hmi_content = read_file(args.iec_hmi_file)

    if os.path.exists(args.graphics):
        graphics_composite_content = read_file(args.graphics)
        iec_hmi_content = process_graphics(iec_hmi_content, graphics_composite_content)
    else:
        print(f"File {args.graphics} not found.")

    if os.path.exists(args.subwindow):
        sub_window_content = read_file(args.subwindow)
        iec_hmi_content = process_subwindow(iec_hmi_content, sub_window_content)
    else:
        print(f"File {args.subwindow} not found.")


    # Блок замены DestinationUUID
    iec_hmi_content = iec_hmi_content.replace('E0FDB58B4C0E41BEF99CB99F0F523C83', 'EAC5288F431A370F7493EF98A2C613D5')
    iec_hmi_content = iec_hmi_content.replace('B3E2DCE04C63F5A91D55B4B585803AB1', '599604C246641AA6BA0E508C9ABF7EA4')
    iec_hmi_content = iec_hmi_content.replace('C6CE29B54853ABD72B3982A71CC39353', '1555B4384D69683C33FCB4A79B1A0932')

    result_filename = 'result.iec_hmi'
    write_file(result_filename, iec_hmi_content)

if __name__ == '__main__':
    main()
