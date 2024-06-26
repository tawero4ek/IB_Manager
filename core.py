import argparse
import os
import re


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

    # Жестко заданный блок GraphicsCompositeFBType
    GRAPHICS_BLOCK = '''
    <GraphicsCompositeFBType Name="TNewGraphicsCompositeType" ShowVarTypes="true" UUID="VU23MZKKH3BERD2T7CTTELBTH4">
        <InterfaceList>
            <EventOutputs>
                <Event Name="mouseLBPress" Comment="событие нажатия левой кнопки мыши на объекте" UUID="V6KZEKNMZSTEPFU4AATMKR23JQ" />
                <Event Name="mouseLBRelease" Comment="событие отпускания левой кнопки мыши на объекте" UUID="CMAONDPWHSAEHMJS6M4XSAGDNQ" />
                <Event Name="mouseRBPress" Comment="событие нажатия правой кнопки мыши на объекте" UUID="6WJ6SXLHALQEHCL5A7XVWG6Q2M" />
                <Event Name="mouseRBRelease" Comment="событие отпускания правой кнопки мыши на объекте" UUID="RVY3ACQCBPUUDNBFKT37BQJZDY" />
                <Event Name="mouseEnter" Comment="событие входа указателя мыши в пределы объекта" UUID="CVJR3KU4H2OUZIFNWASV2K7YKY" />
                <Event Name="mouseLeave" Comment="событие выхода указателя мыши за пределы объекта" UUID="ULABXQT2CWHEVGWFBP2XXTJVCY" />
                <Event Name="mouseLBDblClick" Comment="событие двойного щелчка левой кнопки мыши на объекте" UUID="2JR5EGZ5UMXUDM6FM6RQVHYMJA" />
            </EventOutputs>
            <InputVars>
                <VarDeclaration Name="pos" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" Comment="позиция объекта" Group="Общие" InitialValue="(x:=0,y:=0)" UUID="YICJMWNGDJSENDCQB25KI7V7TI" />
                <VarDeclaration Name="angle" Type="LREAL" Comment="угол поворота объекта" Group="Общие" InitialValue="0" UUID="QAO7YAFI4UWUVECT5A6T3LCA2Y" />
                <VarDeclaration Name="enabled" Type="BOOL" Comment="доступность объекта" Group="Общие" InitialValue="TRUE" UUID="AOL3AFL4X2NUXJHAPDGTSQVGMY" />
                <VarDeclaration Name="moveable" Type="BOOL" Comment="подвижность объекта" Group="Общие" InitialValue="FALSE" UUID="BWAWE3KLRTPUNPRN4YTUWGLDXI" />
                <VarDeclaration Name="visible" Type="BOOL" Comment="видимость объекта" Group="Общие" InitialValue="TRUE" UUID="R4UML2QPG4NEHGHPSN2NKE6GUI" />
                <VarDeclaration Name="zValue" Type="LREAL" Comment="z-индекс объекта" Group="Общие" InitialValue="0" UUID="VXTOSKNU3FNUPMCAN6PKO5EDGI" />
                <VarDeclaration Name="hint" Type="STRING" Comment="всплывающая подсказка" Group="Общие" InitialValue="&apos;&apos;" UUID="CLZADEBSNHDEJMFXQH53VBNQEE" />
                <VarDeclaration Name="size" Type="TSize" TypeUUID="XDTT5M52XMSURN23S57SF26UGU" Comment="размер прямоугольника" Group="Общие" InitialValue="(width:=50,height:=50)" UUID="HC2FKFJ4NBUU3J5U7QZTECI2TM" />
            </InputVars>
        </InterfaceList>
    </GraphicsCompositeFBType>
    '''
    for window_name in window_names:
        # Ищем блоки WindowFBType
        window_pattern = re.compile(fr'<WindowFBType Name="{window_name}".*?</WindowFBType>', re.DOTALL)

        window_match = window_pattern.search(iec_hmi_content)

        if window_match:
            window_block = window_match.group()

            # Замена WindowFBType на GraphicsCompositeFBType
            updated_window_block = window_block.replace('<WindowFBType', '<GraphicsCompositeFBType').replace(
                '</WindowFBType>', '</GraphicsCompositeFBType>')

            # Удаление старых строк <VarDeclaration Name="pos", <VarDeclaration Name="visible", <VarDeclaration
            # Name="size"
            updated_window_block = re.sub(r'<VarDeclaration Name="(pos|visible|size)".*?/>', '', updated_window_block,
                                          count=3)

            # Извлекаем содержимое <EventOutputs> из жестко заданного блока
            graphics_event_outputs = re.search(r'<EventOutputs>(.*?)</EventOutputs>', GRAPHICS_BLOCK, re.DOTALL).group(
                1)

            # Добавляем содержимое <EventOutputs> из жестко заданного блока в <EventOutputs> из WindowFBType
            updated_window_block = re.sub(r'(<EventOutputs>)(.*?)(</EventOutputs>)',
                                          fr'\1\n{graphics_event_outputs}\2\3', updated_window_block, count=1,
                                          flags=re.DOTALL)

            # Извлекаем необходимые VarDeclaration из жестко заданного блока
            new_vars_pattern = re.compile(
                r'(<VarDeclaration Name="(zValue|hint|moveable|enabled|angle)".*?/>|<VarDeclaration Name="(pos|visible|size)".*?InitialValue=".*?".*?/>|<VarDeclaration Name="(pos|visible|size)".*?/>)',

                re.DOTALL)
            new_vars = new_vars_pattern.findall(GRAPHICS_BLOCK)
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
            updated_window_block = re.sub(r'(<GraphicsCompositeFBType .*?<InputVars>)(.*?)(</InputVars>)',
                                          fr'\1\n{new_vars_text}{tabulation}\2\3', updated_window_block, count=1,
                                          flags=re.DOTALL)

            # Замена старого блока на обновленный
            iec_hmi_content = iec_hmi_content.replace(window_block, updated_window_block)

    return iec_hmi_content


# Блок замены на SubWindow
def process_subwindow(iec_hmi_content, sub_window_content):
    # Получаем названия окон из TType.txt
    window_names = sub_window_content.strip().split('\n')
    # Жестко заданный блок SubWindowFBType
    SUBWINDOW_BLOCK = '''
    <SubWindowFBType Name="TNewSubWindow" ShowVarTypes="true" UUID="26ATFZ6JTHMULHTL3SN6NMGTRE">
        <InterfaceList>
            <EventInputs>
                <Event Name="show" UUID="5OQ6VR6NEZGUHNP6SUHDH3MAWM" />
                <Event Name="hide" UUID="7WLQDBX2VRDUXALIRZGS6HUXSM" />
            </EventInputs>
            <EventOutputs>
                <Event Name="mouseLBPress" Comment="событие нажатия левой кнопки мыши на объекте" UUID="V6KZEKNMZSTEPFU4AATMKR23JQ" />
                <Event Name="mouseLBRelease" Comment="событие отпускания левой кнопки мыши на объекте" UUID="CMAONDPWHSAEHMJS6M4XSAGDNQ" />
                <Event Name="mouseRBPress" Comment="событие нажатия правой кнопки мыши на объекте" UUID="6WJ6SXLHALQEHCL5A7XVWG6Q2M" />
                <Event Name="mouseRBRelease" Comment="событие отпускания правой кнопки мыши на объекте" UUID="RVY3ACQCBPUUDNBFKT37BQJZDY" />
                <Event Name="mouseEnter" Comment="событие входа указателя мыши в пределы объекта" UUID="CVJR3KU4H2OUZIFNWASV2K7YKY" />
                <Event Name="mouseLeave" Comment="событие выхода указателя мыши за пределы объекта" UUID="ULABXQT2CWHEVGWFBP2XXTJVCY" />
                <Event Name="mouseLBDblClick" Comment="событие двойного щелчка левой кнопки мыши на объекте" UUID="2JR5EGZ5UMXUDM6FM6RQVHYMJA" />
                <Event Name="showed" UUID="SV7KTHQOU7FUVGCPLRYADJZPIE" />
                <Event Name="hid" UUID="BSQJOLG73PTUPJYLMBHGJQD65M" />
            </EventOutputs>
            <InputVars>
                <VarDeclaration Name="pos" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" Comment="позиция объекта" Group="Общие" InitialValue="(x:=0,y:=0)" UUID="YICJMWNGDJSENDCQB25KI7V7TI" />
                <VarDeclaration Name="angle" Type="LREAL" Comment="угол поворота объекта" Group="Общие" InitialValue="0" UUID="QAO7YAFI4UWUVECT5A6T3LCA2Y" />
                <VarDeclaration Name="enabled" Type="BOOL" Comment="доступность объекта" Group="Общие" InitialValue="TRUE" UUID="AOL3AFL4X2NUXJHAPDGTSQVGMY" />
                <VarDeclaration Name="moveable" Type="BOOL" Comment="подвижность объекта" Group="Общие" InitialValue="FALSE" UUID="BWAWE3KLRTPUNPRN4YTUWGLDXI" />
                <VarDeclaration Name="visible" Type="BOOL" Comment="видимость объекта" Group="Общие" InitialValue="FALSE" UUID="R4UML2QPG4NEHGHPSN2NKE6GUI" />
                <VarDeclaration Name="zValue" Type="LREAL" Comment="z-индекс объекта" Group="Общие" InitialValue="0" UUID="VXTOSKNU3FNUPMCAN6PKO5EDGI" />
                <VarDeclaration Name="hint" Type="STRING" Comment="всплывающая подсказка" Group="Общие" InitialValue="&apos;&apos;" UUID="CLZADEBSNHDEJMFXQH53VBNQEE" />
                <VarDeclaration Name="size" Type="TSize" TypeUUID="XDTT5M52XMSURN23S57SF26UGU" Comment="размер прямоугольника" Group="Общие" InitialValue="(width:=100,height:=100)" UUID="HC2FKFJ4NBUU3J5U7QZTECI2TM" />
                <VarDeclaration Name="frame_color" Type="TColor" TypeUUID="EDYJMIBCJR5UJOZWGS3UVJENZA" InitialValue="4293980400" UUID="GS2XRATVXFKEDNVR4AYF2FOHB4" />
                <VarDeclaration Name="bg_color" Type="TColor" TypeUUID="EDYJMIBCJR5UJOZWGS3UVJENZA" InitialValue="4294967295" UUID="IZCT7UFDEEXEXA45WVKQH4CXO4" />
                <VarDeclaration Name="caption" Type="STRING" InitialValue="&apos;&apos;" UUID="4SEHRDHYXADETHGWSFVJCJBXGI" />
                <VarDeclaration Name="caption_font" Type="TFont" TypeUUID="YVT73EACFULUPIWKAFYTDAC3S4" InitialValue="(family:=&apos;PT Sans&apos;,size:=12,bold:=FALSE,italic:=FALSE,underline:=FALSE,strikeout:=FALSE)" UUID="QSRIHPHZL46UPJPPH4M4OB7PS4" />
                <VarDeclaration Name="closable" Type="BOOL" InitialValue="FALSE" UUID="MHEPWGX4TXFUPIWFJHGMKSAXPA" />
            </InputVars>
        </InterfaceList>
    </SubWindowFBType>
    '''
    for window_name in window_names:
        # Ищем блоки WindowFBType
        window_pattern = re.compile(fr'<WindowFBType Name="{window_name}".*?</WindowFBType>', re.DOTALL)

        window_match = window_pattern.search(iec_hmi_content)

        if window_match:
            window_block = window_match.group()

            # Замена WindowFBType на SubWindowFBType
            updated_window_block = window_block.replace('<WindowFBType', '<SubWindowFBType').replace('</WindowFBType>',
                                                                                                     '</SubWindowFBType>')

            # Удаление старых строк <VarDeclaration Name="pos", <VarDeclaration Name="visible", <VarDeclaration
            # Name="size"
            updated_window_block = re.sub(r'<VarDeclaration Name="(pos|visible|size)".*?/>', '', updated_window_block,
                                          count=3)

            # Извлекаем содержимое <EventOutputs> из жестко заданного блока
            graphics_event_outputs = re.search(r'<EventOutputs>(.*?)</EventOutputs>', SUBWINDOW_BLOCK, re.DOTALL).group(
                1)

            # Добавляем содержимое <EventOutputs> из SubWindowFBType в <EventOutputs> из WindowFBType
            updated_window_block = re.sub(r'(<EventOutputs>)(.*?)(</EventOutputs>)',
                                          fr'\1\n{graphics_event_outputs}\2\3', updated_window_block, count=1,
                                          flags=re.DOTALL)

            # Извлекаем необходимые VarDeclaration из жестко заданного блока
            new_vars_pattern = re.compile(
                r'(<VarDeclaration Name="(zValue|hint|moveable|enabled|angle|frame_color|caption_font|closable'
                r')".*?/>|<VarDeclaration Name="(pos|visible|size)".*?InitialValue=".*?".*?/>|<VarDeclaration Name="('
                r'pos|visible|size)".*?/>)(?!<VarDeclaration Name="(initialValue)".*?)',
                re.DOTALL)
            new_vars = new_vars_pattern.findall(SUBWINDOW_BLOCK)
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
            updated_window_block = re.sub(r'(<SubWindowFBType .*?<InputVars>)(.*?)(</InputVars>)',
                                          fr'\1\n{new_vars_text}{tabulation}\2\3', updated_window_block, count=1,
                                          flags=re.DOTALL)

            # Замена старого блока на обновленный
            iec_hmi_content = iec_hmi_content.replace(window_block, updated_window_block)

    return iec_hmi_content


def main_core(command):
    parser = argparse.ArgumentParser(description="Process .iec_hmi files.")
    parser.add_argument('iec_hmi_file', help='The .iec_hmi file to process.')
    parser.add_argument('--graphics', help='The GraphicsCompositeType.txt file.', default='GraphicsCompositeType.txt')
    parser.add_argument('--subwindow', help='The TSubWindowType.txt file.', default='TSubWindowType.txt')

    args = parser.parse_args(command)  # Парсинг аргументов из команды

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
