import re
import shutil
import os
import uuid

def execute_ib_command(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Найти все вхождения <FB Name="AlarmViewer\d+" Type="TAlarmViewer" TypeUUID="[^"]+".*?<Palette>...</Palette> и извлечь их содержимое
        alarm_palettes = re.findall(r'<FB Name="\w+\d*" Type="TAlarmViewer" TypeUUID="[^"]+".*?<Palette>(.*?)</Palette>', content, re.DOTALL)
        
        # Найти все вхождения <Palette>...</Palette> и извлечь их содержимое
        general_palettes = re.findall(r'<Palette>(.*?)</Palette>', content, re.DOTALL)
        
        # Переменные для хранения содержимого
        general_palettes_modified = []
        alarm_palettes_modified = []

        # Функция для модификации содержимого <StateData>
        def modify_state_data(palette_content):
            def replacement(match):
                state, fg, bg = match.groups()
                return f'<StateData State="{state}" Foreground="{fg}" Background="{bg}" Blinking="0" ForegroundAlter="{fg}" BackgroundAlter="{bg}" />'
            
            return re.sub(r'<StateData State="(\d+)" Foreground="(#[0-9a-fA-F]{6})" Background="(#[0-9a-fA-F]{6})" />', replacement, palette_content)
        # Модифицировать содержимое всех палитр и удалить дубликаты для general_palettes
        for palette_content in general_palettes:
            modified_content = modify_state_data(palette_content)
            general_palettes_modified.append(modified_content)

        # Модифицировать содержимое всех палитр и удалить дубликаты для alarm_palettes
        for palette_content in alarm_palettes:
            modified_content = modify_state_data(palette_content)
            alarm_palettes_modified.append(modified_content)

        # Преобразовать списки в строки
        general_palettes_str = '\n'.join(general_palettes_modified).strip()  # Убираем лишние пустые строки
        alarm_palettes_str = '\n'.join(alarm_palettes_modified).strip()  # Убираем лишние пустые строки

        # Чтение содержимого result.iec_hmi
        with open('result.iec_hmi', 'r+', encoding='utf-8') as result_file:
            result_content = result_file.read()
            
            # Вставка измененного содержимого в EventPalette
            if general_palettes_str:
                if re.search(r'<EventPalette>', result_content) is None:
                    result_content += f'\n<EventPalette>\n{general_palettes_str}\n</EventPalette>'
                else:
                    result_content = re.sub(r'(<EventPalette>\s*)(.*?)(\s*</EventPalette>)', fr'\1{general_palettes_str}\2\3', result_content, flags=re.DOTALL)
            
            # Вставка измененного содержимого в AlarmPalette
            if alarm_palettes_str:
                if re.search(r'<AlarmPalette>', result_content) is None:
                    result_content += f'\n<AlarmPalette>\n{alarm_palettes_str}\n</AlarmPalette>'
                else:
                    result_content = re.sub(r'(<AlarmPalette>\s*)(.*?)(\s*</AlarmPalette>)', fr'\1{alarm_palettes_str}\2\3', result_content, flags=re.DOTALL)

            # Запись обратно в файл
            result_file.seek(0)
            result_file.write(result_content)
            result_file.truncate()
        
        print("Файл успешно обновлен.")

    except Exception as e:
        print(f"Произошла ошибка: {e}")


def change_font_in_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Заменить все строки family:=&apos;*****&apos; на family:=&apos;PT Sans&apos;
        updated_content = re.sub(r'family:=&apos;.*?&apos;', r'family:=&apos;PT Sans&apos;', content)

        with open(f'result.iec_hmi', 'w', encoding='utf-8') as file:
            file.write(updated_content)

        print("Шрифты успешно обновлены.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

def add_files_to_design(destination_folder):
    try:
        source_folder = os.path.join(os.path.dirname(__file__), 'source')
        
        if not os.path.exists(source_folder):
            print(f"Папка 'source' не найдена по пути {source_folder}")
            return

        for item in os.listdir(source_folder):
            source_path = os.path.join(source_folder, item)
            destination_path = os.path.join(destination_folder, item)

            if os.path.isdir(source_path):
                shutil.copytree(source_path, destination_path, dirs_exist_ok=True)
            else:
                shutil.copy2(source_path, destination_path)

        print("Файлы успешно скопированы.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

def add_variables_to_files(prj_file, mnemo_file, event_logger_file):
    prj_addition = """
		<Signal Name="countEvents" UUID="QDU3M57FNUYE3B3BJPSZTTSLMU" Type="REAL" Global="TRUE" Storage="persistent" Comment="ИБ: Количество событий, хранящихся в пределах одной базы данных" />
		<Signal Name="countWarningEvents" UUID="E3IAVKI2X7LEZECAHW2ZAQMUHQ" Type="REAL" Global="TRUE" Storage="persistent" Comment="ИБ: Количество событий, при которых будут выдаваться предупредительные события" />
		<Signal Name="timePeriod" UUID="55TLYWWO4ZSU5HKFOHWK64PZWY" Type="REAL" Global="TRUE" Storage="persistent" Comment="ИБ: Период выдачи событий о переполнении" />
		<Signal Name="dir" UUID="QCBLIZHWZMNE5K6FWBVEMF57MM" Type="STRING" Global="TRUE" Storage="persistent" Comment="ИБ: Путь для сохранения выгрузки базы данных в CSV при переполнении" />
		<Signal Name="nameFile" UUID="2VONHG6AT2NUTAAQNBNDTXUCVI" Type="STRING" Global="TRUE" Storage="persistent" Comment="ИБ: Имя файла данных ИБ CSV" />
		<Signal Name="nameUser" UUID="QGYOIKKUP2WURKTISXV424YX3Q" Type="STRING" Global="TRUE" Storage="persistent" Comment="ИБ: Имя пользователя от имени, которого будут формироваться служебные события" />
		<Signal Name="save" UUID="EBLB3XCJNSTUZN4RSDJ7VJZUKI" Type="BOOL" Global="TRUE" Comment="ИБ: Флаг записи настроек БД в энергонезависимую память" />
		<Signal Name="connectBD" UUID="QS4L5BI5E4KU7HMX4TACM4I4GA" Type="BOOL" Global="TRUE" Storage="persistent" Comment="ИБ: Флаг соединения с БД после ввода имени пользователя, пароля, имени БД" />
		<Signal Name="userBD" UUID="QKXE5ZSKC2WEDIHRPU3UWDVTTU" Type="STRING" Global="TRUE" Storage="persistent" Comment="ИБ: Имя пользователя БД (зашифрованное)" />
		<Signal Name="passBD" UUID="NALONZ2ZVWYUZPMRVDTGOZUEWQ" Type="STRING" Global="TRUE" Storage="persistent" Comment="ИБ: Пароль пользователя БД (зашифрованный)" />
		<Signal Name="nameBD" UUID="6CSHNG4TPV6EBMIB27CGWNYXUA" Type="STRING" Global="TRUE" Storage="persistent" Comment="ИБ: Имя БД (зашифрованное)" />
		<Signal Name="connectedBD" UUID="GFLFSMA6VY3E5H6PDFXOC7GZNI" Type="BOOL" Global="TRUE" Comment="ИБ: Флаг наличия связи с БД" />
		<Signal Name="DumpBD" UUID="MO7UO7XAVSOEHLWUBJO35JQXFU" Type="BOOL" Global="TRUE" Comment="ИБ: Флаг принудительной записи данных в csv файл" />
        <Signal Name="Type_OS" UUID="H55SYOBEQWLE7LRKKDWXSKERKA" Type="BOOL" InitialValue="FALSE" Usage="" Global="TRUE" Comment="Тип операционной системы (False-AstraLinux/TRUE- Windows) " />
    """
    mnemo_addition = """
		<Signal Name="ThisNode" UUID="IWFC3632K22ERPFEGTWM3NPU5M" Type="STRING" Usage="" />
		<Signal Name="countEvents" UUID="QDU3M57FNUYE3B3BJPSZTTSLMU" Type="REAL" Usage="" Global="TRUE" Storage="persistent" Comment="ИБ: Количество событий, хранящихся в пределах одной базы данных" />
		<Signal Name="countWarningEvents" UUID="E3IAVKI2X7LEZECAHW2ZAQMUHQ" Type="REAL" Usage="" Global="TRUE" Storage="persistent" Comment="ИБ: Количество событий, при которых будут выдаваться предупредительные события" />
		<Signal Name="timePeriod" UUID="55TLYWWO4ZSU5HKFOHWK64PZWY" Type="REAL" Usage="" Global="TRUE" Storage="persistent" Comment="ИБ: Период выдачи событий о переполнении" />
		<Signal Name="dir" UUID="QCBLIZHWZMNE5K6FWBVEMF57MM" Type="STRING" Usage="" Global="TRUE" Storage="persistent" Comment="ИБ: Путь для сохранения выгрузки базы данных в CSV при переполнении" />
		<Signal Name="nameFile" UUID="2VONHG6AT2NUTAAQNBNDTXUCVI" Type="STRING" Usage="" Global="TRUE" Storage="persistent" Comment="ИБ: Имя файла данных ИБ CSV" />
		<Signal Name="nameUser" UUID="QGYOIKKUP2WURKTISXV424YX3Q" Type="STRING" Usage="" Global="TRUE" Storage="persistent" Comment="ИБ: Имя пользователя от имени, которого будут формироваться служебные события" />
		<Signal Name="save" UUID="EBLB3XCJNSTUZN4RSDJ7VJZUKI" Type="BOOL" Usage="" Global="TRUE" Comment="ИБ: Флаг записи настроек БД в энергонезависимую память" />
		<Signal Name="connectBD" UUID="QS4L5BI5E4KU7HMX4TACM4I4GA" Type="BOOL" Usage="" Global="TRUE" Storage="persistent" Comment="ИБ: Флаг соединения с БД после ввода имени пользователя, пароля, имени БД" />
		<Signal Name="userBD" UUID="QKXE5ZSKC2WEDIHRPU3UWDVTTU" Type="STRING" Usage="" Global="TRUE" Storage="persistent" Comment="ИБ: Имя пользователя БД (зашифрованное)" />
		<Signal Name="passBD" UUID="NALONZ2ZVWYUZPMRVDTGOZUEWQ" Type="STRING" Usage="" Global="TRUE" Storage="persistent" Comment="ИБ: Пароль пользователя БД (зашифрованный)" />
		<Signal Name="nameBD" UUID="6CSHNG4TPV6EBMIB27CGWNYXUA" Type="STRING" Usage="" Global="TRUE" Storage="persistent" Comment="ИБ: Имя БД (зашифрованное)" />
		<Signal Name="connectedBD" UUID="GFLFSMA6VY3E5H6PDFXOC7GZNI" Type="BOOL" Usage="" Global="TRUE" Comment="ИБ: Флаг наличия связи с БД" />
		<Signal Name="DumpBD" UUID="MO7UO7XAVSOEHLWUBJO35JQXFU" Type="BOOL" Usage="" Global="TRUE" Comment="ИБ: Флаг принудительной записи данных в csv файл" />
		<Signal Name="R_Control" UUID="2GZP57EYBY7U3HM7UZ2EDHXHQ4" Type="BOOL" Usage="" />
		<Signal Name="R_SetPoint" UUID="AQGXRTB2CCQUPGSA4QTKOH7Q6Q" Type="BOOL" Usage="" />
		<Signal Name="R_Print" UUID="VJGD7TTOQE6E3HBQI67UBSXWZM" Type="BOOL" Usage="" />
		<Signal Name="R_ViewArj" UUID="WFHAIVO4HXIUNNUWHQCZ3XAVIE" Type="BOOL" Usage="" />
		<Signal Name="R_QuitAlarm" UUID="YAQUAA3ZI7QEVGBADBA5CXSH6Y" Type="BOOL" Usage="" />
		<Signal Name="R_CfgEvViewer" UUID="JO74X7UJ54GELDNM6QYXJHAFQU" Type="BOOL" Usage="" />
		<Signal Name="R_Simulate" UUID="U4JVFPNF56FUFHMGKDYCGVWUS4" Type="BOOL" Usage="" />
        <Signal Name="Type_OS" UUID="H55SYOBEQWLE7LRKKDWXSKERKA" Type="BOOL" InitialValue="FALSE" Usage="" Global="TRUE" Comment="Тип операционной системы (False-AstraLinux/TRUE- Windows) " />
        """
    event_logger_addition = """
		<Signal Name="connectBD" UUID="QS4L5BI5E4KU7HMX4TACM4I4GA" Type="BOOL" Usage="" Global="TRUE" Storage="persistent" Comment="ИБ: Флаг соединения с БД после ввода имени пользователя, пароля, имени БД" />
		<Signal Name="userBD" UUID="QKXE5ZSKC2WEDIHRPU3UWDVTTU" Type="STRING" Usage="" Global="TRUE" Storage="persistent" Comment="ИБ: Имя пользователя БД (зашифрованное)" />
		<Signal Name="passBD" UUID="NALONZ2ZVWYUZPMRVDTGOZUEWQ" Type="STRING" Usage="" Global="TRUE" Storage="persistent" Comment="ИБ: Пароль пользователя БД (зашифрованный)" />
		<Signal Name="nameBD" UUID="6CSHNG4TPV6EBMIB27CGWNYXUA" Type="STRING" Usage="" Global="TRUE" Storage="persistent" Comment="ИБ: Имя БД (зашифрованное)" />
    """
    try:
        # Открываем файл .prj и добавляем новые сигналы
        with open(prj_file, 'r', encoding='utf-8') as f:
            prj_content = f.read()
        prj_content = prj_content.replace('</Globals>', prj_addition + '</Globals>')
        with open(prj_file, 'w', encoding='utf-8') as f:
            f.write(prj_content)

        # Открываем файл .int mnemo и добавляем новые сигналы
        with open(mnemo_file, 'r', encoding='utf-8') as f:
            mnemo_content = f.read()
        mnemo_content = mnemo_content.replace('</InterfaceList>', mnemo_addition + '</InterfaceList>')
        with open(mnemo_file, 'w', encoding='utf-8') as f:
            f.write(mnemo_content)

        # Открываем файл .int event logger и добавляем новые сигналы
        with open(event_logger_file, 'r', encoding='utf-8') as f:
            event_logger_content = f.read()
        event_logger_content = event_logger_content.replace('</InterfaceList>', event_logger_addition + '</InterfaceList>')
        with open(event_logger_file, 'w', encoding='utf-8') as f:
            f.write(event_logger_content)

    except Exception as e:
        print(f"Error adding variables to files: {e}")

def add_HMI_to_files(file_path):
    HMI_addition = """
        <Folder Name="IB" Comment="" Data="" UUID="3ESE2HQ3M5EUZIZODWES52KEL4">
            <BasicFBType Name="B_Change" Comment="формирует событие при изменении вх. переменной -steam" ShowVarTypes="true" UUID="NZWRQBU33QQUXBOX3J3FMZ24BE">
                <InterfaceList>
                    <EventInputs>
                        <Event Name="EI" UUID="CV4BS257KR5UTCWKBTIUVWB3LU" />
                    </EventInputs>
                    <EventOutputs>
                        <Event Name="CHANGED" UUID="3MSQFW5VZWDEPJSTR4PG5W5XVA" />
                    </EventOutputs>
                    <InputVars>
                        <VarDeclaration Name="value" Type="BOOL" InitialValue="FALSE" UUID="6K5FPXJJLLKUTANA7PYTBT7BYA" changeEvent="EI" changeEventUUID="CV4BS257KR5UTCWKBTIUVWB3LU" />
                    </InputVars>
                </InterfaceList>
                <BasicFB>
                    <Algorithm Name="fictive" UUID="Y377WWETWYDEXPNZRIRCJASJW4">
                        <ST Text=";(* нет операций *)" />
                    </Algorithm>
                    <ECC>
                        <ECState Name="READY" UUID="O6X5C3VBCBQEJHOLMQZEDJ3DYU" />
                        <ECState Name="CLOP" UUID="TFX6NTHIHR7UJPFQM24CKCJAXI">
                            <ECAction Algorithm="fictive" AlgorithmUUID="Y377WWETWYDEXPNZRIRCJASJW4" Output="CHANGED" OutputUUID="3MSQFW5VZWDEPJSTR4PG5W5XVA" />
                        </ECState>
                        <ECTransition Source="READY" SourceUUID="O6X5C3VBCBQEJHOLMQZEDJ3DYU" Destination="CLOP" DestinationUUID="TFX6NTHIHR7UJPFQM24CKCJAXI" Condition="EI" />
                        <ECTransition Source="CLOP" SourceUUID="TFX6NTHIHR7UJPFQM24CKCJAXI" Destination="READY" DestinationUUID="O6X5C3VBCBQEJHOLMQZEDJ3DYU" Condition="BOOL#1" />
                    </ECC>
                </BasicFB>
            </BasicFBType>
            <GraphicsCompositeFBType Name="TButtonUser" ShowVarTypes="true" UUID="BP3HNKZODXIURKHJ7AGNNV3TV4">
                <InterfaceList>
                    <EventOutputs>
                        <Event Name="mouseLBPress" Comment="событие нажатия левой кнопки мыши на объекте" UUID="V6KZEKNMZSTEPFU4AATMKR23JQ" />
                        <Event Name="mouseLBRelease" Comment="событие отпускания левой кнопки мыши на объекте" UUID="CMAONDPWHSAEHMJS6M4XSAGDNQ" />
                        <Event Name="mouseRBPress" Comment="событие нажатия правой кнопки мыши на объекте" UUID="6WJ6SXLHALQEHCL5A7XVWG6Q2M" />
                        <Event Name="mouseRBRelease" Comment="событие отпускания правой кнопки мыши на объекте" UUID="RVY3ACQCBPUUDNBFKT37BQJZDY" />
                        <Event Name="mouseEnter" Comment="событие входа указателя мыши в пределы объекта" UUID="CVJR3KU4H2OUZIFNWASV2K7YKY" />
                        <Event Name="mouseLeave" Comment="событие выхода указателя мыши за пределы объекта" UUID="ULABXQT2CWHEVGWFBP2XXTJVCY" />
                        <Event Name="mouseLBDblClick" Comment="событие двойного щелчка левой кнопки мыши на объекте" UUID="2JR5EGZ5UMXUDM6FM6RQVHYMJA" />
                        <Event Name="Pressed" UUID="AVZEIOFH2TIU7JQZ5DTD2CN2PY" />
                    </EventOutputs>
                    <InputVars>
                        <VarDeclaration Name="pos" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" Comment="позиция объекта" InitialValue="(x:=0,y:=0)" UUID="YICJMWNGDJSENDCQB25KI7V7TI" />
                        <VarDeclaration Name="angle" Type="LREAL" Comment="угол поворота объекта" InitialValue="0" UUID="QAO7YAFI4UWUVECT5A6T3LCA2Y" />
                        <VarDeclaration Name="enabled" Type="BOOL" Comment="доступность объекта" InitialValue="TRUE" UUID="AOL3AFL4X2NUXJHAPDGTSQVGMY" />
                        <VarDeclaration Name="moveable" Type="BOOL" Comment="подвижность объекта" InitialValue="FALSE" UUID="BWAWE3KLRTPUNPRN4YTUWGLDXI" />
                        <VarDeclaration Name="visible" Type="BOOL" Comment="видимость объекта" InitialValue="TRUE" UUID="R4UML2QPG4NEHGHPSN2NKE6GUI" />
                        <VarDeclaration Name="zValue" Type="LREAL" Comment="z-индекс объекта" InitialValue="0" UUID="VXTOSKNU3FNUPMCAN6PKO5EDGI" />
                        <VarDeclaration Name="hint" Type="STRING" Comment="всплывающая подсказка" InitialValue="&apos;&apos;" UUID="CLZADEBSNHDEJMFXQH53VBNQEE" />
                        <VarDeclaration Name="size" Type="TSize" TypeUUID="XDTT5M52XMSURN23S57SF26UGU" Comment="размер прямоугольника" InitialValue="(width:=50,height:=50)" UUID="HC2FKFJ4NBUU3J5U7QZTECI2TM" />
                        <VarDeclaration Name="font" Type="TFont" TypeUUID="YVT73EACFULUPIWKAFYTDAC3S4" InitialValue="(family:=&apos;Tahoma&apos;,size:=13,bold:=TRUE,italic:=FALSE,underline:=FALSE,strikeout:=FALSE)" UUID="QJ3IJIGWZ5XEXGM2FDR6ZOXYDI" />
                        <VarDeclaration Name="Caption" Type="STRING" Comment="Окно расположения кнопки" InitialValue="&apos;&apos;" UUID="57KGOBVUSDTEVGXGSZCXY4RMBU" />
                    </InputVars>
                </InterfaceList>
                <FBNetwork>
                    <FB Name="SEL_0" Type="SEL" TypeUUID="VTYYYXK24ZYEFIHECN6CYXIJ5M" Enabled="true" UUID="O4GM2CCCR4IE3LWEN47TOI5DVQ" X="-44.3204923780627" Y="350.12212838239">
                        <VarValue Variable="IN0" Value="4288848295" Type="TColor" TypeUUID="EDYJMIBCJR5UJOZWGS3UVJENZA" />
                        <VarValue Variable="IN1" Value="4287861400" Type="TColor" TypeUUID="EDYJMIBCJR5UJOZWGS3UVJENZA" />
                    </FB>
                    <FB Name="Rect" Type="TRect" TypeUUID="24POL55EVH5U5GD3E4VMTU2OW4" Enabled="true" UUID="T7TF5JJAVFWUHFHXXZ5FZYNWT4" X="257.814287082339" Y="96.270616804819">
                        <VarValue Variable="bg_color" Value="16777215" Type="TColor" TypeUUID="EDYJMIBCJR5UJOZWGS3UVJENZA" />
                        <VarValue Variable="frame_color" Value="4294967295" Type="TColor" TypeUUID="EDYJMIBCJR5UJOZWGS3UVJENZA" />
                        <VarValue Variable="pos" Value="(x:=1,y:=1)" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" />
                        <VarValue Variable="zValue" Value="1" Type="LREAL" />
                    </FB>
                    <FB Name="E_SR" Type="E_SR" TypeUUID="RRP6KOL3Q66ERAUTY4G4XHPSJ4" Enabled="true" UUID="FYYXT4H4IHJEPKCUSPLD66ZDTY" X="569.357921708311" Y="161.835560614673" />
                    <FB Name="_ChangeUser" Type="T_ChangeUser" TypeUUID="NEUKQC7QEKVEZGX4745NW4CR44" Enabled="true" UUID="FHP7F5RCGN4ELEKEGWMUATT6BQ" X="896.314287082339" Y="113.270616804819">
                        <VarValue Variable="bg_color" Value="4290822336" Type="TColor" TypeUUID="EDYJMIBCJR5UJOZWGS3UVJENZA" />
                        <VarValue Variable="caption" Value="&apos;Окно авторизации&apos;" Type="STRING" />
                        <VarValue Variable="caption_font" Value="(family:=&apos;Tahoma&apos;,size:=13,bold:=FALSE,italic:=FALSE,underline:=FALSE,strikeout:=FALSE)" Type="TFont" TypeUUID="YVT73EACFULUPIWKAFYTDAC3S4" />
                        <VarValue Variable="closable" Value="TRUE" Type="BOOL" />
                        <VarValue Variable="pos" Value="(x:=280,y:=-70)" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" />
                    </FB>
                    <FB Name="FramedText" Type="TFramedText" TypeUUID="STR4DBAAWDOUJHFCH7OLU3OTFU" Enabled="true" UUID="AAHZE53MBCFUNC3LVGFOKMFG54" X="260.25" Y="600">
                        <VarValue Variable="alignment" Value="8" Type="TAlignment" TypeUUID="IUA2FTZVSF6EVJPPY3ZKXNHV6E" />
                        <VarValue Variable="font" Value="(family:=&apos;Tahoma&apos;,size:=12,bold:=FALSE,italic:=FALSE,underline:=FALSE,strikeout:=FALSE)" Type="TFont" TypeUUID="YVT73EACFULUPIWKAFYTDAC3S4" />
                        <VarValue Variable="frame_color" Value="4283050759" Type="TColor" TypeUUID="EDYJMIBCJR5UJOZWGS3UVJENZA" />
                        <VarValue Variable="pen_width" Value="3" Type="INT" />
                        <VarValue Variable="pos" Value="(x:=0,y:=0)" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" />
                        <VarValue Variable="zValue" Value="0" Type="LREAL" />
                    </FB>
                    <FB Name="CUR_DATA" Type="CUR_DATA" TypeUUID="63RFPIII26GUTO6ECZZ5724EPY" Enabled="true" UUID="SIFBTMR6M5XE5IJ3UE4BV5VZ7E" X="625.75" Y="480.75">
                        <VarValue Variable="VAR" Value="&apos;NodeName&apos;" Type="STRING" />
                    </FB>
                    <FB Name="IS_RegEvent3Cat" Type="TIS_RegEvent3Cat" TypeUUID="ZLJGKUXENPYEVM6AQX5RGFE4HQ" Enabled="true" UUID="E42EAGSECNQU5M6KQ4TFHXROMY" X="638.75" Y="286.125">
                        <VarValue Variable="M_Type" Value="&apos;Кнопка&apos;" Type="STRING" />
                        <VarValue Variable="Message" Value="&apos;Нажата кнопка &apos;" Type="STRING" />
                        <VarValue Variable="Name" Value="&apos;Вызов окна авторизации&apos;" Type="STRING" />
                    </FB>
                    <EventConnections>
                        <Connection Source="Rect.mouseLBRelease" Destination="Pressed" SourceUUID="A55EE69F436DA9207ABEF7949FB6E15C.8DE6001343803CF639F332B16CC30079" DestinationUUID="384472054FD1D4A7E6E819A67EBA093D" />
                        <Connection Source="Rect.mouseEnter" Destination="E_SR.S" SourceUUID="A55EE69F436DA9207ABEF7949FB6E15C.AA1D53154C9D3E9C25B0ADA056F82B5D" DestinationUUID="F079312E47D241FCD69354A89E237B3F.CA109EE94AEC00A1D0AAFA857E3712F8" dx1="10" dx2="102.044" dy="0.564944" />
                        <Connection Source="Rect.mouseLeave" Destination="E_SR.R" SourceUUID="A55EE69F436DA9207ABEF7949FB6E15C.C21BC0A24A8E157AF50BC59A1635CD7B" DestinationUUID="F079312E47D241FCD69354A89E237B3F.7DA8AA7346A8B200581116B130862F54" dx1="10" dx2="102.044" dy="0.564944" />
                        <Connection Source="_ChangeUser.Close" Destination="_ChangeUser.hide" SourceUUID="F6F2DF2945783322993544910C7E4E40.35001D8749D8D62E6BC449A2637B7549" DestinationUUID="F6F2DF2945783322993544910C7E4E40.860197FD4B47ACFA4D8E688193971E2F" dx1="10" dx2="10" dy="-183.25" />
                        <Connection Source="Rect.mouseLBRelease" Destination="_ChangeUser.show" SourceUUID="A55EE69F436DA9207ABEF7949FB6E15C.8DE6001343803CF639F332B16CC30079" DestinationUUID="F6F2DF2945783322993544910C7E4E40.C7EAA1EB434D26CD0E95FEB5B380ED33" dx1="386" dx2="53" dy="0.75" />
                        <Connection Source="Rect.mouseLBRelease" Destination="IS_RegEvent3Cat.Registrer" SourceUUID="A55EE69F436DA9207ABEF7949FB6E15C.8DE6001343803CF639F332B16CC30079" DestinationUUID="1A4034274E6113442687CAB3662EDE53.F4863EC2452A178A4460539D5B716C64" dx1="10.0004" dx2="171.435" dy="173.604" />
                    </EventConnections>
                    <DataConnections>
                        <Connection Source="E_SR.Q" Destination="SEL_0.G" SourceUUID="F079312E47D241FCD69354A89E237B3F.5758CA974978140FA5F3308319BA6292" DestinationUUID="08CD0C774D108F423F6FC4AEACA32337.E51CF88C46776F33BF0D21B3F4741605" dx1="10" dx2="57.9211" dy="20.75" />
                        <Connection Source="size" Destination="Rect.size" SourceUUID="1555B4384D69683C33FCB4A79B1A0932" DestinationUUID="A55EE69F436DA9207ABEF7949FB6E15C.1555B4384D69683C33FCB4A79B1A0932" />
                        <Connection Source="size" Destination="FramedText.size" SourceUUID="1555B4384D69683C33FCB4A79B1A0932" DestinationUUID="77920F00468B086C8AA96B8BEFA630E5.1555B4384D69683C33FCB4A79B1A0932" />
                        <Connection Source="SEL_0.OUT" Destination="FramedText.bg_color" SourceUUID="08CD0C774D108F423F6FC4AEACA32337.D94D29B049B6DB4E0A29EA9CB5266805" DestinationUUID="77920F00468B086C8AA96B8BEFA630E5.BB427CD148EAA5E6767B94A5F44367C5" dx1="14" dx2="173.07" dy="600.878" />
                        <Connection Source="_ChangeUser.knText" Destination="FramedText.text" SourceUUID="F6F2DF2945783322993544910C7E4E40.91A545CC4D7565BE5D54C6B3866F875B" DestinationUUID="77920F00468B086C8AA96B8BEFA630E5.6197985F4F26DAD792BB4698C1EFE1AA" dx1="10" dx2="10" dy="232" />
                        <Connection Source="CUR_DATA.DATA" Destination="_ChangeUser.Node" SourceUUID="B2190A924E6E673E38A13BA1F9B9F61A.F0CAC1EA4C932AC826D10A9E03B0BDB8" DestinationUUID="F6F2DF2945783322993544910C7E4E40.1066CBB24613CBF20662A5A36435643D" dx1="10" dx2="335.064" dy="-0.229383" />
                    </DataConnections>
                </FBNetwork>
            </GraphicsCompositeFBType>
            <CompositeFBType Name="TIS2RegEventButton" ShowVarTypes="true" UUID="ZNZZ47LTYMZUNHA2UGTJLLMH7E">
                <InterfaceList>
                    <EventInputs>
                        <Event Name="Registrer" Comment="Регистрация события" UUID="YI7IN5EKC4VELHKTMBCGI3DRLM" />
                    </EventInputs>
                    <InputVars>
                        <VarDeclaration Name="NameButton" Type="STRING" Comment="Имя кнопки" InitialValue="&apos;&apos;" UUID="KDFI6VOY264UDM3KJBN7EJDJI4" />
                        <VarDeclaration Name="M_Severity" Type="INT" Comment="Серьезность события [1- Низкая, 2-Высокая]" InitialValue="1" UUID="UNEOEJWIT7XEFH2BS2NCVYNH4A" />
                        <VarDeclaration Name="M_Type" Type="STRING" Comment="Тип события" InitialValue="&apos;&apos;" UUID="JIYB2U44MBMEFK3FG4JBPRJWQY" />
                        <VarDeclaration Name="Other" Type="STRING" InitialValue="&apos;&apos;" UUID="A6AMTPSXWTQU5EWCT3JLUMPHCM" />
                        <VarDeclaration Name="Caption" Type="STRING" InitialValue="&apos;&apos;" UUID="OJIBLKHQA7JUBCTGWN624PXGFI" />
                    </InputVars>
                </InterfaceList>
                <FBNetwork>
                    <FB Name="CONCAT_1" Type="CONCAT" TypeUUID="7HP3AWELA2YEXGQJEJ7TED5TRU" Enabled="true" UUID="MOROMA6BXZ6ULCVT2IEKYRZPVA" X="-270.75" Y="870">
                        <VarValue Variable="IN0" Value="&apos;Нажата кнопка: &quot;&apos;" Type="STRING" />
                        <VarValue Variable="IN2" Value="&apos;&quot; &apos;" Type="STRING" />
                        <InterfaceList>
                            <InputVars>
                                <VarDeclaration Name="IN0" Type="STRING" InitialValue="&apos;&apos;" UUID="AXI6CN37DOUUZBRC5BPPTMRVWY" />
                                <VarDeclaration Name="IN1" Type="STRING" InitialValue="&apos;&apos;" UUID="VVFNN5MKVRUU7N3IQCZRJPQYZA" />
                                <VarDeclaration Name="IN2" Type="STRING" InitialValue="&apos;&apos;" UUID="VWALHD4ILK3EHFDCAUCBI5RYTQ" />
                                <VarDeclaration Name="IN3" Type="STRING" InitialValue="&apos;&apos;" UUID="JULHLE2XH7AUHJF6YR6YZ62CUE" />
                            </InputVars>
                            <OutputVars>
                                <VarDeclaration Name="OUT" Type="STRING" InitialValue="&apos;&apos;" UUID="LSW25TPVAJUEDLEA4A36JHIQAU" />
                            </OutputVars>
                        </InterfaceList>
                    </FB>
                    <FB Name="EventRegistrator_1" Type="TEventRegistrator" TypeUUID="OXLMPZHLLMBUHA366SFNI6E7JE" Enabled="true" UUID="HNWEKN2FGTKEPLGSYFFTDJ4ZPU" X="191.75" Y="899">
                        <VarValue Variable="CATEGORY" Value="5" Type="DINT" />
                        <VarValue Variable="SOURCE" Value="&apos;ИБ кнопка&apos;" Type="STRING" />
                        <VarValue Variable="STATE" Value="1" Type="INT" />
                    </FB>
                    <FB Name="IS2_TAG_composit" Type="TIS2_TAG_composit" TypeUUID="RW3EJM6JXFZE5P5ODTVG4VKOZU" Enabled="true" UUID="ULPUV76OIHFUDKY7SJYMWZNHVQ" X="-278.25" Y="1038.375" />
                    <EventConnections>
                        <Connection Source="Registrer" Destination="EventRegistrator_1.E_REGISTER" SourceUUID="F4863EC2452A178A4460539D5B716C64" DestinationUUID="37456C3B47D434454BC1D2AC7D99A731.D2D48FB74E4CC596B8CF8C856673AC58" />
                    </EventConnections>
                    <DataConnections>
                        <Connection Source="NameButton" Destination="CONCAT_1.IN1" SourceUUID="558FCA5041B9D7D85B486AB3476924F2" DestinationUUID="03E6A263457DBEC108D2B38AA82F47AC.F5D64AAD4F69AC8AB38068B7C818BE14" />
                        <Connection Source="Caption" Destination="CONCAT_1.IN3" SourceUUID="A815507240D307F07DB3668A2AE63EAE" DestinationUUID="03E6A263457DBEC108D2B38AA82F47AC.9375164D43C13F577DC4BEA4A142FB8C" />
                        <Connection Source="CONCAT_1.OUT" Destination="EventRegistrator_1.TEXT" SourceUUID="03E6A263457DBEC108D2B38AA82F47AC.CDAEAD5C416802F537E080AC05109DE4" DestinationUUID="37456C3B47D434454BC1D2AC7D99A731.772765ED460DFE7D24CCCBBBF6484CAF" dx1="113" dx2="198" dy="152.5" />
                        <Connection Source="IS2_TAG_composit.OutString" Destination="EventRegistrator_1.TAG" SourceUUID="FF4ADFA241CB41CE70921FABACA765CB.87058C3B4EBCDABBB405A494078BB7BA" DestinationUUID="37456C3B47D434454BC1D2AC7D99A731.7D5023924D24083A40A8E08A50B6771E" dx1="70.5" dx2="198" dy="0.375" />
                        <Connection Source="M_Severity" Destination="IS2_TAG_composit.M_Severety" SourceUUID="26E248A342EE9FC89A96419FE0A7E12A" DestinationUUID="FF4ADFA241CB41CE70921FABACA765CB.9A40058A443B5EF8A89538BC0E292B1B" />
                        <Connection Source="M_Type" Destination="IS2_TAG_composit.M_Type" SourceUUID="531D304A4258609C123765AB8636C517" DestinationUUID="FF4ADFA241CB41CE70921FABACA765CB.E7303F12483CAEA7807E9AAE7298AF69" />
                        <Connection Source="Other" Destination="IS2_TAG_composit.M_Other" SourceUUID="BEC980074EE1B457D29EC29213E731BA" DestinationUUID="FF4ADFA241CB41CE70921FABACA765CB.2EE28A284A09598C8C0BA19CD118DD9E" />
                    </DataConnections>
                </FBNetwork>
            </CompositeFBType>
            <CompositeFBType Name="TIS2_RegEventChangeValue" ShowVarTypes="true" UUID="JML3DHIB6ZTUFIRU6V64OGBK6I">
                <InterfaceList>
                    <EventInputs>
                        <Event Name="Registrer" Comment="Регистрация события" UUID="YI7IN5EKC4VELHKTMBCGI3DRLM" />
                    </EventInputs>
                    <InputVars>
                        <VarDeclaration Name="NameParam" Type="STRING" Comment="Имя кнопки" InitialValue="&apos;&apos;" UUID="KDFI6VOY264UDM3KJBN7EJDJI4" />
                        <VarDeclaration Name="M_Severity" Type="INT" Comment="Серьезность события [1- Низкая, 2-Высокая]" InitialValue="2" UUID="UNEOEJWIT7XEFH2BS2NCVYNH4A" />
                        <VarDeclaration Name="M_Type" Type="STRING" Comment="Тип события" InitialValue="&apos;Изм.зн.&apos;" UUID="JIYB2U44MBMEFK3FG4JBPRJWQY" />
                        <VarDeclaration Name="Other" Type="STRING" InitialValue="&apos;&apos;" UUID="A6AMTPSXWTQU5EWCT3JLUMPHCM" />
                        <VarDeclaration Name="pr_Value" Type="STRING" Comment="Старое значение" InitialValue="&apos;&apos;" UUID="5N5BNK4AVJMUBLZUXPPYKBCN2M" />
                        <VarDeclaration Name="new_Value" Type="STRING" InitialValue="&apos;&apos;" UUID="INW4QSGTHH4EHPEERVIRNWFNTQ" />
                        <VarDeclaration Name="Message" Type="STRING" InitialValue="&apos;Изменено значение параметра: &apos;" UUID="OG23GYQ2JZOEJI7RKJHD7GUJHA" />
                    </InputVars>
                </InterfaceList>
                <FBNetwork>
                    <FB Name="CONCAT_1" Type="CONCAT" TypeUUID="7HP3AWELA2YEXGQJEJ7TED5TRU" Enabled="true" UUID="6FLUVATJCBQETIHGOHKOPCXOAQ" X="-544.75" Y="611">
                        <VarValue Variable="IN2" Value="&apos;&quot; c &apos;" Type="STRING" />
                        <VarValue Variable="IN4" Value="&apos; на &apos;" Type="STRING" />
                        <InterfaceList>
                            <InputVars>
                                <VarDeclaration Name="IN0" Type="STRING" InitialValue="&apos;&apos;" UUID="AXI6CN37DOUUZBRC5BPPTMRVWY" />
                                <VarDeclaration Name="IN1" Type="STRING" InitialValue="&apos;&apos;" UUID="VVFNN5MKVRUU7N3IQCZRJPQYZA" />
                                <VarDeclaration Name="IN2" Type="STRING" InitialValue="&apos;&apos;" UUID="VWALHD4ILK3EHFDCAUCBI5RYTQ" />
                                <VarDeclaration Name="IN3" Type="STRING" InitialValue="&apos;&apos;" UUID="JULHLE2XH7AUHJF6YR6YZ62CUE" />
                                <VarDeclaration Name="IN4" Type="STRING" InitialValue="&apos;&apos;" UUID="ZWU4LPMG5RJURKYMT44BBBTW5M" />
                                <VarDeclaration Name="IN5" Type="STRING" InitialValue="&apos;&apos;" UUID="QLSPSCXBGM2EZLG72W6XP2WELU" />
                            </InputVars>
                            <OutputVars>
                                <VarDeclaration Name="OUT" Type="STRING" InitialValue="&apos;&apos;" UUID="LSW25TPVAJUEDLEA4A36JHIQAU" />
                            </OutputVars>
                        </InterfaceList>
                    </FB>
                    <FB Name="CONCAT1_2_0" Type="CONCAT" TypeUUID="7HP3AWELA2YEXGQJEJ7TED5TRU" Enabled="true" UUID="VOEOBQJISTWUFHDER7EHYTG4KI" X="-544.75" Y="518.875">
                        <VarValue Variable="IN0" Value="&apos;ИБ &apos;" Type="STRING" />
                        <InterfaceList>
                            <InputVars>
                                <VarDeclaration Name="IN0" Type="STRING" InitialValue="&apos;&apos;" UUID="AXI6CN37DOUUZBRC5BPPTMRVWY" />
                                <VarDeclaration Name="IN1" Type="STRING" InitialValue="&apos;&apos;" UUID="VVFNN5MKVRUU7N3IQCZRJPQYZA" />
                            </InputVars>
                            <OutputVars>
                                <VarDeclaration Name="OUT" Type="STRING" InitialValue="&apos;&apos;" UUID="LSW25TPVAJUEDLEA4A36JHIQAU" />
                            </OutputVars>
                        </InterfaceList>
                    </FB>
                    <FB Name="EventRegistrator_1" Type="TEventRegistrator" TypeUUID="OXLMPZHLLMBUHA366SFNI6E7JE" Enabled="true" UUID="4QG3KHNATALE7B26RKFJH5GCYY" X="-93.25" Y="708">
                        <VarValue Variable="CATEGORY" Value="5" Type="DINT" />
                        <VarValue Variable="STATE" Value="1" Type="INT" />
                    </FB>
                    <FB Name="IS2_TAG_composit" Type="TIS2_TAG_composit" TypeUUID="RW3EJM6JXFZE5P5ODTVG4VKOZU" Enabled="true" UUID="B2TDPLGD6UUEFLJMMBH6UMP3WQ" X="-574.75" Y="936.625" />
                    <EventConnections>
                        <Connection Source="Registrer" Destination="EventRegistrator_1.E_REGISTER" SourceUUID="F4863EC2452A178A4460539D5B716C64" DestinationUUID="1DB50DE44F1698A08A8A5E87C6C2F493.D2D48FB74E4CC596B8CF8C856673AC58" />
                    </EventConnections>
                    <DataConnections>
                        <Connection Source="NameParam" Destination="CONCAT_1.IN1" SourceUUID="558FCA5041B9D7D85B486AB3476924F2" DestinationUUID="824A57F149601069D471E6A004EE8AE7.F5D64AAD4F69AC8AB38068B7C818BE14" />
                        <Connection Source="pr_Value" Destination="CONCAT_1.IN3" SourceUUID="AB167AEB4059AA80DFBB34AFD34D0485" DestinationUUID="824A57F149601069D471E6A004EE8AE7.9375164D43C13F577DC4BEA4A142FB8C" />
                        <Connection Source="new_Value" Destination="CONCAT_1.IN5" SourceUUID="48C86D4343F839D3518D84BC9CADD816" DestinationUUID="824A57F149601069D471E6A004EE8AE7.0AF9E4824C3433E1BDD5DFAC5DC4EA77" />
                        <Connection Source="CONCAT1_2_0.OUT" Destination="EventRegistrator_1.SOURCE" SourceUUID="C1E088AB42ED9428C88F649C52DC4C7C.CDAEAD5C416802F537E080AC05109DE4" DestinationUUID="1DB50DE44F1698A08A8A5E87C6C2F493.F36EEF8C49622050FB77A58D834678C9" dx1="185.25" dx2="114.75" dy="296.375" />
                        <Connection Source="Message" Destination="CONCAT_1.IN0" SourceUUID="62B3B571445C4E1A4E52F1A338899A3F" DestinationUUID="824A57F149601069D471E6A004EE8AE7.37E1D1054CA91B7F5EE82286B635B2F9" />
                        <Connection Source="M_Severity" Destination="IS2_TAG_composit.M_Severety" SourceUUID="26E248A342EE9FC89A96419FE0A7E12A" DestinationUUID="AC37A60E4228F5C34F602CADB4FB31EA.9A40058A443B5EF8A89538BC0E292B1B" />
                        <Connection Source="M_Type" Destination="IS2_TAG_composit.M_Type" SourceUUID="531D304A4258609C123765AB8636C517" DestinationUUID="AC37A60E4228F5C34F602CADB4FB31EA.E7303F12483CAEA7807E9AAE7298AF69" />
                        <Connection Source="Other" Destination="IS2_TAG_composit.M_Other" SourceUUID="BEC980074EE1B457D29EC29213E731BA" DestinationUUID="AC37A60E4228F5C34F602CADB4FB31EA.2EE28A284A09598C8C0BA19CD118DD9E" />
                        <Connection Source="IS2_TAG_composit.OutString" Destination="EventRegistrator_1.TAG" SourceUUID="AC37A60E4228F5C34F602CADB4FB31EA.87058C3B4EBCDABBB405A494078BB7BA" DestinationUUID="1DB50DE44F1698A08A8A5E87C6C2F493.7D5023924D24083A40A8E08A50B6771E" dx1="10" dx2="270" dy="-88.875" />
                        <Connection Source="CONCAT_1.OUT" Destination="EventRegistrator_1.TEXT" SourceUUID="824A57F149601069D471E6A004EE8AE7.CDAEAD5C416802F537E080AC05109DE4" DestinationUUID="1DB50DE44F1698A08A8A5E87C6C2F493.772765ED460DFE7D24CCCBBBF6484CAF" dx1="22.5" dx2="277.5" dy="220.5" />
                        <Connection Source="M_Type" Destination="CONCAT1_2_0.IN1" SourceUUID="531D304A4258609C123765AB8636C517" DestinationUUID="C1E088AB42ED9428C88F649C52DC4C7C.F5D64AAD4F69AC8AB38068B7C818BE14" />
                    </DataConnections>
                </FBNetwork>
            </CompositeFBType>
            <CompositeFBType Name="TIS2_TAG_composit" ShowVarTypes="true" UUID="RW3EJM6JXFZE5P5ODTVG4VKOZU">
                <InterfaceList>
                    <InputVars>
                        <VarDeclaration Name="M_Severety" Type="INT" InitialValue="1" UUID="RICUBGXYLY5UJPBYSWUBWKZJBY" />
                        <VarDeclaration Name="M_Type" Type="STRING" InitialValue="&apos;&apos;" UUID="CI7TBZ5HVY6ERLU2P2AGTL4YOI" />
                        <VarDeclaration Name="M_Other" Type="STRING" InitialValue="&apos;&apos;" UUID="FCFOELUMLEEUVHFBBOGJ5XIY2E" />
                    </InputVars>
                    <OutputVars>
                        <VarDeclaration Name="OutString" Type="STRING" InitialValue="&apos;&apos;" UUID="HOGALB533K6E5FFEAW2LVN4LA4" />
                    </OutputVars>
                </InterfaceList>
                <FBNetwork>
                    <FB Name="INT_TO_STRING_0" Type="INT_TO_STRING" TypeUUID="DVKPKBXSXV6URJDEHFQ5RVNGVU" Enabled="true" UUID="UXTJYVN5RRZUXJLKR5J7T6L6RI" Y="16.125" />
                    <FB Name="CONCAT_0" Type="CONCAT" TypeUUID="7HP3AWELA2YEXGQJEJ7TED5TRU" Enabled="true" UUID="2FMLFVYRRCGEXCMTSCAGO6XDXE" X="241">
                        <VarValue Variable="IN0" Value="&apos;Severity=&apos;" Type="STRING" />
                        <VarValue Variable="IN2" Value="&apos; ,Type=&apos;" Type="STRING" />
                        <VarValue Variable="IN4" Value="&apos; ,Node=&apos;" Type="STRING" />
                        <VarValue Variable="IN6" Value="&apos; ,info=&apos;" Type="STRING" />
                        <InterfaceList>
                            <InputVars>
                                <VarDeclaration Name="IN0" Type="STRING" InitialValue="&apos;&apos;" UUID="AXI6CN37DOUUZBRC5BPPTMRVWY" />
                                <VarDeclaration Name="IN1" Type="STRING" InitialValue="&apos;&apos;" UUID="VVFNN5MKVRUU7N3IQCZRJPQYZA" />
                                <VarDeclaration Name="IN2" Type="STRING" InitialValue="&apos;&apos;" UUID="VWALHD4ILK3EHFDCAUCBI5RYTQ" />
                                <VarDeclaration Name="IN3" Type="STRING" InitialValue="&apos;&apos;" UUID="JULHLE2XH7AUHJF6YR6YZ62CUE" />
                                <VarDeclaration Name="IN4" Type="STRING" InitialValue="&apos;&apos;" UUID="ZWU4LPMG5RJURKYMT44BBBTW5M" />
                                <VarDeclaration Name="IN5" Type="STRING" InitialValue="&apos;&apos;" UUID="QLSPSCXBGM2EZLG72W6XP2WELU" />
                                <VarDeclaration Name="IN6" Type="STRING" InitialValue="&apos;&apos;" UUID="A3XB6F245N6EXAYQPJKBTZGCKE" />
                                <VarDeclaration Name="IN7" Type="STRING" InitialValue="&apos;&apos;" UUID="4SXEIB335ZLUNPLTHJVU5OG5IU" />
                            </InputVars>
                            <OutputVars>
                                <VarDeclaration Name="OUT" Type="STRING" InitialValue="&apos;&apos;" UUID="LSW25TPVAJUEDLEA4A36JHIQAU" />
                            </OutputVars>
                        </InterfaceList>
                    </FB>
                    <FB Name="CUR_DATA" Type="CUR_DATA" TypeUUID="63RFPIII26GUTO6ECZZ5724EPY" Enabled="true" UUID="WCR44ETXYSWEVODQ4Y2XGNC3RU" X="-120.25" Y="98.75">
                        <VarValue Variable="VAR" Value="&apos;NodeName&apos;" Type="STRING" />
                    </FB>
                    <DataConnections>
                        <Connection Source="INT_TO_STRING_0.OUT" Destination="CONCAT_0.IN1" SourceUUID="559CE6A54B738CBD538F6AA58A7EF9F9.D89E0AEC4B753921B5BD8AA3C3222244" DestinationUUID="D7B258D14B8C881180909389B9E37A67.F5D64AAD4F69AC8AB38068B7C818BE14" dx1="10" dx2="99.5" dy="0.125" />
                        <Connection Source="M_Severety" Destination="INT_TO_STRING_0.IN0" SourceUUID="9A40058A443B5EF8A89538BC0E292B1B" DestinationUUID="559CE6A54B738CBD538F6AA58A7EF9F9.4A28E63F4A1944460953AD888785193F" />
                        <Connection Source="M_Type" Destination="CONCAT_0.IN3" SourceUUID="E7303F12483CAEA7807E9AAE7298AF69" DestinationUUID="D7B258D14B8C881180909389B9E37A67.9375164D43C13F577DC4BEA4A142FB8C" />
                        <Connection Source="CONCAT_0.OUT" Destination="OutString" SourceUUID="D7B258D14B8C881180909389B9E37A67.CDAEAD5C416802F537E080AC05109DE4" DestinationUUID="87058C3B4EBCDABBB405A494078BB7BA" />
                        <Connection Source="M_Other" Destination="CONCAT_0.IN7" SourceUUID="2EE28A284A09598C8C0BA19CD118DD9E" DestinationUUID="D7B258D14B8C881180909389B9E37A67.0744AEE44657EE7B6B3A73BD45DDB84E" />
                        <Connection Source="CUR_DATA.DATA" Destination="CONCAT_0.IN5" SourceUUID="12CEA3B04AACC47735E670B88D5B3473.F0CAC1EA4C932AC826D10A9E03B0BDB8" DestinationUUID="D7B258D14B8C881180909389B9E37A67.0AF9E4824C3433E1BDD5DFAC5DC4EA77" dx1="12" dx2="196.75" dy="-33.75" />
                    </DataConnections>
                </FBNetwork>
            </CompositeFBType>
            <CompositeFBType Name="TIS2_TAG_composit0" ShowVarTypes="true" UUID="IH2YBCI7JE6UHPPRJGX5WLEOYE">
                <InterfaceList>
                    <InputVars>
                        <VarDeclaration Name="M_Severety" Type="INT" InitialValue="1" UUID="RICUBGXYLY5UJPBYSWUBWKZJBY" />
                        <VarDeclaration Name="M_Type" Type="STRING" InitialValue="&apos;&apos;" UUID="CI7TBZ5HVY6ERLU2P2AGTL4YOI" />
                        <VarDeclaration Name="M_Other" Type="STRING" InitialValue="&apos;&apos;" UUID="FCFOELUMLEEUVHFBBOGJ5XIY2E" />
                    </InputVars>
                    <OutputVars>
                        <VarDeclaration Name="OutString" Type="STRING" InitialValue="&apos;&apos;" UUID="HOGALB533K6E5FFEAW2LVN4LA4" />
                    </OutputVars>
                </InterfaceList>
                <FBNetwork>
                    <FB Name="INT_TO_STRING_0" Type="INT_TO_STRING" TypeUUID="DVKPKBXSXV6URJDEHFQ5RVNGVU" Enabled="true" UUID="J7CFKXMS2KYEDATBMLBN6MIPKY" Y="16.125" />
                    <FB Name="CONCAT_0" Type="CONCAT" TypeUUID="7HP3AWELA2YEXGQJEJ7TED5TRU" Enabled="true" UUID="CAD6WJKOYJHUXLQOWPBCIMC2BY" X="241">
                        <VarValue Variable="IN0" Value="&apos;Severity=&apos;" Type="STRING" />
                        <VarValue Variable="IN2" Value="&apos; ,Type=&apos;" Type="STRING" />
                        <VarValue Variable="IN4" Value="&apos; ,Node=&apos;" Type="STRING" />
                        <VarValue Variable="IN6" Value="&apos; ,info=&apos;" Type="STRING" />
                        <InterfaceList>
                            <InputVars>
                                <VarDeclaration Name="IN0" Type="STRING" InitialValue="&apos;&apos;" UUID="AXI6CN37DOUUZBRC5BPPTMRVWY" />
                                <VarDeclaration Name="IN1" Type="STRING" InitialValue="&apos;&apos;" UUID="VVFNN5MKVRUU7N3IQCZRJPQYZA" />
                                <VarDeclaration Name="IN2" Type="STRING" InitialValue="&apos;&apos;" UUID="VWALHD4ILK3EHFDCAUCBI5RYTQ" />
                                <VarDeclaration Name="IN3" Type="STRING" InitialValue="&apos;&apos;" UUID="JULHLE2XH7AUHJF6YR6YZ62CUE" />
                                <VarDeclaration Name="IN4" Type="STRING" InitialValue="&apos;&apos;" UUID="ZWU4LPMG5RJURKYMT44BBBTW5M" />
                                <VarDeclaration Name="IN5" Type="STRING" InitialValue="&apos;&apos;" UUID="QLSPSCXBGM2EZLG72W6XP2WELU" />
                                <VarDeclaration Name="IN6" Type="STRING" InitialValue="&apos;&apos;" UUID="A3XB6F245N6EXAYQPJKBTZGCKE" />
                                <VarDeclaration Name="IN7" Type="STRING" InitialValue="&apos;&apos;" UUID="4SXEIB335ZLUNPLTHJVU5OG5IU" />
                            </InputVars>
                            <OutputVars>
                                <VarDeclaration Name="OUT" Type="STRING" InitialValue="&apos;&apos;" UUID="LSW25TPVAJUEDLEA4A36JHIQAU" />
                            </OutputVars>
                        </InterfaceList>
                    </FB>
                    <FB Name="CUR_DATA" Type="CUR_DATA" TypeUUID="63RFPIII26GUTO6ECZZ5724EPY" Enabled="true" UUID="ND35LYCPRSBENK4DY6TSEOB5NE" X="-120.25" Y="98.75">
                        <VarValue Variable="VAR" Value="&apos;NodeName&apos;" Type="STRING" />
                    </FB>
                    <DataConnections>
                        <Connection Source="INT_TO_STRING_0.OUT" Destination="CONCAT_0.IN1" SourceUUID="5D55C44F41B0D292C2626182560F31DF.D89E0AEC4B753921B5BD8AA3C3222244" DestinationUUID="25EB07104B4FC24EC2B30EAE0E5A3024.F5D64AAD4F69AC8AB38068B7C818BE14" dx1="10" dx2="99.5" dy="0.125" />
                        <Connection Source="M_Severety" Destination="INT_TO_STRING_0.IN0" SourceUUID="9A40058A443B5EF8A89538BC0E292B1B" DestinationUUID="5D55C44F41B0D292C2626182560F31DF.4A28E63F4A1944460953AD888785193F" />
                        <Connection Source="M_Type" Destination="CONCAT_0.IN3" SourceUUID="E7303F12483CAEA7807E9AAE7298AF69" DestinationUUID="25EB07104B4FC24EC2B30EAE0E5A3024.9375164D43C13F577DC4BEA4A142FB8C" />
                        <Connection Source="CONCAT_0.OUT" Destination="OutString" SourceUUID="25EB07104B4FC24EC2B30EAE0E5A3024.CDAEAD5C416802F537E080AC05109DE4" DestinationUUID="87058C3B4EBCDABBB405A494078BB7BA" />
                        <Connection Source="M_Other" Destination="CONCAT_0.IN7" SourceUUID="2EE28A284A09598C8C0BA19CD118DD9E" DestinationUUID="25EB07104B4FC24EC2B30EAE0E5A3024.0744AEE44657EE7B6B3A73BD45DDB84E" />
                        <Connection Source="CUR_DATA.DATA" Destination="CONCAT_0.IN5" SourceUUID="E0D5F76846828C4FA7C783AB693D3822.F0CAC1EA4C932AC826D10A9E03B0BDB8" DestinationUUID="25EB07104B4FC24EC2B30EAE0E5A3024.0AF9E4824C3433E1BDD5DFAC5DC4EA77" dx1="12" dx2="196.75" dy="-33.75" />
                    </DataConnections>
                </FBNetwork>
            </CompositeFBType>
            <GraphicsCompositeFBType Name="TIS_Admin" ShowVarTypes="true" UUID="RCWMIYTR6S7E5B7443YVEC6FTY">
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
                        <VarDeclaration Name="size" Type="TSize" TypeUUID="XDTT5M52XMSURN23S57SF26UGU" Comment="размер прямоугольника" Group="Общие" InitialValue="(width:=1910,height:=850)" UUID="HC2FKFJ4NBUU3J5U7QZTECI2TM" />
                        <VarDeclaration Name="CaptionForEvent" Type="STRING" InitialValue="&apos;&apos;" UUID="MPEP7H2KZ42URFPEJ2F3AKZKAI" />
                        <VarDeclaration Name="NodeName" Type="STRING" Comment="Наименование данного узла (АРМа)" InitialValue="&apos;&apos;" UUID="IIZGUTRNFFFUXOJLOKXKHVEPOA" />
                    </InputVars>
                </InterfaceList>
                <FBNetwork>
                    <FB Name="CONTROL_CENTER" Type="CONTROL_CENTER" TypeUUID="CK3VDFKOHHGEFLCJP3SFPRPUNI" Enabled="true" UUID="UGWPK762T7KUZBGSYGCGXSS26U" X="-11.1757918639615" Y="1460.10526347535">
                        <VarValue Variable="pos" Value="(x:=21.3926677329803,y:=230)" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" />
                        <VarValue Variable="size" Value="(width:=596,height:=480)" Type="TSize" TypeUUID="XDTT5M52XMSURN23S57SF26UGU" />
                    </FB>
                    <FB Name="TLButton_1" Type="TTLButton" TypeUUID="GCLFMT6OHZVEFEJCWS6KYXUKVM" Enabled="true" UUID="COJP4UCXCBUEDKJV527US53ZXM" X="-1158.46635432441" Y="1038.88818055333">
                        <VarValue Variable="font" Value="(family:=&apos;PT Sans&apos;,size:=16,bold:=FALSE,italic:=FALSE,underline:=FALSE,strikeout:=FALSE)" Type="TFont" TypeUUID="YVT73EACFULUPIWKAFYTDAC3S4" />
                        <VarValue Variable="pos" Value="(x:=26,y:=744)" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" />
                        <VarValue Variable="size" Value="(width:=167,height:=48)" Type="TSize" TypeUUID="XDTT5M52XMSURN23S57SF26UGU" />
                        <VarValue Variable="text" Value="&apos;Настройка$nбазы ИБ&apos;" Type="STRING" />
                    </FB>
                    <FB Name="SYS_EXEC" Type="SYS_EXEC" TypeUUID="HK2J7QJJLTOEXFIGTGWVWBSRQI" Enabled="true" UUID="TDSJ2T265JOU3IJ4IJTGHYNFWY" X="-500.392256919863" Y="580.787020842866" />
                    <FB Name="TLButton" Type="TTLButton" TypeUUID="GCLFMT6OHZVEFEJCWS6KYXUKVM" Enabled="true" UUID="WSTDYCMV5Z3EXG7SMH3COVFSSE" X="-1169.86742100715" Y="22.7122767128358">
                        <VarValue Variable="font" Value="(family:=&apos;PT Sans&apos;,size:=16,bold:=FALSE,italic:=FALSE,underline:=FALSE,strikeout:=FALSE)" Type="TFont" TypeUUID="YVT73EACFULUPIWKAFYTDAC3S4" />
                        <VarValue Variable="pos" Value="(x:=195.39266773298,y:=165.15097210499)" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" />
                        <VarValue Variable="size" Value="(width:=167,height:=48)" Type="TSize" TypeUUID="XDTT5M52XMSURN23S57SF26UGU" />
                        <VarValue Variable="text" Value="&apos;Редактор$nпользователей&apos;" Type="STRING" />
                    </FB>
                    <FB Name="RegEventButton0_5" Type="TIS2RegEventButton" TypeUUID="ZNZZ47LTYMZUNHA2UGTJLLMH7E" Enabled="true" UUID="XBTUYEOZCJTUZPU6P7OTYBDVEI" X="-684.784514123772" Y="179.663759106085">
                        <VarValue Variable="M_Severity" Value="1" Type="INT" />
                        <VarValue Variable="M_Type" Value="&apos;Кнопка&apos;" Type="STRING" />
                        <VarValue Variable="NameButton" Value="&apos;Редактор пользователей&apos;" Type="STRING" />
                        <VarValue Variable="Other" Value="&apos;IS&apos;" Type="STRING" />
                    </FB>
                    <FB Name="USERS_EDITOR_WINDOW" Type="USERS_EDITOR_WINDOW" TypeUUID="O46MCFE2Y75UVH5ZJIRSRGJNRQ" Enabled="true" UUID="7LME3SJ7BZZUJNDSYEGOLMISRU" X="-662.494993742502" Y="22.7122767128358">
                        <VarValue Variable="POS" Value="(x:=375,y:=130)" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" />
                        <VarValue Variable="SIZE" Value="(width:=1000,height:=400)" Type="TSize" TypeUUID="XDTT5M52XMSURN23S57SF26UGU" />
                    </FB>
                    <FB Name="Pixmap0" Type="TPixmap" TypeUUID="EHIXI56IOPNETDXYQD2ICEJMFQ" Enabled="true" UUID="774ZXJXSIGHEVNM2VEWKDTTLQ4" X="27.2351428472728" Y="936.946138600639">
                        <VarValue Variable="image" Value="&apos;IS&apos;" Type="TImage" TypeUUID="GSTTLCO6AMVU3E4NAYBZLAAECQ" />
                        <VarValue Variable="pos" Value="(x:=14,y:=25.6297049067704)" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" />
                        <VarValue Variable="size" Value="(width:=120,height:=150)" Type="TSize" TypeUUID="XDTT5M52XMSURN23S57SF26UGU" />
                        <VarValue Variable="zValue" Value="1" Type="LREAL" />
                    </FB>
                    <FB Name="Text0_0" Type="TSimpleText" TypeUUID="OBURUFGSRT7UVLSMGMSUGBKM5E" Enabled="true" UUID="WAIULAA5MCOETD6U4WSSNVMSN4" X="19.6121861934098">
                        <VarValue Variable="alignment" Value="6" Type="TAlignment" TypeUUID="IUA2FTZVSF6EVJPPY3ZKXNHV6E" />
                        <VarValue Variable="font" Value="(family:=&apos;PT Sans&apos;,size:=27,bold:=TRUE,italic:=FALSE,underline:=FALSE,strikeout:=FALSE)" Type="TFont" TypeUUID="YVT73EACFULUPIWKAFYTDAC3S4" />
                        <VarValue Variable="pos" Value="(x:=206.134900247617,y:=57.8928628015073)" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" />
                        <VarValue Variable="size" Value="(width:=304,height:=72)" Type="TSize" TypeUUID="XDTT5M52XMSURN23S57SF26UGU" />
                        <VarValue Variable="text" Value="&apos;Информационая$nБезопасность&apos;" Type="STRING" />
                        <VarValue Variable="text_color" Value="4283010762" Type="TColor" TypeUUID="EDYJMIBCJR5UJOZWGS3UVJENZA" />
                        <VarValue Variable="wordWrap" Value="TRUE" Type="BOOL" />
                        <VarValue Variable="zValue" Value="1" Type="LREAL" />
                    </FB>
                    <FB Name="RegEventButton0_6" Type="TIS2RegEventButton" TypeUUID="ZNZZ47LTYMZUNHA2UGTJLLMH7E" Enabled="true" UUID="AZSFJASBWVJUHDXTHOCPEXWF5A" X="-783.625931413153" Y="417.838194539586">
                        <VarValue Variable="M_Severity" Value="1" Type="INT" />
                        <VarValue Variable="M_Type" Value="&apos;Кнопка&apos;" Type="STRING" />
                        <VarValue Variable="NameButton" Value="&apos;Просмотр событий&apos;" Type="STRING" />
                        <VarValue Variable="Other" Value="&apos;IS&apos;" Type="STRING" />
                    </FB>
                    <FB Name="TLButton_0" Type="TTLButton" TypeUUID="GCLFMT6OHZVEFEJCWS6KYXUKVM" Enabled="true" UUID="CUEY7WFDXVLU5CM65ODKEMDPDY" X="-1169.86742100715" Y="567.712276712836">
                        <VarValue Variable="font" Value="(family:=&apos;PT Sans&apos;,size:=16,bold:=FALSE,italic:=FALSE,underline:=FALSE,strikeout:=FALSE)" Type="TFont" TypeUUID="YVT73EACFULUPIWKAFYTDAC3S4" />
                        <VarValue Variable="pos" Value="(x:=386.39266773298,y:=165)" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" />
                        <VarValue Variable="size" Value="(width:=167,height:=48)" Type="TSize" TypeUUID="XDTT5M52XMSURN23S57SF26UGU" />
                        <VarValue Variable="text" Value="&apos;Просмотр$nсобытий&apos;" Type="STRING" />
                    </FB>
                    <FB Name="Rect" Type="TRect" TypeUUID="24POL55EVH5U5GD3E4VMTU2OW4" Enabled="true" UUID="MARZMTWFVBUUBL4AMM7CNSZMOM" X="27.1121861934098" Y="404">
                        <VarValue Variable="bg_color" Value="4290822336" Type="TColor" TypeUUID="EDYJMIBCJR5UJOZWGS3UVJENZA" />
                        <VarValue Variable="frame_color" Value="4286611584" Type="TColor" TypeUUID="EDYJMIBCJR5UJOZWGS3UVJENZA" />
                        <VarValue Variable="frame_width" Value="2" Type="UINT" />
                        <VarValue Variable="pos" Value="(x:=0,y:=0)" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" />
                        <VarValue Variable="zValue" Value="-1" Type="LREAL" />
                    </FB>
                    <FB Name="_DataBaseIB_Wnd" Type="T_DataBaseIB_Wnd" TypeUUID="NEHN2R3G67NEJBQONRZIKOVIIU" Enabled="true" UUID="R7SXRBRTLY5EDBTKWGZSKJP65A" X="-579.576965033491" Y="1039.46534624824">
                        <VarValue Variable="bg_color" Value="4290822336" Type="TColor" TypeUUID="EDYJMIBCJR5UJOZWGS3UVJENZA" />
                        <VarValue Variable="caption" Value="&apos;Настройка базы ИБ&apos;" Type="STRING" />
                        <VarValue Variable="caption_font" Value="(family:=&apos;PT Sans&apos;,size:=13,bold:=FALSE,italic:=FALSE,underline:=FALSE,strikeout:=FALSE)" Type="TFont" TypeUUID="YVT73EACFULUPIWKAFYTDAC3S4" />
                        <VarValue Variable="closable" Value="TRUE" Type="BOOL" />
                        <VarValue Variable="moveable" Value="TRUE" Type="BOOL" />
                        <VarValue Variable="pos" Value="(x:=60,y:=360)" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" />
                    </FB>
                    <FB Name="TLButton_8" Type="TTLButton" TypeUUID="GCLFMT6OHZVEFEJCWS6KYXUKVM" Enabled="true" UUID="UJRYQ26D5GIUVAU2OJAY6LP3L4" X="-1178.2348420143" Y="1562.46442619612">
                        <VarValue Variable="font" Value="(family:=&apos;PT Sans&apos;,size:=16,bold:=FALSE,italic:=FALSE,underline:=FALSE,strikeout:=FALSE)" Type="TFont" TypeUUID="YVT73EACFULUPIWKAFYTDAC3S4" />
                        <VarValue Variable="pos" Value="(x:=378.39266773298,y:=744)" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" />
                        <VarValue Variable="size" Value="(width:=167,height:=48)" Type="TSize" TypeUUID="XDTT5M52XMSURN23S57SF26UGU" />
                        <VarValue Variable="text" Value="&apos;Выгрузка$nданных в csv&apos;" Type="STRING" />
                    </FB>
                    <FB Name="RegEventButton0_7" Type="TIS2RegEventButton" TypeUUID="ZNZZ47LTYMZUNHA2UGTJLLMH7E" Enabled="true" UUID="SE2DW7ZPRQMU3FBBVDXIHRMRII" X="-723.734842014305" Y="1747.46442619612">
                        <VarValue Variable="M_Severity" Value="1" Type="INT" />
                        <VarValue Variable="M_Type" Value="&apos;Кнопка&apos;" Type="STRING" />
                        <VarValue Variable="NameButton" Value="&apos;Выгрузка данных в csv-файл&apos;" Type="STRING" />
                        <VarValue Variable="Other" Value="&apos;IS&apos;" Type="STRING" />
                    </FB>
                    <FB Name="EventRegistrator" Type="TEventRegistrator" TypeUUID="OXLMPZHLLMBUHA366SFNI6E7JE" Enabled="true" UUID="DVGGKXK3AIFUZMEWQMXKOAYBT4" X="-372.494993742502" Y="23.7122767128358">
                        <VarValue Variable="CATEGORY" Value="5" Type="DINT" />
                        <VarValue Variable="SOURCE" Value="&apos;ИБ&apos;" Type="STRING" />
                        <VarValue Variable="STATE" Value="1" Type="INT" />
                        <VarValue Variable="TAG" Value="&apos;IS&apos;" Type="STRING" />
                        <VarValue Variable="TEXT" Value="&apos;Открыт редактор пользователей&apos;" Type="STRING" />
                    </FB>
                    <FB Name="EventRegistrator_0" Type="TEventRegistrator" TypeUUID="OXLMPZHLLMBUHA366SFNI6E7JE" Enabled="true" UUID="ZENZNUBGH2YU7NDURWAOOVIJNQ" X="-251.255968212199" Y="1105.14768982659">
                        <VarValue Variable="CATEGORY" Value="5" Type="DINT" />
                        <VarValue Variable="SOURCE" Value="&apos;ИБ&apos;" Type="STRING" />
                        <VarValue Variable="STATE" Value="1" Type="INT" />
                        <VarValue Variable="TAG" Value="&apos;IS&apos;" Type="STRING" />
                        <VarValue Variable="TEXT" Value="&apos;Открыто окно настройки базы данных ИБ&apos;" Type="STRING" />
                    </FB>
                    <FB Name="IS2RegEventButton" Type="TIS2RegEventButton" TypeUUID="ZNZZ47LTYMZUNHA2UGTJLLMH7E" Enabled="true" UUID="B3YVF3QOXA5EPCEYV3E7UGZCLU" X="-840.469777236051" Y="1164.21179734207">
                        <VarValue Variable="M_Type" Value="&apos;Кнопка&apos;" Type="STRING" />
                        <VarValue Variable="NameButton" Value="&apos;Настройка базы данных ИБ&apos;" Type="STRING" />
                        <VarValue Variable="Other" Value="&apos;IS&apos;" Type="STRING" />
                    </FB>
                    <FB Name="SET_SIGNAL_DATA" Type="SET_SIGNAL_DATA" TypeUUID="DD2Z7RQDF3WU7JTZYWZ2CNRCYQ" Enabled="true" UUID="YXQRMZNBKVFUFAWNYAJ5W4SMKU" X="-565.75" Y="1595.375">
                        <VarValue Variable="NAME" Value="&apos;DumpBD&apos;" Type="STRING" />
                        <VarValue Variable="VALUE" Value="TRUE" Type="BOOL" />
                    </FB>
                    <FB Name="SEL" Type="SEL" TypeUUID="VTYYYXK24ZYEFIHECN6CYXIJ5M" Enabled="true" UUID="N6L72R6JXC7UTKS26LZ6H4UNIU" X="-730.75" Y="618.625">
                        <VarValue Variable="IN0" Value="&apos;ArchiveViewer&apos;" Type="STRING" />
                        <VarValue Variable="IN1" Value="&apos;viewArchiveViewer.bat&apos;" Type="STRING" />
                    </FB>
                    <FB Name="SEL_0" Type="SEL" TypeUUID="VTYYYXK24ZYEFIHECN6CYXIJ5M" Enabled="true" UUID="6YZ24XI6AYTUNH22RCJG52TEBE" X="-729.75" Y="704.625">
                        <VarValue Variable="IN0" Value="&apos;-ISViewer&apos;" Type="STRING" />
                        <VarValue Variable="IN1" Value="&apos;&apos;" Type="STRING" />
                    </FB>
                    <FB Name="SYS_EXEC_0" Type="SYS_EXEC" TypeUUID="HK2J7QJJLTOEXFIGTGWVWBSRQI" Enabled="true" UUID="JY64XSYVMEDELC4YDWQTBGKHXE" X="-349.892256919863" Y="744.787020842866">
                        <VarValue Variable="ARGS" Value="&apos;-w &quot;Просмоторщик архивов&quot; -m &quot;700x75&quot; -s$n&quot;1120x610&quot;&apos;" Type="STRING" />
                        <VarValue Variable="PATH" Value="&apos;moveWindow&apos;" Type="STRING" />
                    </FB>
                    <FB Name="E_DELAY" Type="E_DELAY" TypeUUID="2UL67RXFAKEEBJ7U5KGKPTHBG4" Enabled="true" UUID="XKCQG65BP6RUNM4KH6ISQYHJYM" X="-791.25" Y="824.75">
                        <VarValue Variable="DTV" Value="T#500ms" Type="TIME" />
                    </FB>
                    <FB Name="E_SWITCH" Type="E_SWITCH" TypeUUID="3MXTNNSUMXOUPAEPMHDP4LGC44" Enabled="true" UUID="4PEBT3HFOJKERJEEN6FRKK44MU" X="-576.75" Y="808.75" />
                    <EventConnections>
                        <Connection Source="TLButton.clicked" Destination="USERS_EDITOR_WINDOW.SHOW_MODAL" SourceUUID="093CA6B44B76EE95F661F29B91B25427.A24F9CF5410E51D044BD3D8F84270DD4" DestinationUUID="C94DD8FA44730E3F0CC172B48D12B1E5.F3C23704465BE96DC67CBFB1FE25B27F" dx1="252.872" dx2="41.0004" />
                        <Connection Source="TLButton.clicked" Destination="RegEventButton0_5.Registrer" SourceUUID="093CA6B44B76EE95F661F29B91B25427.A24F9CF5410E51D044BD3D8F84270DD4" DestinationUUID="114C67B84C6712D9DD7F9EBE2275043C.F4863EC2452A178A4460539D5B716C64" dx1="261.583" dx2="10" dy="156.951" />
                        <Connection Source="TLButton_8.released" Destination="RegEventButton0_7.Registrer" SourceUUID="6B8863A24A91E9C341729A825FFB2D8F.66A71E404776B337D5781191EAC566A5" DestinationUUID="7F3B34914D198C2FEEA821944291C583.F4863EC2452A178A4460539D5B716C64" dx1="183" dx2="58" dy="152.5" />
                        <Connection Source="TLButton_1.clicked" Destination="_DataBaseIB_Wnd.show" SourceUUID="50FE921341681057BFEE35A9BB797749.A24F9CF5410E51D044BD3D8F84270DD4" DestinationUUID="8678E58F413A5E33B3B16A86E8FE2525.C7EAA1EB434D26CD0E95FEB5B380ED33" dx1="213.599" dx2="151.79" dy="0.577166" />
                        <Connection Source="USERS_EDITOR_WINDOW.SHOWED" Destination="EventRegistrator.E_REGISTER" SourceUUID="C94DD8FA44730E3F0CC172B48D12B1E5.B7FB895E467405BF523BCB8A574A463F" DestinationUUID="5D654C1D4C0B025B2E8396B09F0103A7.D2D48FB74E4CC596B8CF8C856673AC58" dx1="139" dx2="10" dy="49.75" />
                        <Connection Source="_DataBaseIB_Wnd.showed" Destination="EventRegistrator_0.E_REGISTER" SourceUUID="8678E58F413A5E33B3B16A86E8FE2525.9EA97E954ACBA70E705C4F98412FA701" DestinationUUID="D0961BC94FB13E26808D74B46C0955E7.D2D48FB74E4CC596B8CF8C856673AC58" dx1="75.1714" dx2="38.1496" dy="0.682344" />
                        <Connection Source="TLButton_1.clicked" Destination="IS2RegEventButton.Registrer" SourceUUID="50FE921341681057BFEE35A9BB797749.A24F9CF5410E51D044BD3D8F84270DD4" DestinationUUID="EE52F10E473AB80EC9AE98885D221BFA.F4863EC2452A178A4460539D5B716C64" dx1="94.4966" dx2="10" dy="125.324" />
                        <Connection Source="TLButton_8.released" Destination="SET_SIGNAL_DATA.SET" SourceUUID="6B8863A24A91E9C341729A825FFB2D8F.66A71E404776B337D5781191EAC566A5" DestinationUUID="6516E1C5424B55A113C0CD82554C72DB.EEC8DDD84177096204868498B840BA96" dx1="204" dx2="194.985" dy="0.410574" />
                        <Connection Source="TLButton_0.pressed" Destination="RegEventButton0_6.Registrer" SourceUUID="D88F09154E57BDA386EB9E891E6F30A2.8009D6224C2F388DDFFFF5AA7C8FED14" DestinationUUID="825464064353B541843BF38EE8C55EF2.F4863EC2452A178A4460539D5B716C64" dx1="98.7415" dx2="74" dy="-166.124" />
                        <Connection Source="TLButton_0.pressed" Destination="SYS_EXEC.EXEC" SourceUUID="D88F09154E57BDA386EB9E891E6F30A2.8009D6224C2F388DDFFFF5AA7C8FED14" DestinationUUID="4F9DE4984D5DEA5E66423CA1B6A5E163.AAC0A63A475DF9611D1B2B9BE3D0C24C" dx1="323.975" dx2="132" dy="-3.17526" />
                        <Connection Source="TLButton_0.released" Destination="E_DELAY.START" SourceUUID="D88F09154E57BDA386EB9E891E6F30A2.66A71E404776B337D5781191EAC566A5" DestinationUUID="7B0385BA46A37FA1913F8AB3C3E96028.FADB31D0469FF55F7032E998D9F6371C" dx1="100.117" dx2="65" dy="224.538" />
                        <Connection Source="E_SWITCH.EO0" Destination="SYS_EXEC_0.EXEC" SourceUUID="EC19C8E3485472E58B6F84A4659C2B15.F6ABFEF04287F2E24DCCA8AB13C6CD6A" DestinationUUID="CBCB3D4E45066115A11D988BB9479930.AAC0A63A475DF9611D1B2B9BE3D0C24C" dx1="10" dx2="133.358" dy="-63.963" />
                        <Connection Source="E_DELAY.EO" Destination="E_SWITCH.EI" SourceUUID="7B0385BA46A37FA1913F8AB3C3E96028.32DC48154280010E6D51BEA646841346" DestinationUUID="EC19C8E3485472E58B6F84A4659C2B15.98FFB8864D31BE5A9B524B948ACD80C2" dx1="23" dx2="105" dy="-16" />
                    </EventConnections>
                    <DataConnections>
                        <Connection Source="CaptionForEvent" Destination="RegEventButton0_5.Caption" SourceUUID="9FFFC8634835CF4A8B4EE495022A2BB0" DestinationUUID="114C67B84C6712D9DD7F9EBE2275043C.A815507240D307F07DB3668A2AE63EAE" />
                        <Connection Source="CaptionForEvent" Destination="RegEventButton0_6.Caption" SourceUUID="9FFFC8634835CF4A8B4EE495022A2BB0" DestinationUUID="825464064353B541843BF38EE8C55EF2.A815507240D307F07DB3668A2AE63EAE" />
                        <Connection Source="size" Destination="Rect.size" SourceUUID="1555B4384D69683C33FCB4A79B1A0932" DestinationUUID="4E9623604069A8C53E6380AF732CCB26.1555B4384D69683C33FCB4A79B1A0932" />
                        <Connection Source="CaptionForEvent" Destination="RegEventButton0_7.Caption" SourceUUID="9FFFC8634835CF4A8B4EE495022A2BB0" DestinationUUID="7F3B34914D198C2FEEA821944291C583.A815507240D307F07DB3668A2AE63EAE" />
                        <Connection Source="CaptionForEvent" Destination="IS2RegEventButton.Caption" SourceUUID="9FFFC8634835CF4A8B4EE495022A2BB0" DestinationUUID="EE52F10E473AB80EC9AE98885D221BFA.A815507240D307F07DB3668A2AE63EAE" />
                        <Connection Source="visible" Destination="_DataBaseIB_Wnd.enabled" SourceUUID="EAC5288F431A370F7493EF98A2C613D5" DestinationUUID="8678E58F413A5E33B3B16A86E8FE2525.15B097034B9BBE7CCD78E0A466A64239" />
                        <Connection Source="::Type_OS" Destination="SEL.G" SourceUUID="::382C7B3F4F968524ED502AAE50912879" DestinationUUID="47FD976F49BFB8C9F3F25AAA458DF2E3.E51CF88C46776F33BF0D21B3F4741605" />
                        <Connection Source="SEL.OUT" Destination="SYS_EXEC.PATH" SourceUUID="47FD976F49BFB8C9F3F25AAA458DF2E3.D94D29B049B6DB4E0A29EA9CB5266805" DestinationUUID="4F9DE4984D5DEA5E66423CA1B6A5E163.1026E31F4785E5C5C6BFD4BF35DA618B" dx1="10" dx2="102.858" dy="-11.838" />
                        <Connection Source="::Type_OS" Destination="SEL_0.G" SourceUUID="::382C7B3F4F968524ED502AAE50912879" DestinationUUID="5DAE33F64627061E92885A9F0964EA6E.E51CF88C46776F33BF0D21B3F4741605" />
                        <Connection Source="SEL_0.OUT" Destination="SYS_EXEC.ARGS" SourceUUID="5DAE33F64627061E92885A9F0964EA6E.D94D29B049B6DB4E0A29EA9CB5266805" DestinationUUID="4F9DE4984D5DEA5E66423CA1B6A5E163.ED447FF841BAF4005DD12F977DEFF8D2" dx1="40.8577" dx2="71" dy="-81.588" />
                        <Connection Source="::Type_OS" Destination="E_SWITCH.G" SourceUUID="::382C7B3F4F968524ED502AAE50912879" DestinationUUID="EC19C8E3485472E58B6F84A4659C2B15.63821D1741822EDE40CCAF8A2ECE8F83" />
                    </DataConnections>
                </FBNetwork>
            </GraphicsCompositeFBType>
            <CompositeFBType Name="TIS_RegEvent3Cat" ShowVarTypes="true" UUID="ZLJGKUXENPYEVM6AQX5RGFE4HQ">
                <InterfaceList>
                    <EventInputs>
                        <Event Name="Registrer" Comment="Регистрация события" UUID="YI7IN5EKC4VELHKTMBCGI3DRLM" />
                    </EventInputs>
                    <InputVars>
                        <VarDeclaration Name="Name" Type="STRING" Comment="Имя кнопки" InitialValue="&apos;&apos;" UUID="KDFI6VOY264UDM3KJBN7EJDJI4" />
                        <VarDeclaration Name="M_Severity" Type="INT" Comment="Серьезность события [1- Низкая, 2-Высокая]" InitialValue="2" UUID="UNEOEJWIT7XEFH2BS2NCVYNH4A" />
                        <VarDeclaration Name="M_Type" Type="STRING" Comment="Тип события" InitialValue="&apos;Изм.зн.&apos;" UUID="JIYB2U44MBMEFK3FG4JBPRJWQY" />
                        <VarDeclaration Name="NameRu" Type="STRING" InitialValue="&apos;&apos;" UUID="A6AMTPSXWTQU5EWCT3JLUMPHCM" />
                        <VarDeclaration Name="PrefAb" Type="STRING" InitialValue="&apos;&apos;" UUID="ERRJVMLB3FHEXHSMMDWWV4M4RE" />
                        <VarDeclaration Name="Message" Type="STRING" InitialValue="&apos;Изменено значение параметра: &apos;" UUID="OG23GYQ2JZOEJI7RKJHD7GUJHA" />
                    </InputVars>
                </InterfaceList>
                <FBNetwork>
                    <FB Name="CONCAT1_2_0" Type="CONCAT" TypeUUID="7HP3AWELA2YEXGQJEJ7TED5TRU" Enabled="true" UUID="TGWECWDMATLE5D5BTNKGSSK72A" X="-554.75" Y="689.875">
                        <VarValue Variable="IN1" Value="&apos; &apos;" Type="STRING" />
                        <InterfaceList>
                            <InputVars>
                                <VarDeclaration Name="IN0" Type="STRING" InitialValue="&apos;&apos;" UUID="AXI6CN37DOUUZBRC5BPPTMRVWY" />
                                <VarDeclaration Name="IN1" Type="STRING" InitialValue="&apos;&apos;" UUID="VVFNN5MKVRUU7N3IQCZRJPQYZA" />
                                <VarDeclaration Name="IN2" Type="STRING" InitialValue="&apos;&apos;" UUID="VWALHD4ILK3EHFDCAUCBI5RYTQ" />
                            </InputVars>
                            <OutputVars>
                                <VarDeclaration Name="OUT" Type="STRING" InitialValue="&apos;&apos;" UUID="LSW25TPVAJUEDLEA4A36JHIQAU" />
                            </OutputVars>
                        </InterfaceList>
                    </FB>
                    <FB Name="IS_TAG_composit_0" Type="TIS_TAG_composit" TypeUUID="QD5I7AVBOQPEBHS542ZLP4TZYY" Enabled="true" UUID="OPCPMAMBDEPEBAIKO2MGYHWEHA" X="-560.75" Y="949.375" />
                    <FB Name="EventRegistrator_1" Type="TEventRegistrator" TypeUUID="OXLMPZHLLMBUHA366SFNI6E7JE" Enabled="true" UUID="HT2WZYDMPIBULOUXCTX6NA4NIY" X="-93.25" Y="708">
                        <VarValue Variable="CATEGORY" Value="3" Type="DINT" />
                        <VarValue Variable="STATE" Value="1" Type="INT" />
                    </FB>
                    <FB Name="CONCAT1_2_1" Type="CONCAT" TypeUUID="7HP3AWELA2YEXGQJEJ7TED5TRU" Enabled="true" UUID="X2RTEDMXRFXEHJUWFBHMUE4D4E" X="-547.25" Y="831.875">
                        <InterfaceList>
                            <InputVars>
                                <VarDeclaration Name="IN0" Type="STRING" InitialValue="&apos;&apos;" UUID="AXI6CN37DOUUZBRC5BPPTMRVWY" />
                                <VarDeclaration Name="IN1" Type="STRING" InitialValue="&apos;&apos;" UUID="VVFNN5MKVRUU7N3IQCZRJPQYZA" />
                            </InputVars>
                            <OutputVars>
                                <VarDeclaration Name="OUT" Type="STRING" InitialValue="&apos;&apos;" UUID="LSW25TPVAJUEDLEA4A36JHIQAU" />
                            </OutputVars>
                        </InterfaceList>
                    </FB>
                    <EventConnections>
                        <Connection Source="Registrer" Destination="EventRegistrator_1.E_REGISTER" SourceUUID="F4863EC2452A178A4460539D5B716C64" DestinationUUID="E06CF53C45037A6CEF1497BA468D83E6.D2D48FB74E4CC596B8CF8C856673AC58" />
                    </EventConnections>
                    <DataConnections>
                        <Connection Source="NameRu" Destination="CONCAT1_2_0.IN0" SourceUUID="BEC980074EE1B457D29EC29213E731BA" DestinationUUID="5841AC994ED6046C549BA18FD05F4969.37E1D1054CA91B7F5EE82286B635B2F9" />
                        <Connection Source="M_Severity" Destination="IS_TAG_composit_0.M_Severety" SourceUUID="26E248A342EE9FC89A96419FE0A7E12A" DestinationUUID="01F6C473401E198198760A8138C41E6C.9A40058A443B5EF8A89538BC0E292B1B" />
                        <Connection Source="M_Type" Destination="IS_TAG_composit_0.M_Type" SourceUUID="531D304A4258609C123765AB8636C517" DestinationUUID="01F6C473401E198198760A8138C41E6C.E7303F12483CAEA7807E9AAE7298AF69" />
                        <Connection Source="PrefAb" Destination="IS_TAG_composit_0.M_PrefAb" SourceUUID="B19A62244B4ED961ED604C9E899CF16A" DestinationUUID="01F6C473401E198198760A8138C41E6C.63B569DE4F54176BBFCDF3AF435E2E54" />
                        <Connection Source="NameRu" Destination="IS_TAG_composit_0.M_NameRu" SourceUUID="BEC980074EE1B457D29EC29213E731BA" DestinationUUID="01F6C473401E198198760A8138C41E6C.2EE28A284A09598C8C0BA19CD118DD9E" />
                        <Connection Source="M_Type" Destination="CONCAT1_2_0.IN2" SourceUUID="531D304A4258609C123765AB8636C517" DestinationUUID="5841AC994ED6046C549BA18FD05F4969.8FB380AD43B65A88040562949C387614" />
                        <Connection Source="IS_TAG_composit_0.OutString" Destination="EventRegistrator_1.TAG" SourceUUID="01F6C473401E198198760A8138C41E6C.87058C3B4EBCDABBB405A494078BB7BA" DestinationUUID="E06CF53C45037A6CEF1497BA468D83E6.7D5023924D24083A40A8E08A50B6771E" dx1="59.25" dx2="192.75" dy="-101.625" />
                        <Connection Source="CONCAT1_2_0.OUT" Destination="EventRegistrator_1.SOURCE" SourceUUID="5841AC994ED6046C549BA18FD05F4969.CDAEAD5C416802F537E080AC05109DE4" DestinationUUID="E06CF53C45037A6CEF1497BA468D83E6.F36EEF8C49622050FB77A58D834678C9" dx1="195.25" dx2="114.75" dy="125.375" />
                        <Connection Source="CONCAT1_2_1.OUT" Destination="EventRegistrator_1.TEXT" SourceUUID="0D32A3BE436E89974E2896A6E18313CA.CDAEAD5C416802F537E080AC05109DE4" DestinationUUID="E06CF53C45037A6CEF1497BA468D83E6.772765ED460DFE7D24CCCBBBF6484CAF" dx1="25" dx2="277.5" dy="-0.375" />
                        <Connection Source="Message" Destination="CONCAT1_2_1.IN0" SourceUUID="62B3B571445C4E1A4E52F1A338899A3F" DestinationUUID="0D32A3BE436E89974E2896A6E18313CA.37E1D1054CA91B7F5EE82286B635B2F9" />
                        <Connection Source="Name" Destination="CONCAT1_2_1.IN1" SourceUUID="558FCA5041B9D7D85B486AB3476924F2" DestinationUUID="0D32A3BE436E89974E2896A6E18313CA.F5D64AAD4F69AC8AB38068B7C818BE14" />
                    </DataConnections>
                </FBNetwork>
            </CompositeFBType>
            <CompositeFBType Name="TIS_TAG_composit" ShowVarTypes="true" UUID="QD5I7AVBOQPEBHS542ZLP4TZYY">
                <InterfaceList>
                    <InputVars>
                        <VarDeclaration Name="M_Severety" Type="INT" InitialValue="0" UUID="RICUBGXYLY5UJPBYSWUBWKZJBY" />
                        <VarDeclaration Name="M_Type" Type="STRING" InitialValue="&apos;&apos;" UUID="CI7TBZ5HVY6ERLU2P2AGTL4YOI" />
                        <VarDeclaration Name="M_AlgName" Type="STRING" InitialValue="&apos;&apos;" UUID="QEOF6GXXLJEEFOVOSNDHJRLBHU" />
                        <VarDeclaration Name="M_PrefAb" Type="STRING" InitialValue="&apos;&apos;" UUID="3ZU3KY3LC5KE7L7TZW7VILS6IM" />
                        <VarDeclaration Name="M_NameRu" Type="STRING" InitialValue="&apos;&apos;" UUID="FCFOELUMLEEUVHFBBOGJ5XIY2E" />
                    </InputVars>
                    <OutputVars>
                        <VarDeclaration Name="OutString" Type="STRING" InitialValue="&apos;&apos;" UUID="HOGALB533K6E5FFEAW2LVN4LA4" />
                    </OutputVars>
                </InterfaceList>
                <FBNetwork>
                    <FB Name="INT_TO_STRING_0" Type="INT_TO_STRING" TypeUUID="DVKPKBXSXV6URJDEHFQ5RVNGVU" Enabled="true" UUID="YMPEV6D56KSENFGRX7KPPH2S3Q" Y="16.125" />
                    <FB Name="CONCAT_0" Type="CONCAT" TypeUUID="7HP3AWELA2YEXGQJEJ7TED5TRU" Enabled="true" UUID="X2V3MTAVSNAUBLVSQD4CBTBJUQ" X="241" InputCount="10">
                        <VarValue Variable="IN0" Value="&apos;Severity=&apos;" Type="STRING" />
                        <VarValue Variable="IN2" Value="&apos; ,Type=&apos;" Type="STRING" />
                        <VarValue Variable="IN4" Value="&apos; ,AlgName=&apos;" Type="STRING" />
                        <VarValue Variable="IN6" Value="&apos; ,PrefAb=&apos;" Type="STRING" />
                        <VarValue Variable="IN8" Value="&apos; ,NameRu=&apos;" Type="STRING" />
                        <InterfaceList>
                            <InputVars>
                                <VarDeclaration Name="IN0" Type="STRING" InitialValue="&apos;&apos;" UUID="AXI6CN37DOUUZBRC5BPPTMRVWY" />
                                <VarDeclaration Name="IN1" Type="STRING" InitialValue="&apos;&apos;" UUID="VVFNN5MKVRUU7N3IQCZRJPQYZA" />
                                <VarDeclaration Name="IN2" Type="STRING" InitialValue="&apos;&apos;" UUID="VWALHD4ILK3EHFDCAUCBI5RYTQ" />
                                <VarDeclaration Name="IN3" Type="STRING" InitialValue="&apos;&apos;" UUID="JULHLE2XH7AUHJF6YR6YZ62CUE" />
                                <VarDeclaration Name="IN4" Type="STRING" InitialValue="&apos;&apos;" UUID="ZWU4LPMG5RJURKYMT44BBBTW5M" />
                                <VarDeclaration Name="IN5" Type="STRING" InitialValue="&apos;&apos;" UUID="QLSPSCXBGM2EZLG72W6XP2WELU" />
                                <VarDeclaration Name="IN6" Type="STRING" InitialValue="&apos;&apos;" UUID="A3XB6F245N6EXAYQPJKBTZGCKE" />
                                <VarDeclaration Name="IN7" Type="STRING" InitialValue="&apos;&apos;" UUID="4SXEIB335ZLUNPLTHJVU5OG5IU" />
                                <VarDeclaration Name="IN8" Type="STRING" InitialValue="&apos;&apos;" UUID="DSBHNCBOLXQEVEKACQMZVLZJUY" />
                                <VarDeclaration Name="IN9" Type="STRING" InitialValue="&apos;&apos;" UUID="EOQIB7P3PBEU7PZPRTVFEFGXNI" />
                            </InputVars>
                            <OutputVars>
                                <VarDeclaration Name="OUT" Type="STRING" InitialValue="&apos;&apos;" UUID="LSW25TPVAJUEDLEA4A36JHIQAU" />
                            </OutputVars>
                        </InterfaceList>
                    </FB>
                    <DataConnections>
                        <Connection Source="INT_TO_STRING_0.OUT" Destination="CONCAT_0.IN1" SourceUUID="F84A1EC346A4F27DD4BFD194DC529FF7.D89E0AEC4B753921B5BD8AA3C3222244" DestinationUUID="4CB6ABBE40419315F880B2AEA429CC20.F5D64AAD4F69AC8AB38068B7C818BE14" />
                        <Connection Source="M_Severety" Destination="INT_TO_STRING_0.IN0" SourceUUID="9A40058A443B5EF8A89538BC0E292B1B" DestinationUUID="F84A1EC346A4F27DD4BFD194DC529FF7.4A28E63F4A1944460953AD888785193F" />
                        <Connection Source="M_Type" Destination="CONCAT_0.IN3" SourceUUID="E7303F12483CAEA7807E9AAE7298AF69" DestinationUUID="4CB6ABBE40419315F880B2AEA429CC20.9375164D43C13F577DC4BEA4A142FB8C" />
                        <Connection Source="M_AlgName" Destination="CONCAT_0.IN5" SourceUUID="1A5F1C8142485AF74693AEBA3D61C574" DestinationUUID="4CB6ABBE40419315F880B2AEA429CC20.0AF9E4824C3433E1BDD5DFAC5DC4EA77" />
                        <Connection Source="M_PrefAb" Destination="CONCAT_0.IN7" SourceUUID="63B569DE4F54176BBFCDF3AF435E2E54" DestinationUUID="4CB6ABBE40419315F880B2AEA429CC20.0744AEE44657EE7B6B3A73BD45DDB84E" />
                        <Connection Source="M_NameRu" Destination="CONCAT_0.IN9" SourceUUID="2EE28A284A09598C8C0BA19CD118DD9E" DestinationUUID="4CB6ABBE40419315F880B2AEA429CC20.FD80A0234F4978FBEA8C2FBF6AD71452" />
                        <Connection Source="CONCAT_0.OUT" Destination="OutString" SourceUUID="4CB6ABBE40419315F880B2AEA429CC20.CDAEAD5C416802F537E080AC05109DE4" DestinationUUID="87058C3B4EBCDABBB405A494078BB7BA" />
                    </DataConnections>
                </FBNetwork>
            </CompositeFBType>
            <CompositeFBType Name="TLoginEvents" ShowVarTypes="true" UUID="PUC3VYMLNH5UTFKKVQFIONPRPA">
                <InterfaceList>
                    <EventInputs>
                        <Event Name="copyName" UUID="VFQVLRVLTJOELEQDRH7HRCO22A" />
                        <Event Name="logIn" UUID="CBDGLEB7ER6ENG4PLPG3DGSJFY" />
                        <Event Name="logOut" UUID="N5B3Q47HST7UJLGSZE75NNKTPE" />
                        <Event Name="logFail" UUID="UHRHWPCKHUHEDB365ZLV7WVOZU" />
                    </EventInputs>
                    <InputVars>
                        <VarDeclaration Name="userName" Type="STRING" InitialValue="&apos;&apos;" UUID="SL6PKCCP3NZEDNTMDNVYH4QMJI" />
                        <VarDeclaration Name="source" Type="STRING" InitialValue="&apos;&apos;" UUID="V7K3DP2ELGSULPSNDILLPTQTQM" />
                    </InputVars>
                </InterfaceList>
                <FBNetwork>
                    <FB Name="CONCAT_0" Type="CONCAT" TypeUUID="7HP3AWELA2YEXGQJEJ7TED5TRU" Enabled="true" UUID="PF5XCFXBMJMEDBXSLJZGFXQKPI" X="90.906082968718" Y="631.832527938315">
                        <VarValue Variable="IN0" Value="&apos;Пользователь &apos;" Type="STRING" />
                        <VarValue Variable="IN2" Value="&apos; вышел из системы&apos;" Type="STRING" />
                        <InterfaceList>
                            <InputVars>
                                <VarDeclaration Name="IN0" Type="STRING" InitialValue="&apos;&apos;" UUID="AXI6CN37DOUUZBRC5BPPTMRVWY" />
                                <VarDeclaration Name="IN1" Type="STRING" InitialValue="&apos;&apos;" UUID="VVFNN5MKVRUU7N3IQCZRJPQYZA" />
                                <VarDeclaration Name="IN2" Type="STRING" InitialValue="&apos;&apos;" UUID="VWALHD4ILK3EHFDCAUCBI5RYTQ" />
                            </InputVars>
                            <OutputVars>
                                <VarDeclaration Name="OUT" Type="STRING" InitialValue="&apos;&apos;" UUID="LSW25TPVAJUEDLEA4A36JHIQAU" />
                            </OutputVars>
                        </InterfaceList>
                    </FB>
                    <FB Name="E_MOVE" Type="E_MOVE" TypeUUID="KOMZ2GUYLSOUTOUYV7UCD3COUA" Enabled="true" UUID="YLZNKGCGCMUUPFTRG6RG7UTUUY" X="-110.124926739692" Y="487.531903764226" />
                    <FB Name="EventRegistrator_2" Type="TEventRegistrator" TypeUUID="OXLMPZHLLMBUHA366SFNI6E7JE" Enabled="true" UUID="RVNQADHWZQEEPHHWVP53W4CEE4" X="411.967912518223" Y="508.496251451605">
                        <VarValue Variable="CATEGORY" Value="1060" Type="DINT" />
                        <VarValue Variable="STATE" Value="1" Type="INT" />
                    </FB>
                    <FB Name="EventRegistrator_1" Type="TEventRegistrator" TypeUUID="OXLMPZHLLMBUHA366SFNI6E7JE" Enabled="true" UUID="6QD6YAM2PXAEVBPUKZJ556ZFBE" X="411.967912518223" Y="282.25880082655">
                        <VarValue Variable="CATEGORY" Value="1060" Type="DINT" />
                        <VarValue Variable="STATE" Value="1" Type="INT" />
                        <VarValue Variable="TEXT" Value="&apos;Неудачная попытка входа в систему&apos;" Type="STRING" />
                    </FB>
                    <FB Name="EventRegistrator_0" Type="TEventRegistrator" TypeUUID="OXLMPZHLLMBUHA366SFNI6E7JE" Enabled="true" UUID="CNUXEYDCV2KU7HNIQSD2EQQ5KA" X="411.967912518223" Y="72.496251451605">
                        <VarValue Variable="CATEGORY" Value="1060" Type="DINT" />
                        <VarValue Variable="STATE" Value="1" Type="INT" />
                    </FB>
                    <FB Name="IS2_TAG_composit" Type="TIS2_TAG_composit" TypeUUID="RW3EJM6JXFZE5P5ODTVG4VKOZU" Enabled="true" UUID="WO2TQRWRGWLEBIFLUBVWYXUFL4" X="-157" Y="-7">
                        <VarValue Variable="M_Other" Value="&apos;Авторизация&apos;" Type="STRING" />
                        <VarValue Variable="M_Type" Value="&apos;Пользователи&apos;" Type="STRING" />
                    </FB>
                    <FB Name="CONCAT_1" Type="CONCAT" TypeUUID="7HP3AWELA2YEXGQJEJ7TED5TRU" Enabled="true" UUID="V7MBSUPOFOUU7DFEQKGNI64TP4" X="60.66988996463" Y="195.832527938315">
                        <VarValue Variable="IN0" Value="&apos;Пользователь &apos;" Type="STRING" />
                        <VarValue Variable="IN2" Value="&apos; вошел в систему&apos;" Type="STRING" />
                        <InterfaceList>
                            <InputVars>
                                <VarDeclaration Name="IN0" Type="STRING" InitialValue="&apos;&apos;" UUID="AXI6CN37DOUUZBRC5BPPTMRVWY" />
                                <VarDeclaration Name="IN1" Type="STRING" InitialValue="&apos;&apos;" UUID="VVFNN5MKVRUU7N3IQCZRJPQYZA" />
                                <VarDeclaration Name="IN2" Type="STRING" InitialValue="&apos;&apos;" UUID="VWALHD4ILK3EHFDCAUCBI5RYTQ" />
                            </InputVars>
                            <OutputVars>
                                <VarDeclaration Name="OUT" Type="STRING" InitialValue="&apos;&apos;" UUID="LSW25TPVAJUEDLEA4A36JHIQAU" />
                            </OutputVars>
                        </InterfaceList>
                    </FB>
                    <FB Name="EventRegistrator_3" Type="TEventRegistrator" TypeUUID="OXLMPZHLLMBUHA366SFNI6E7JE" Enabled="true" UUID="WFZBMFGVS6ZEPDL26DLIW5A3AA" X="664.467912518223" Y="508.496251451605">
                        <VarValue Variable="CATEGORY" Value="3" Type="DINT" />
                        <VarValue Variable="STATE" Value="1" Type="INT" />
                    </FB>
                    <FB Name="EventRegistrator_4" Type="TEventRegistrator" TypeUUID="OXLMPZHLLMBUHA366SFNI6E7JE" Enabled="true" UUID="LW3MSMH54W7E3NM46QXR746NGM" X="664.467912518223" Y="72.496251451605">
                        <VarValue Variable="CATEGORY" Value="3" Type="DINT" />
                        <VarValue Variable="STATE" Value="1" Type="INT" />
                    </FB>
                    <FB Name="EventRegistrator_5" Type="TEventRegistrator" TypeUUID="OXLMPZHLLMBUHA366SFNI6E7JE" Enabled="true" UUID="Q3SNDRV4PFZU7EFPVCYYF26BYE" X="664.467912518223" Y="282.25880082655">
                        <VarValue Variable="CATEGORY" Value="3" Type="DINT" />
                        <VarValue Variable="STATE" Value="1" Type="INT" />
                        <VarValue Variable="TEXT" Value="&apos;Неудачная попытка входа в систему&apos;" Type="STRING" />
                    </FB>
                    <EventConnections>
                        <Connection Source="copyName" Destination="E_MOVE.EI" SourceUUID="C65561A9455C9AABFE890392D0DA8978" DestinationUUID="18D5F2C247291346A2377196A674D26F.A6673E064886A40E7B09A185541AA35B" />
                        <Connection Source="logFail" Destination="EventRegistrator_1.E_REGISTER" SourceUUID="3C7BE2A1410E3D4A57EE7E87CDAEDA5F" DestinationUUID="01EC07F44AC07D9A5356F4850925FBDE.D2D48FB74E4CC596B8CF8C856673AC58" />
                        <Connection Source="logIn" Destination="EventRegistrator_0.E_REGISTER" SourceUUID="90654610467C243FCD5B8F9B2E499AB1" DestinationUUID="607269134F95AE628784A89D501D42A2.D2D48FB74E4CC596B8CF8C856673AC58" />
                        <Connection Source="logOut" Destination="EventRegistrator_2.E_REGISTER" SourceUUID="73B8436F44FF94E73FC9D2AC7953B5D6" DestinationUUID="0C005B8D4708CCF6FBABF69C274470BB.D2D48FB74E4CC596B8CF8C856673AC58" />
                        <Connection Source="logIn" Destination="EventRegistrator_4.E_REGISTER" SourceUUID="90654610467C243FCD5B8F9B2E499AB1" DestinationUUID="30C9B65D4DBEE5FD2FF49CB533CDF31F.D2D48FB74E4CC596B8CF8C856673AC58" />
                        <Connection Source="logFail" Destination="EventRegistrator_5.E_REGISTER" SourceUUID="3C7BE2A1410E3D4A57EE7E87CDAEDA5F" DestinationUUID="C6D1E4864F7379BCB1A8AF90C1C1EB82.D2D48FB74E4CC596B8CF8C856673AC58" />
                        <Connection Source="logOut" Destination="EventRegistrator_3.E_REGISTER" SourceUUID="73B8436F44FF94E73FC9D2AC7953B5D6" DestinationUUID="141672B147B297D5D6F07A8D001B748B.D2D48FB74E4CC596B8CF8C856673AC58" />
                    </EventConnections>
                    <DataConnections>
                        <Connection Source="CONCAT_1.OUT" Destination="EventRegistrator_0.TEXT" SourceUUID="5119D8AF4FA92BEE8C82A48C7F937BD4.CDAEAD5C416802F537E080AC05109DE4" DestinationUUID="607269134F95AE628784A89D501D42A2.772765ED460DFE7D24CCCBBBF6484CAF" dx1="124.798" dx2="75" dy="0.163724" />
                        <Connection Source="IS2_TAG_composit.OutString" Destination="EventRegistrator_0.TAG" SourceUUID="4638B5B3409635D16BA0ABA05F855E6C.87058C3B4EBCDABBB405A494078BB7BA" DestinationUUID="607269134F95AE628784A89D501D42A2.7D5023924D24083A40A8E08A50B6771E" dx1="292.468" dx2="75" dy="219.246" />
                        <Connection Source="E_MOVE.OUT" Destination="CONCAT_0.IN1" SourceUUID="18D5F2C247291346A2377196A674D26F.8D1A74BB45DAFDA6122CEAB37D0A0B0E" DestinationUUID="16717B79415862E1725AF2867A0ADE62.F5D64AAD4F69AC8AB38068B7C818BE14" dx1="73.531" dx2="10" dy="134.551" />
                        <Connection Source="IS2_TAG_composit.OutString" Destination="EventRegistrator_1.TAG" SourceUUID="4638B5B3409635D16BA0ABA05F855E6C.87058C3B4EBCDABBB405A494078BB7BA" DestinationUUID="01EC07F44AC07D9A5356F4850925FBDE.7D5023924D24083A40A8E08A50B6771E" dx1="292.468" dx2="75" dy="429.009" />
                        <Connection Source="CONCAT_0.OUT" Destination="EventRegistrator_2.TEXT" SourceUUID="16717B79415862E1725AF2867A0ADE62.CDAEAD5C416802F537E080AC05109DE4" DestinationUUID="0C005B8D4708CCF6FBABF69C274470BB.772765ED460DFE7D24CCCBBBF6484CAF" dx1="59.2362" dx2="110.326" dy="0.163724" />
                        <Connection Source="userName" Destination="CONCAT_1.IN1" SourceUUID="08F5FC924172DB4F6B1B6CB64A0CF283" DestinationUUID="5119D8AF4FA92BEE8C82A48C7F937BD4.F5D64AAD4F69AC8AB38068B7C818BE14" />
                        <Connection Source="userName" Destination="E_MOVE.IN0" SourceUUID="08F5FC924172DB4F6B1B6CB64A0CF283" DestinationUUID="18D5F2C247291346A2377196A674D26F.12D4A84044620AC53A4DDFB015980EA0" />
                        <Connection Source="source" Destination="EventRegistrator_0.SOURCE" SourceUUID="BFB1D5AF45A55944161A4DBE8313CEB7" DestinationUUID="607269134F95AE628784A89D501D42A2.F36EEF8C49622050FB77A58D834678C9" />
                        <Connection Source="source" Destination="EventRegistrator_1.SOURCE" SourceUUID="BFB1D5AF45A55944161A4DBE8313CEB7" DestinationUUID="01EC07F44AC07D9A5356F4850925FBDE.F36EEF8C49622050FB77A58D834678C9" />
                        <Connection Source="source" Destination="EventRegistrator_2.SOURCE" SourceUUID="BFB1D5AF45A55944161A4DBE8313CEB7" DestinationUUID="0C005B8D4708CCF6FBABF69C274470BB.F36EEF8C49622050FB77A58D834678C9" />
                        <Connection Source="IS2_TAG_composit.OutString" Destination="EventRegistrator_2.TAG" SourceUUID="4638B5B3409635D16BA0ABA05F855E6C.87058C3B4EBCDABBB405A494078BB7BA" DestinationUUID="0C005B8D4708CCF6FBABF69C274470BB.7D5023924D24083A40A8E08A50B6771E" dx1="292.468" dx2="75" dy="655.246" />
                        <Connection Source="source" Destination="EventRegistrator_5.SOURCE" SourceUUID="BFB1D5AF45A55944161A4DBE8313CEB7" DestinationUUID="C6D1E4864F7379BCB1A8AF90C1C1EB82.F36EEF8C49622050FB77A58D834678C9" />
                        <Connection Source="source" Destination="EventRegistrator_4.SOURCE" SourceUUID="BFB1D5AF45A55944161A4DBE8313CEB7" DestinationUUID="30C9B65D4DBEE5FD2FF49CB533CDF31F.F36EEF8C49622050FB77A58D834678C9" />
                        <Connection Source="source" Destination="EventRegistrator_3.SOURCE" SourceUUID="BFB1D5AF45A55944161A4DBE8313CEB7" DestinationUUID="141672B147B297D5D6F07A8D001B748B.F36EEF8C49622050FB77A58D834678C9" />
                        <Connection Source="CONCAT_1.OUT" Destination="EventRegistrator_4.TEXT" SourceUUID="5119D8AF4FA92BEE8C82A48C7F937BD4.CDAEAD5C416802F537E080AC05109DE4" DestinationUUID="30C9B65D4DBEE5FD2FF49CB533CDF31F.772765ED460DFE7D24CCCBBBF6484CAF" dx1="442.298" dx2="10" dy="0.163724" />
                        <Connection Source="CONCAT_0.OUT" Destination="EventRegistrator_3.TEXT" SourceUUID="16717B79415862E1725AF2867A0ADE62.CDAEAD5C416802F537E080AC05109DE4" DestinationUUID="141672B147B297D5D6F07A8D001B748B.772765ED460DFE7D24CCCBBBF6484CAF" dx1="412.062" dx2="10" dy="0.163724" />
                        <Connection Source="IS2_TAG_composit.OutString" Destination="EventRegistrator_3.TAG" SourceUUID="4638B5B3409635D16BA0ABA05F855E6C.87058C3B4EBCDABBB405A494078BB7BA" DestinationUUID="141672B147B297D5D6F07A8D001B748B.7D5023924D24083A40A8E08A50B6771E" dx1="609.968" dx2="10" dy="655.246" />
                        <Connection Source="IS2_TAG_composit.OutString" Destination="EventRegistrator_5.TAG" SourceUUID="4638B5B3409635D16BA0ABA05F855E6C.87058C3B4EBCDABBB405A494078BB7BA" DestinationUUID="C6D1E4864F7379BCB1A8AF90C1C1EB82.7D5023924D24083A40A8E08A50B6771E" dx1="609.968" dx2="10" dy="429.009" />
                        <Connection Source="IS2_TAG_composit.OutString" Destination="EventRegistrator_4.TAG" SourceUUID="4638B5B3409635D16BA0ABA05F855E6C.87058C3B4EBCDABBB405A494078BB7BA" DestinationUUID="30C9B65D4DBEE5FD2FF49CB533CDF31F.7D5023924D24083A40A8E08A50B6771E" dx1="609.968" dx2="10" dy="219.246" />
                    </DataConnections>
                </FBNetwork>
            </CompositeFBType>
            <GraphicsCompositeFBType Name="TNewEditor" ShowVarTypes="true" UUID="OYKZWYZHFTIUXAJILU4I2UEWGM">
                <InterfaceList>
                    <EventOutputs>
                        <Event Name="mouseLBPress" Comment="событие нажатия левой кнопки мыши на объекте" UUID="V6KZEKNMZSTEPFU4AATMKR23JQ" />
                        <Event Name="mouseLBRelease" Comment="событие отпускания левой кнопки мыши на объекте" UUID="CMAONDPWHSAEHMJS6M4XSAGDNQ" />
                        <Event Name="mouseRBPress" Comment="событие нажатия правой кнопки мыши на объекте" UUID="6WJ6SXLHALQEHCL5A7XVWG6Q2M" />
                        <Event Name="mouseRBRelease" Comment="событие отпускания правой кнопки мыши на объекте" UUID="RVY3ACQCBPUUDNBFKT37BQJZDY" />
                        <Event Name="mouseEnter" Comment="событие входа указателя мыши в пределы объекта" UUID="CVJR3KU4H2OUZIFNWASV2K7YKY" />
                        <Event Name="mouseLeave" Comment="событие выхода указателя мыши за пределы объекта" UUID="ULABXQT2CWHEVGWFBP2XXTJVCY" />
                        <Event Name="mouseLBDblClick" Comment="событие двойного щелчка левой кнопки мыши на объекте" UUID="2JR5EGZ5UMXUDM6FM6RQVHYMJA" />
                        <Event Name="edited" UUID="IJIBS2EGAEYUTJN6AS633LKLAQ" />
                    </EventOutputs>
                    <InputVars>
                        <VarDeclaration Name="pos" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" Comment="позиция объекта" Group="Общие" InitialValue="(x:=0,y:=0)" UUID="YICJMWNGDJSENDCQB25KI7V7TI" />
                        <VarDeclaration Name="angle" Type="LREAL" Comment="угол поворота объекта" Group="Общие" InitialValue="0" UUID="QAO7YAFI4UWUVECT5A6T3LCA2Y" />
                        <VarDeclaration Name="enabled" Type="BOOL" Comment="доступность объекта" Group="Общие" InitialValue="TRUE" UUID="AOL3AFL4X2NUXJHAPDGTSQVGMY" />
                        <VarDeclaration Name="moveable" Type="BOOL" Comment="подвижность объекта" Group="Общие" InitialValue="FALSE" UUID="BWAWE3KLRTPUNPRN4YTUWGLDXI" />
                        <VarDeclaration Name="visible" Type="BOOL" Comment="видимость объекта" Group="Общие" InitialValue="TRUE" UUID="R4UML2QPG4NEHGHPSN2NKE6GUI" />
                        <VarDeclaration Name="zValue" Type="LREAL" Comment="z-индекс объекта" Group="Общие" InitialValue="0" UUID="VXTOSKNU3FNUPMCAN6PKO5EDGI" />
                        <VarDeclaration Name="hint" Type="STRING" Comment="всплывающая подсказка" Group="Общие" InitialValue="&apos;&apos;" UUID="CLZADEBSNHDEJMFXQH53VBNQEE" />
                        <VarDeclaration Name="size" Type="TSize" TypeUUID="XDTT5M52XMSURN23S57SF26UGU" Comment="размер прямоугольника" Group="Общие" InitialValue="(width:=418,height:=24)" UUID="HC2FKFJ4NBUU3J5U7QZTECI2TM" />
                        <VarDeclaration Name="name" Type="STRING" InitialValue="&apos;&apos;" UUID="FNEOZECXEJHEDKHKAZWMWZDOWM" />
                        <VarDeclaration Name="i_value" Type="REAL" InitialValue="0" UUID="IWW4RMZ6BR7UREXTGK4II5F3PQ" />
                    </InputVars>
                    <OutputVars>
                        <VarDeclaration Name="o_value" Type="REAL" InitialValue="0" UUID="VYDPIKCJPGIU5I5EJCFGYNLPNI" />
                    </OutputVars>
                </InterfaceList>
                <FBNetwork>
                    <FB Name="RealEditor" Type="TRealEditor" TypeUUID="CHPABVNXB4IELDHRTINGQHKUYY" Enabled="true" UUID="XZCY2XHUAGKUDMMKWM5WS3VJIE" X="76" Y="-3">
                        <VarValue Variable="decimals" Value="0" Type="INT" />
                        <VarValue Variable="pos" Value="(x:=204,y:=-1)" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" />
                        <VarValue Variable="size" Value="(width:=216,height:=24)" Type="TSize" TypeUUID="XDTT5M52XMSURN23S57SF26UGU" />
                        <VarValue Variable="zValue" Value="1000001" Type="LREAL" />
                    </FB>
                    <FB Name="SimpleText" Type="TSimpleText" TypeUUID="OBURUFGSRT7UVLSMGMSUGBKM5E" Enabled="true" UUID="XUSCSNYGO5LEJHSNXZCNSUIJXM" X="51.5" Y="508">
                        <VarValue Variable="alignment" Value="8" Type="TAlignment" TypeUUID="IUA2FTZVSF6EVJPPY3ZKXNHV6E" />
                        <VarValue Variable="pos" Value="(x:=-1,y:=0)" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" />
                        <VarValue Variable="size" Value="(width:=202,height:=23)" Type="TSize" TypeUUID="XDTT5M52XMSURN23S57SF26UGU" />
                        <VarValue Variable="zValue" Value="1000001" Type="LREAL" />
                    </FB>
                    <FB Name="Rect" Type="TRect" TypeUUID="24POL55EVH5U5GD3E4VMTU2OW4" Enabled="true" UUID="VIC2SUAATJMUPDSBXFM35TXSD4" X="507" Y="490">
                        <VarValue Variable="pos" Value="(x:=-3.84654601027512,y:=-1.32257077823688)" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" />
                        <VarValue Variable="size" Value="(width:=422.69309202055,height:=23.6451415564738)" Type="TSize" TypeUUID="XDTT5M52XMSURN23S57SF26UGU" />
                    </FB>
                    <FB Name="IS2_RegEventChangeValue" Type="TIS2_RegEventChangeValue" TypeUUID="JML3DHIB6ZTUFIRU6V64OGBK6I" Enabled="true" UUID="BG6MFE5WTSPETGBJRJLIZWY76M" X="950.25" Y="109.875">
                        <VarValue Variable="M_Type" Value="&apos;Изм.зн.&apos;" Type="STRING" />
                        <VarValue Variable="Message" Value="&apos;Изменено значение параметра: &apos;" Type="STRING" />
                        <VarValue Variable="Other" Value="&apos;IS&apos;" Type="STRING" />
                    </FB>
                    <FB Name="FORMAT_REAL_0" Type="FORMAT_REAL" TypeUUID="7Y3KASBDDFREPCP2FVUNPMN4RY" Enabled="true" UUID="OVI5IL7JENWU7JK7SI7WG6MHEM" X="692.07480328396" Y="349.51486383157">
                        <VarValue Variable="PRECISION" Value="1" Type="INT" />
                    </FB>
                    <FB Name="E_MOVE" Type="E_MOVE" TypeUUID="KOMZ2GUYLSOUTOUYV7UCD3COUA" Enabled="true" UUID="WT4JZHNMRFYUNFBPJH7U6I4DNM" X="472.5" Y="388.61333745482" />
                    <FB Name="FORMAT_REAL_1" Type="FORMAT_REAL" TypeUUID="7Y3KASBDDFREPCP2FVUNPMN4RY" Enabled="true" UUID="YYELD3SSGWTU7K3IPC6ILECGOY" X="483.85623340617" Y="159">
                        <VarValue Variable="PRECISION" Value="1" Type="INT" />
                    </FB>
                    <EventConnections>
                        <Connection Source="RealEditor.edited" Destination="edited" SourceUUID="5C8D45BE419501F43BB38AB141A96E69.44BC864C4E42D8E8C46AA2A02E06567B" DestinationUUID="6819504249310186BD04BEA5044BADBD" />
                        <Connection Source="RealEditor.edited" Destination="IS2_RegEventChangeValue.Registrer" SourceUUID="5C8D45BE419501F43BB38AB141A96E69.44BC864C4E42D8E8C46AA2A02E06567B" DestinationUUID="93C2BC09499E9CB6568A2998F31FDB8C.F4863EC2452A178A4460539D5B716C64" dx1="118.75" dx2="565" dy="-0.875" />
                        <Connection Source="RealEditor.edited" Destination="E_MOVE.EI" SourceUUID="5C8D45BE419501F43BB38AB141A96E69.44BC864C4E42D8E8C46AA2A02E06567B" DestinationUUID="9D9CF8B4467189ACFF492F946B83234F.A6673E064886A40E7B09A185541AA35B" dx1="10" dx2="196" dy="277.863" />
                    </EventConnections>
                    <DataConnections>
                        <Connection Source="i_value" Destination="RealEditor.i_value" SourceUUID="B3C8AD45487F0C3EB832F3927CBB7484" DestinationUUID="5C8D45BE419501F43BB38AB141A96E69.22DFAB1C4EB5FAF1DA769BAE59EDE774" />
                        <Connection Source="RealEditor.o_value" Destination="o_value" SourceUUID="5C8D45BE419501F43BB38AB141A96E69.515F10D1477E364CF89A05B0DA05AD98" DestinationUUID="28F406AE4E9179498A48A4A36A6F356C" />
                        <Connection Source="name" Destination="SimpleText.text" SourceUUID="90EC482B414E22576C06EAA8B36E64CB" DestinationUUID="372924BD4456770644BE4D9EBB0951D9.6197985F4F26DAD792BB4698C1EFE1AA" />
                        <Connection Source="name" Destination="IS2_RegEventChangeValue.NameParam" SourceUUID="90EC482B414E22576C06EAA8B36E64CB" DestinationUUID="93C2BC09499E9CB6568A2998F31FDB8C.558FCA5041B9D7D85B486AB3476924F2" />
                        <Connection Source="E_MOVE.OUT" Destination="FORMAT_REAL_0.IN0" SourceUUID="9D9CF8B4467189ACFF492F946B83234F.8D1A74BB45DAFDA6122CEAB37D0A0B0E" DestinationUUID="2FD451754F6D23E93F925FA523877963.7F0C7CDC4C8CADC721C9D89304D41BFB" dx1="21" dx2="81.0748" dy="-0.0984736" />
                        <Connection Source="i_value" Destination="E_MOVE.IN0" SourceUUID="B3C8AD45487F0C3EB832F3927CBB7484" DestinationUUID="9D9CF8B4467189ACFF492F946B83234F.12D4A84044620AC53A4DDFB015980EA0" />
                        <Connection Source="FORMAT_REAL_0.OUT" Destination="IS2_RegEventChangeValue.pr_Value" SourceUUID="2FD451754F6D23E93F925FA523877963.E83536CE4B677B433161FFA69AF67216" DestinationUUID="93C2BC09499E9CB6568A2998F31FDB8C.AB167AEB4059AA80DFBB34AFD34D0485" dx1="21" dx2="67.6752" dy="-148.64" />
                        <Connection Source="FORMAT_REAL_1.OUT" Destination="IS2_RegEventChangeValue.new_Value" SourceUUID="EEB108C64FA73552BC7868AB76469085.E83536CE4B677B433161FFA69AF67216" DestinationUUID="93C2BC09499E9CB6568A2998F31FDB8C.48C86D4343F839D3518D84BC9CADD816" dx1="21" dx2="275.894" dy="58.125" />
                        <Connection Source="RealEditor.o_value" Destination="FORMAT_REAL_1.IN0" SourceUUID="5C8D45BE419501F43BB38AB141A96E69.515F10D1477E364CF89A05B0DA05AD98" DestinationUUID="EEB108C64FA73552BC7868AB76469085.7F0C7CDC4C8CADC721C9D89304D41BFB" dx1="80.3562" dx2="137" dy="87.25" />
                        <Connection Source="enabled" Destination="RealEditor.enabled" SourceUUID="15B097034B9BBE7CCD78E0A466A64239" DestinationUUID="5C8D45BE419501F43BB38AB141A96E69.15B097034B9BBE7CCD78E0A466A64239" />
                    </DataConnections>
                </FBNetwork>
            </GraphicsCompositeFBType>
            <GraphicsCompositeFBType Name="TNewString" ShowVarTypes="true" UUID="E5KCKMMFJL5ULIXLKXSUHJALFU">
                <InterfaceList>
                    <EventOutputs>
                        <Event Name="mouseLBPress" Comment="событие нажатия левой кнопки мыши на объекте" UUID="V6KZEKNMZSTEPFU4AATMKR23JQ" />
                        <Event Name="mouseLBRelease" Comment="событие отпускания левой кнопки мыши на объекте" UUID="CMAONDPWHSAEHMJS6M4XSAGDNQ" />
                        <Event Name="mouseRBPress" Comment="событие нажатия правой кнопки мыши на объекте" UUID="6WJ6SXLHALQEHCL5A7XVWG6Q2M" />
                        <Event Name="mouseRBRelease" Comment="событие отпускания правой кнопки мыши на объекте" UUID="RVY3ACQCBPUUDNBFKT37BQJZDY" />
                        <Event Name="mouseEnter" Comment="событие входа указателя мыши в пределы объекта" UUID="CVJR3KU4H2OUZIFNWASV2K7YKY" />
                        <Event Name="mouseLeave" Comment="событие выхода указателя мыши за пределы объекта" UUID="ULABXQT2CWHEVGWFBP2XXTJVCY" />
                        <Event Name="mouseLBDblClick" Comment="событие двойного щелчка левой кнопки мыши на объекте" UUID="2JR5EGZ5UMXUDM6FM6RQVHYMJA" />
                        <Event Name="edited" UUID="D3LXDRUHHIAEZDAESQBLDQAFEE" />
                    </EventOutputs>
                    <InputVars>
                        <VarDeclaration Name="pos" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" Comment="позиция объекта" Group="Общие" InitialValue="(x:=0,y:=0)" UUID="YICJMWNGDJSENDCQB25KI7V7TI" />
                        <VarDeclaration Name="angle" Type="LREAL" Comment="угол поворота объекта" Group="Общие" InitialValue="0" UUID="QAO7YAFI4UWUVECT5A6T3LCA2Y" />
                        <VarDeclaration Name="enabled" Type="BOOL" Comment="доступность объекта" Group="Общие" InitialValue="TRUE" UUID="AOL3AFL4X2NUXJHAPDGTSQVGMY" />
                        <VarDeclaration Name="moveable" Type="BOOL" Comment="подвижность объекта" Group="Общие" InitialValue="FALSE" UUID="BWAWE3KLRTPUNPRN4YTUWGLDXI" />
                        <VarDeclaration Name="visible" Type="BOOL" Comment="видимость объекта" Group="Общие" InitialValue="TRUE" UUID="R4UML2QPG4NEHGHPSN2NKE6GUI" />
                        <VarDeclaration Name="zValue" Type="LREAL" Comment="z-индекс объекта" Group="Общие" InitialValue="0" UUID="VXTOSKNU3FNUPMCAN6PKO5EDGI" />
                        <VarDeclaration Name="hint" Type="STRING" Comment="всплывающая подсказка" Group="Общие" InitialValue="&apos;&apos;" UUID="CLZADEBSNHDEJMFXQH53VBNQEE" />
                        <VarDeclaration Name="size" Type="TSize" TypeUUID="XDTT5M52XMSURN23S57SF26UGU" Comment="размер прямоугольника" Group="Общие" InitialValue="(width:=418,height:=24)" UUID="HC2FKFJ4NBUU3J5U7QZTECI2TM" />
                        <VarDeclaration Name="name" Type="STRING" InitialValue="&apos;&apos;" UUID="FNEOZECXEJHEDKHKAZWMWZDOWM" />
                        <VarDeclaration Name="i_value" Type="STRING" InitialValue="&apos;&apos;" UUID="IWW4RMZ6BR7UREXTGK4II5F3PQ" />
                    </InputVars>
                    <OutputVars>
                        <VarDeclaration Name="o_value" Type="STRING" InitialValue="&apos;&apos;" UUID="VYDPIKCJPGIU5I5EJCFGYNLPNI" />
                    </OutputVars>
                </InterfaceList>
                <FBNetwork>
                    <FB Name="SimpleText" Type="TSimpleText" TypeUUID="OBURUFGSRT7UVLSMGMSUGBKM5E" Enabled="true" UUID="5MUUQWLC4L4ULO7OP3YC5SSXKQ" X="316.5" Y="50">
                        <VarValue Variable="alignment" Value="8" Type="TAlignment" TypeUUID="IUA2FTZVSF6EVJPPY3ZKXNHV6E" />
                        <VarValue Variable="pos" Value="(x:=-1,y:=0)" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" />
                        <VarValue Variable="size" Value="(width:=202,height:=23)" Type="TSize" TypeUUID="XDTT5M52XMSURN23S57SF26UGU" />
                        <VarValue Variable="zValue" Value="1000001" Type="LREAL" />
                    </FB>
                    <FB Name="Rect" Type="TRect" TypeUUID="24POL55EVH5U5GD3E4VMTU2OW4" Enabled="true" UUID="QFXCQ7MONZXEXCX5RLV5HT5EBM" X="751" Y="85">
                        <VarValue Variable="pos" Value="(x:=-3.84654601027512,y:=-1.32257077823688)" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" />
                        <VarValue Variable="size" Value="(width:=422.69309202055,height:=23.6451415564738)" Type="TSize" TypeUUID="XDTT5M52XMSURN23S57SF26UGU" />
                    </FB>
                    <FB Name="STRINGEditor" Type="TSTRINGEditor" TypeUUID="YOEO7FJP6CHEPFEGMCTNCFO4EE" Enabled="true" UUID="U3R6NRQAWJUU5KHKV65PZSK6YE" X="-18.5" Y="301">
                        <VarValue Variable="pos" Value="(x:=204,y:=-1)" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" />
                        <VarValue Variable="size" Value="(width:=216,height:=24)" Type="TSize" TypeUUID="XDTT5M52XMSURN23S57SF26UGU" />
                    </FB>
                    <FB Name="IS2_RegEventChangeValue" Type="TIS2_RegEventChangeValue" TypeUUID="JML3DHIB6ZTUFIRU6V64OGBK6I" Enabled="true" UUID="G6F7A6DO7M7URCFX5BCNQYTCDE" X="832.75" Y="542">
                        <VarValue Variable="M_Type" Value="&apos;Изм.зн.&apos;" Type="STRING" />
                        <VarValue Variable="Message" Value="&apos;Изменено значение параметра: &apos;" Type="STRING" />
                        <VarValue Variable="Other" Value="&apos;IS&apos;" Type="STRING" />
                    </FB>
                    <FB Name="E_MOVE" Type="E_MOVE" TypeUUID="KOMZ2GUYLSOUTOUYV7UCD3COUA" Enabled="true" UUID="VXMSB6ZV5GYETNUMDPKKDRWWJU" X="362" Y="606.73833745482" />
                    <EventConnections>
                        <Connection Source="STRINGEditor.edited" Destination="edited" SourceUUID="C6E6E3A64E69B200BAAFEAA8C15EC9FC.9C986A3D4B4E76486ABEDA82C3623E6D" DestinationUUID="C671D71E4C003A870294048C2105C0B1" />
                        <Connection Source="STRINGEditor.edited" Destination="IS2_RegEventChangeValue.Registrer" SourceUUID="C6E6E3A64E69B200BAAFEAA8C15EC9FC.9C986A3D4B4E76486ABEDA82C3623E6D" DestinationUUID="78F08B37483FFB6E44E8B788196262D8.F4863EC2452A178A4460539D5B716C64" dx1="653.75" dx2="10" dy="127.25" />
                        <Connection Source="STRINGEditor.edited" Destination="E_MOVE.EI" SourceUUID="C6E6E3A64E69B200BAAFEAA8C15EC9FC.9C986A3D4B4E76486ABEDA82C3623E6D" DestinationUUID="FB20D9AD49B0E935D41B8CB64DD6C6A1.A6673E064886A40E7B09A185541AA35B" dx1="161" dx2="32" dy="191.988" />
                    </EventConnections>
                    <DataConnections>
                        <Connection Source="name" Destination="SimpleText.text" SourceUUID="90EC482B414E22576C06EAA8B36E64CB" DestinationUUID="594829EB45F9E262F07EEEBB5457CA2E.6197985F4F26DAD792BB4698C1EFE1AA" />
                        <Connection Source="i_value" Destination="STRINGEditor.i_value" SourceUUID="B3C8AD45487F0C3EB832F3927CBB7484" DestinationUUID="C6E6E3A64E69B200BAAFEAA8C15EC9FC.5217CEEF4233A34B9BB779B04926B3C8" />
                        <Connection Source="STRINGEditor.o_value" Destination="o_value" SourceUUID="C6E6E3A64E69B200BAAFEAA8C15EC9FC.C1A591934EA531FCA72F84B680532A23" DestinationUUID="28F406AE4E9179498A48A4A36A6F356C" />
                        <Connection Source="name" Destination="IS2_RegEventChangeValue.NameParam" SourceUUID="90EC482B414E22576C06EAA8B36E64CB" DestinationUUID="78F08B37483FFB6E44E8B788196262D8.558FCA5041B9D7D85B486AB3476924F2" />
                        <Connection Source="i_value" Destination="E_MOVE.IN0" SourceUUID="B3C8AD45487F0C3EB832F3927CBB7484" DestinationUUID="FB20D9AD49B0E935D41B8CB64DD6C6A1.12D4A84044620AC53A4DDFB015980EA0" />
                        <Connection Source="E_MOVE.OUT" Destination="IS2_RegEventChangeValue.pr_Value" SourceUUID="FB20D9AD49B0E935D41B8CB64DD6C6A1.8D1A74BB45DAFDA6122CEAB37D0A0B0E" DestinationUUID="78F08B37483FFB6E44E8B788196262D8.AB167AEB4059AA80DFBB34AFD34D0485" dx1="84.0748" dx2="269.175" dy="0.261663" />
                        <Connection Source="STRINGEditor.o_value" Destination="IS2_RegEventChangeValue.new_Value" SourceUUID="C6E6E3A64E69B200BAAFEAA8C15EC9FC.C1A591934EA531FCA72F84B680532A23" DestinationUUID="78F08B37483FFB6E44E8B788196262D8.48C86D4343F839D3518D84BC9CADD816" dx1="498.75" dx2="165" dy="208.5" />
                        <Connection Source="enabled" Destination="STRINGEditor.enabled" SourceUUID="15B097034B9BBE7CCD78E0A466A64239" DestinationUUID="C6E6E3A64E69B200BAAFEAA8C15EC9FC.15B097034B9BBE7CCD78E0A466A64239" />
                    </DataConnections>
                </FBNetwork>
            </GraphicsCompositeFBType>
            <GraphicsCompositeFBType Name="T_Button_Simple" ShowVarTypes="true" UUID="F2YXTL3R7DCUDAA4ZOGSNBO2PE">
                <InterfaceList>
                    <EventOutputs>
                        <Event Name="mouseLBPress" Comment="событие нажатия левой кнопки мыши на объекте" UUID="V6KZEKNMZSTEPFU4AATMKR23JQ" />
                        <Event Name="mouseLBRelease" Comment="событие отпускания левой кнопки мыши на объекте" UUID="CMAONDPWHSAEHMJS6M4XSAGDNQ" />
                        <Event Name="mouseRBPress" Comment="событие нажатия правой кнопки мыши на объекте" UUID="6WJ6SXLHALQEHCL5A7XVWG6Q2M" />
                        <Event Name="mouseRBRelease" Comment="событие отпускания правой кнопки мыши на объекте" UUID="RVY3ACQCBPUUDNBFKT37BQJZDY" />
                        <Event Name="mouseEnter" Comment="событие входа указателя мыши в пределы объекта" UUID="CVJR3KU4H2OUZIFNWASV2K7YKY" />
                        <Event Name="mouseLeave" Comment="событие выхода указателя мыши за пределы объекта" UUID="ULABXQT2CWHEVGWFBP2XXTJVCY" />
                        <Event Name="mouseLBDblClick" Comment="событие двойного щелчка левой кнопки мыши на объекте" UUID="2JR5EGZ5UMXUDM6FM6RQVHYMJA" />
                        <Event Name="pressed" UUID="NENER6DP3ZYULMY7SSJZEJI2IA" />
                        <Event Name="released" UUID="KIFJAHCV3GXUNP7EUN7CJBQ3FE" />
                        <Event Name="clicked" UUID="6GQ25X6PWQGULN2ILB4XMBFVZE" />
                    </EventOutputs>
                    <InputVars>
                        <VarDeclaration Name="pos" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" Comment="позиция объекта" InitialValue="(x:=0,y:=0)" UUID="YICJMWNGDJSENDCQB25KI7V7TI" />
                        <VarDeclaration Name="angle" Type="LREAL" Comment="угол поворота объекта" InitialValue="0" UUID="QAO7YAFI4UWUVECT5A6T3LCA2Y" />
                        <VarDeclaration Name="enabled" Type="BOOL" Comment="доступность объекта" InitialValue="TRUE" UUID="AOL3AFL4X2NUXJHAPDGTSQVGMY" />
                        <VarDeclaration Name="moveable" Type="BOOL" Comment="подвижность объекта" InitialValue="FALSE" UUID="BWAWE3KLRTPUNPRN4YTUWGLDXI" />
                        <VarDeclaration Name="visible" Type="BOOL" Comment="видимость объекта" InitialValue="TRUE" UUID="R4UML2QPG4NEHGHPSN2NKE6GUI" />
                        <VarDeclaration Name="zValue" Type="LREAL" Comment="z-индекс объекта" InitialValue="0" UUID="VXTOSKNU3FNUPMCAN6PKO5EDGI" />
                        <VarDeclaration Name="hint" Type="STRING" Comment="всплывающая подсказка" InitialValue="&apos;&apos;" UUID="CLZADEBSNHDEJMFXQH53VBNQEE" />
                        <VarDeclaration Name="size" Type="TSize" TypeUUID="XDTT5M52XMSURN23S57SF26UGU" Comment="размер прямоугольника" InitialValue="(width:=50,height:=50)" UUID="HC2FKFJ4NBUU3J5U7QZTECI2TM" />
                        <VarDeclaration Name="Text" Type="STRING" InitialValue="&apos;&apos;" UUID="RAP6YUMSTXKUBFYIHFUGMQB7MU" />
                        <VarDeclaration Name="isOn" Type="BOOL" Comment="Подсветка кнопки" InitialValue="FALSE" UUID="WHYMWCDXMX7UJOBGWXSPJE25A4" />
                        <VarDeclaration Name="Coment" Type="STRING" InitialValue="&apos;&apos;" UUID="GVGDW7IXPVQUXBXREJQYWZDERU" />
                    </InputVars>
                </InterfaceList>
                <FBNetwork>
                    <FB Name="TLButton0" Type="TTLButton" TypeUUID="GCLFMT6OHZVEFEJCWS6KYXUKVM" Enabled="true" UUID="M2PW4BFPGNCEJAFHFA6VPY7GFU" X="206.25" Y="259.306837418178">
                        <VarValue Variable="corner" Value="2" Type="REAL" />
                        <VarValue Variable="font" Value="(family:=&apos;Tahoma&apos;,size:=12,bold:=FALSE,italic:=FALSE,underline:=FALSE,strikeout:=FALSE)" Type="TFont" TypeUUID="YVT73EACFULUPIWKAFYTDAC3S4" />
                        <VarValue Variable="text_color" Value="4278190080" Type="TColor" TypeUUID="EDYJMIBCJR5UJOZWGS3UVJENZA" />
                        <VarValue Variable="zValue" Value="0" Type="LREAL" />
                    </FB>
                    <FB Name="SEL1" Type="SEL" TypeUUID="VTYYYXK24ZYEFIHECN6CYXIJ5M" Enabled="true" UUID="62H6R24CIABEVKZEVAIQYWK65E" X="-254.971314507894" Y="462.834878978121">
                        <VarValue Variable="IN0" Value="4288321951" Type="TColor" TypeUUID="EDYJMIBCJR5UJOZWGS3UVJENZA" />
                        <VarValue Variable="IN1" Value="4278228480" Type="TColor" TypeUUID="EDYJMIBCJR5UJOZWGS3UVJENZA" />
                    </FB>
                    <FB Name="Rect_0" Type="TRect" TypeUUID="24POL55EVH5U5GD3E4VMTU2OW4" Enabled="true" UUID="3FNAZ7DEXG6UTGREGF7ZVASICI" X="582.528685492106" Y="243.834878978121">
                        <VarValue Variable="frame_color" Value="4283050759" Type="TColor" TypeUUID="EDYJMIBCJR5UJOZWGS3UVJENZA" />
                        <VarValue Variable="zValue" Value="-1" Type="LREAL" />
                    </FB>
                    <FB Name="IS_RegEvent5Cat" Type="TIS_RegEvent3Cat" TypeUUID="ZLJGKUXENPYEVM6AQX5RGFE4HQ" Enabled="true" UUID="PUQSF5YP2SJURB3HFTKSBVZIWA" X="535.75" Y="746.125">
                        <VarValue Variable="M_Type" Value="&apos;Кнопка&apos;" Type="STRING" />
                        <VarValue Variable="PrefAb" Value="&apos;none&apos;" Type="STRING" />
                    </FB>
                    <FB Name="Comment" Type="CONCAT" TypeUUID="7HP3AWELA2YEXGQJEJ7TED5TRU" Enabled="true" UUID="Y7SDQX2FTF3UXMMFM5VEBDVHXM" X="195.25" Y="869.75">
                        <VarValue Variable="IN1" Value="&apos;. Нажата кнопка &apos;" Type="STRING" />
                        <InterfaceList>
                            <InputVars>
                                <VarDeclaration Name="IN0" Type="STRING" InitialValue="&apos;&apos;" UUID="AXI6CN37DOUUZBRC5BPPTMRVWY" />
                                <VarDeclaration Name="IN1" Type="STRING" InitialValue="&apos;&apos;" UUID="VVFNN5MKVRUU7N3IQCZRJPQYZA" />
                            </InputVars>
                            <OutputVars>
                                <VarDeclaration Name="OUT" Type="STRING" InitialValue="&apos;&apos;" UUID="LSW25TPVAJUEDLEA4A36JHIQAU" />
                            </OutputVars>
                        </InterfaceList>
                    </FB>
                    <EventConnections>
                        <Connection Source="TLButton0.clicked" Destination="clicked" SourceUUID="046E9F66444433AF3D28A7802DE6E357.A24F9CF5410E51D044BD3D8F84270DD4" DestinationUUID="DFAEA1F1450DB4CF795848B7C9B50476" />
                        <Connection Source="TLButton0.pressed" Destination="pressed" SourceUUID="046E9F66444433AF3D28A7802DE6E357.8009D6224C2F388DDFFFF5AA7C8FED14" DestinationUUID="F8481A694571DE6F93941FB3401A2592" />
                        <Connection Source="TLButton0.released" Destination="released" SourceUUID="046E9F66444433AF3D28A7802DE6E357.66A71E404776B337D5781191EAC566A5" DestinationUUID="1C900A5246AFD9557EA3E4BF291B8624" />
                        <Connection Source="TLButton0.released" Destination="IS_RegEvent5Cat.Registrer" SourceUUID="046E9F66444433AF3D28A7802DE6E357.66A71E404776B337D5781191EAC566A5" DestinationUUID="F722217D4893D40FD52C6787B028D720.F4863EC2452A178A4460539D5B716C64" dx1="106" dx2="10" dy="454.318" />
                    </EventConnections>
                    <DataConnections>
                        <Connection Source="enabled" Destination="TLButton0.enabled" SourceUUID="15B097034B9BBE7CCD78E0A466A64239" DestinationUUID="046E9F66444433AF3D28A7802DE6E357.15B097034B9BBE7CCD78E0A466A64239" />
                        <Connection Source="visible" Destination="TLButton0.visible" SourceUUID="EAC5288F431A370F7493EF98A2C613D5" DestinationUUID="046E9F66444433AF3D28A7802DE6E357.EAC5288F431A370F7493EF98A2C613D5" />
                        <Connection Source="size" Destination="TLButton0.size" SourceUUID="1555B4384D69683C33FCB4A79B1A0932" DestinationUUID="046E9F66444433AF3D28A7802DE6E357.1555B4384D69683C33FCB4A79B1A0932" />
                        <Connection Source="Text" Destination="TLButton0.text" SourceUUID="51EC1F8840D59D9268390897653F4066" DestinationUUID="046E9F66444433AF3D28A7802DE6E357.1DD7F61A4F7C5156E6E9B18CF45D2641" />
                        <Connection Source="isOn" Destination="SEL1.G" SourceUUID="08CBF0B144FF6577E4B526B8075D93F4" DestinationUUID="EBE88FF64A02408211A824ABE95E590C.E51CF88C46776F33BF0D21B3F4741605" />
                        <Connection Source="size" Destination="Rect_0.size" SourceUUID="1555B4384D69683C33FCB4A79B1A0932" DestinationUUID="FC0C5AD949BDB9647F31249A1248829A.1555B4384D69683C33FCB4A79B1A0932" />
                        <Connection Source="SEL1.OUT" Destination="TLButton0.color" SourceUUID="EBE88FF64A02408211A824ABE95E590C.D94D29B049B6DB4E0A29EA9CB5266805" DestinationUUID="046E9F66444433AF3D28A7802DE6E357.FC86BB724660D6AD0CA251B07BFAB891" dx1="205" dx2="138.721" dy="1.22196" />
                        <Connection Source="SEL1.OUT" Destination="TLButton0.highlightColor" SourceUUID="EBE88FF64A02408211A824ABE95E590C.D94D29B049B6DB4E0A29EA9CB5266805" DestinationUUID="046E9F66444433AF3D28A7802DE6E357.06A0E19C44EF63B0E3EC17B6C002736C" dx1="320.721" dx2="23" dy="17.472" />
                        <Connection Source="Comment.OUT" Destination="IS_RegEvent5Cat.Message" SourceUUID="5F38E4C74B7799456A6785B1BBA78E40.CDAEAD5C416802F537E080AC05109DE4" DestinationUUID="F722217D4893D40FD52C6787B028D720.62B3B571445C4E1A4E52F1A338899A3F" dx1="10" dx2="250" dy="-0.125" />
                        <Connection Source="Coment" Destination="Comment.IN0" SourceUUID="7D3B4C354B617D176122F1868D64648B" DestinationUUID="5F38E4C74B7799456A6785B1BBA78E40.37E1D1054CA91B7F5EE82286B635B2F9" />
                        <Connection Source="Text" Destination="IS_RegEvent5Cat.Name" SourceUUID="51EC1F8840D59D9268390897653F4066" DestinationUUID="F722217D4893D40FD52C6787B028D720.558FCA5041B9D7D85B486AB3476924F2" />
                    </DataConnections>
                </FBNetwork>
            </GraphicsCompositeFBType>
            <SubWindowFBType Name="T_ChangeUser" ShowVarTypes="true" UUID="NEUKQC7QEKVEZGX4745NW4CR44">
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
                        <Event Name="Close" UUID="Q4OQANJO23METISJYRVUS5L3MM" />
                    </EventOutputs>
                    <InputVars>
                        <VarDeclaration Name="pos" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" Comment="позиция объекта" Group="Общие" InitialValue="(x:=0,y:=0)" UUID="YICJMWNGDJSENDCQB25KI7V7TI" />
                        <VarDeclaration Name="angle" Type="LREAL" Comment="угол поворота объекта" Group="Общие" InitialValue="0" UUID="QAO7YAFI4UWUVECT5A6T3LCA2Y" />
                        <VarDeclaration Name="enabled" Type="BOOL" Comment="доступность объекта" Group="Общие" InitialValue="TRUE" UUID="AOL3AFL4X2NUXJHAPDGTSQVGMY" />
                        <VarDeclaration Name="moveable" Type="BOOL" Comment="подвижность объекта" Group="Общие" InitialValue="FALSE" UUID="BWAWE3KLRTPUNPRN4YTUWGLDXI" />
                        <VarDeclaration Name="visible" Type="BOOL" Comment="видимость объекта" Group="Общие" InitialValue="FALSE" UUID="R4UML2QPG4NEHGHPSN2NKE6GUI" />
                        <VarDeclaration Name="zValue" Type="LREAL" Comment="z-индекс объекта" Group="Общие" InitialValue="0" UUID="VXTOSKNU3FNUPMCAN6PKO5EDGI" />
                        <VarDeclaration Name="hint" Type="STRING" Comment="всплывающая подсказка" Group="Общие" InitialValue="&apos;&apos;" UUID="CLZADEBSNHDEJMFXQH53VBNQEE" />
                        <VarDeclaration Name="size" Type="TSize" TypeUUID="XDTT5M52XMSURN23S57SF26UGU" Comment="размер прямоугольника" Group="Общие" InitialValue="(width:=300,height:=100)" UUID="HC2FKFJ4NBUU3J5U7QZTECI2TM" />
                        <VarDeclaration Name="frame_color" Type="TColor" TypeUUID="EDYJMIBCJR5UJOZWGS3UVJENZA" InitialValue="4293980400" UUID="GS2XRATVXFKEDNVR4AYF2FOHB4" />
                        <VarDeclaration Name="bg_color" Type="TColor" TypeUUID="EDYJMIBCJR5UJOZWGS3UVJENZA" InitialValue="4290822336" UUID="IZCT7UFDEEXEXA45WVKQH4CXO4" />
                        <VarDeclaration Name="caption" Type="STRING" InitialValue="&apos;Авторизация&apos;" UUID="4SEHRDHYXADETHGWSFVJCJBXGI" />
                        <VarDeclaration Name="caption_font" Type="TFont" TypeUUID="YVT73EACFULUPIWKAFYTDAC3S4" InitialValue="(family:=&apos;PT Sans&apos;,size:=12,bold:=FALSE,italic:=FALSE,underline:=FALSE,strikeout:=FALSE)" UUID="QSRIHPHZL46UPJPPH4M4OB7PS4" />
                        <VarDeclaration Name="closable" Type="BOOL" InitialValue="FALSE" UUID="MHEPWGX4TXFUPIWFJHGMKSAXPA" />
                        <VarDeclaration Name="Node" Type="STRING" InitialValue="&apos;&apos;" UUID="WLFWMEHSZMJUNI5FMIDD2ZBVMQ" />
                    </InputVars>
                    <OutputVars>
                        <VarDeclaration Name="knText" Type="STRING" InitialValue="&apos;&apos;" UUID="ZRC2LEN6MV2U3M6GKROVXB3PQY" />
                    </OutputVars>
                </InterfaceList>
                <FBNetwork>
                    <FB Name="E_MERGE_0" Type="E_MERGE" TypeUUID="JXEGZ46GJOGE7GKSENPHVM3FKE" Enabled="true" UUID="PMPVE4TBYJBE5MFL3GE2DFKN7I" X="273.75" Y="309.25">
                        <InterfaceList>
                            <EventInputs>
                                <Event Name="EI0" Comment="первое событие" UUID="LOGSQQQJRXSUHPA5HPTLEJUCNM" />
                                <Event Name="EI1" Comment="второе событие" UUID="USBMKUE64M7UDKX5KQ5VDXNU5M" />
                            </EventInputs>
                            <EventOutputs>
                                <Event Name="EO" Comment="результирующее событие, возникает при возникновении любого из входных" UUID="ZDYG622BT46ENJSJX7SNGHZVP4" />
                            </EventOutputs>
                        </InterfaceList>
                    </FB>
                    <FB Name="USER_1" Type="USER" TypeUUID="A7XEUSN5LWDEPBBUZIYW5YREEE" Enabled="true" UUID="SBD2WMBLQBUEHJ63WBL3NNOPTE" X="581.25" Y="109.625" />
                    <FB Name="E_MERGE" Type="E_MERGE" TypeUUID="JXEGZ46GJOGE7GKSENPHVM3FKE" Enabled="true" UUID="X3WA7H7HIFTELABJMUSZGJ3EAU" X="942.25" Y="110.25">
                        <InterfaceList>
                            <EventInputs>
                                <Event Name="EI0" Comment="первое событие" UUID="LOGSQQQJRXSUHPA5HPTLEJUCNM" />
                                <Event Name="EI1" Comment="второе событие" UUID="USBMKUE64M7UDKX5KQ5VDXNU5M" />
                            </EventInputs>
                            <EventOutputs>
                                <Event Name="EO" Comment="результирующее событие, возникает при возникновении любого из входных" UUID="ZDYG622BT46ENJSJX7SNGHZVP4" />
                            </EventOutputs>
                        </InterfaceList>
                    </FB>
                    <FB Name="CHECK_RIGHTS" Type="CHECK_RIGHTS" TypeUUID="5BRYFTGV5SLUJM274MTCRPCCCI" Enabled="true" UUID="R3S5LFFQ3QNUPGWPJAYOFKOHVE" X="1208.25" Y="110.875">
                        <VarValue Variable="IN0" Value="&apos;Control&apos;" Type="STRING" />
                    </FB>
                    <FB Name="CHECK_RIGHTS_0" Type="CHECK_RIGHTS" TypeUUID="5BRYFTGV5SLUJM274MTCRPCCCI" Enabled="true" UUID="GGTBQY6PA4AENMMBGHIRLUH7PE" X="1208.25" Y="206.875">
                        <VarValue Variable="IN0" Value="&apos;SetPoints&apos;" Type="STRING" />
                    </FB>
                    <FB Name="_Button_Simple" Type="TTL_Button" TypeUUID="FZV4NCDMHQIEZMCWPPWAINALOI" Enabled="true" UUID="YIYX56QTJRMEJMIPCYTTIXEU6U" X="-68.25" Y="-4.375">
                        <VarValue Variable="Text" Value="&apos;Вход&apos;" Type="STRING" />
                        <VarValue Variable="pos" Value="(x:=16,y:=16.5)" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" />
                        <VarValue Variable="size" Value="(width:=115,height:=40)" Type="TSize" TypeUUID="XDTT5M52XMSURN23S57SF26UGU" />
                    </FB>
                    <FB Name="_Button_Simple_0" Type="TTL_Button" TypeUUID="FZV4NCDMHQIEZMCWPPWAINALOI" Enabled="true" UUID="GMKDG4OY7CWUZEBHFVXK4CJQA4" X="-65.25" Y="437.625">
                        <VarValue Variable="Text" Value="&apos;Смена пароля&apos;" Type="STRING" />
                        <VarValue Variable="pos" Value="(x:=156,y:=16.5)" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" />
                        <VarValue Variable="size" Value="(width:=115,height:=40)" Type="TSize" TypeUUID="XDTT5M52XMSURN23S57SF26UGU" />
                    </FB>
                    <FB Name="CHECK_RIGHTS_5" Type="CHECK_RIGHTS" TypeUUID="5BRYFTGV5SLUJM274MTCRPCCCI" Enabled="true" UUID="DS7VHG3ZGEPUVINUHWDQLEQCWE" X="1211.25" Y="302.875">
                        <VarValue Variable="IN0" Value="&apos;Simulate&apos;" Type="STRING" />
                    </FB>
                    <FB Name="LoginEvents" Type="TLoginEvents" TypeUUID="PUC3VYMLNH5UTFKKVQFIONPRPA" Enabled="true" UUID="WZOEMO5XVTKE3EBJ7GD3Y7URG4" X="907.75" Y="373.375" />
                    <FB Name="CONCAT" Type="CONCAT" TypeUUID="7HP3AWELA2YEXGQJEJ7TED5TRU" Enabled="true" UUID="OAX4XDSRPPRU5CEX7AA7IEKTD4" X="1121.67684226928" Y="-73.260330599677">
                        <VarValue Variable="IN0" Value="&apos;$nВремя сеанса &apos;" Type="STRING" />
                        <InterfaceList>
                            <InputVars>
                                <VarDeclaration Name="IN0" Type="STRING" InitialValue="&apos;&apos;" UUID="AXI6CN37DOUUZBRC5BPPTMRVWY" />
                                <VarDeclaration Name="IN1" Type="STRING" InitialValue="&apos;&apos;" UUID="VVFNN5MKVRUU7N3IQCZRJPQYZA" />
                            </InputVars>
                            <OutputVars>
                                <VarDeclaration Name="OUT" Type="STRING" InitialValue="&apos;&apos;" UUID="LSW25TPVAJUEDLEA4A36JHIQAU" />
                            </OutputVars>
                        </InterfaceList>
                    </FB>
                    <FB Name="GT" Type="GT" TypeUUID="LX7CXXXZDZQERBKGSSMV66OHAE" Enabled="true" UUID="L25RRVAFXDOEXHVQFE2WPY2EJY" X="843.404540797282" Y="-151.638545759944">
                        <VarValue Variable="IN1" Value="T#0s" Type="TIME" />
                        <InterfaceList>
                            <InputVars>
                                <VarDeclaration Name="IN0" Type="ANY_ELEMENTARY" InitialValue="" UUID="S7L7PMQ7ZICUJEJMEXIH6N75OU" />
                                <VarDeclaration Name="IN1" Type="ANY_ELEMENTARY" InitialValue="" UUID="FRECLMIKYAOE5C5Z3HPL6POD4I" />
                            </InputVars>
                            <OutputVars>
                                <VarDeclaration Name="OUT" Type="BOOL" InitialValue="FALSE" UUID="RC43T2RQML2EFL53UDHDEIXZDM" />
                            </OutputVars>
                        </InterfaceList>
                    </FB>
                    <FB Name="W2_CONCAT_01" Type="CONCAT" TypeUUID="7HP3AWELA2YEXGQJEJ7TED5TRU" Enabled="true" UUID="4C27HS2MRL5URNWKHA2FKGSXV4" X="1503.93391899341" Y="-227.75">
                        <VarValue Variable="IN0" Value="&apos;Пользователь: &apos;" Type="STRING" />
                        <InterfaceList>
                            <InputVars>
                                <VarDeclaration Name="IN0" Type="STRING" InitialValue="&apos;&apos;" UUID="AXI6CN37DOUUZBRC5BPPTMRVWY" />
                                <VarDeclaration Name="IN1" Type="STRING" InitialValue="&apos;&apos;" UUID="VVFNN5MKVRUU7N3IQCZRJPQYZA" />
                                <VarDeclaration Name="IN2" Type="STRING" InitialValue="&apos;&apos;" UUID="VWALHD4ILK3EHFDCAUCBI5RYTQ" />
                            </InputVars>
                            <OutputVars>
                                <VarDeclaration Name="OUT" Type="STRING" InitialValue="&apos;&apos;" UUID="LSW25TPVAJUEDLEA4A36JHIQAU" />
                            </OutputVars>
                        </InterfaceList>
                    </FB>
                    <FB Name="FORMAT_TIME" Type="FORMAT_TIME" TypeUUID="55SPV7QHMHZU3PWDJ5IEMAOLOY" Enabled="true" UUID="W6JPSVDPPPIU3GVBJQKL7YIKLA" X="845.75" Y="-18.44510076594">
                        <VarValue Variable="FORMAT" Value="&apos;hh:mm:ss&apos;" Type="STRING" />
                    </FB>
                    <FB Name="SEL" Type="SEL" TypeUUID="VTYYYXK24ZYEFIHECN6CYXIJ5M" Enabled="true" UUID="ALVDQXFYVVUENIVCVQX5DZTZEY" X="1330.67684226928" Y="-105.385330599677">
                        <VarValue Variable="IN0" Value="&apos;&apos;" Type="STRING" />
                    </FB>
                    <FB Name="CHECK_RIGHTS_1" Type="CHECK_RIGHTS" TypeUUID="5BRYFTGV5SLUJM274MTCRPCCCI" Enabled="true" UUID="LBRUKZACOBVEJGVDYCUDCM56HA" X="1217.75" Y="572.875">
                        <VarValue Variable="IN0" Value="&apos;ViewArj&apos;" Type="STRING" />
                    </FB>
                    <FB Name="CHECK_RIGHTS_2" Type="CHECK_RIGHTS" TypeUUID="5BRYFTGV5SLUJM274MTCRPCCCI" Enabled="true" UUID="KXYXGTGRM6UERLL5263OSQCGFE" X="1214.75" Y="476.875">
                        <VarValue Variable="IN0" Value="&apos;Print&apos;" Type="STRING" />
                    </FB>
                    <FB Name="CHECK_RIGHTS_3" Type="CHECK_RIGHTS" TypeUUID="5BRYFTGV5SLUJM274MTCRPCCCI" Enabled="true" UUID="JSSWC7ML4LCU5MEG3CVLPDIIGY" X="1214.75" Y="380.875">
                        <VarValue Variable="IN0" Value="&apos;CfgEvViewer&apos;" Type="STRING" />
                    </FB>
                    <FB Name="CHECK_RIGHTS_4" Type="CHECK_RIGHTS" TypeUUID="5BRYFTGV5SLUJM274MTCRPCCCI" Enabled="true" UUID="AHVD6JQCYYCE5AHSNWJCEMSFOY" X="1214.25" Y="671.875">
                        <VarValue Variable="IN0" Value="&apos;QuitAlarm&apos;" Type="STRING" />
                    </FB>
                    <EventConnections>
                        <Connection Source="E_MERGE_0.EO" Destination="Close" SourceUUID="72521F7B4E42C26189D9ABB0FA4D95A1.6B6FF0C8463C9F41E4BF49A67F351FD3" DestinationUUID="35001D8749D8D62E6BC449A2637B7549" />
                        <Connection Source="USER_1.LOGGED_IN" Destination="E_MERGE.EI0" SourceUUID="30AB47904368802B57B0DBA799CFB5B6.B77A355349DB4A2498EFD381D024A8B1" DestinationUUID="9F0FECBE456641E72565298005642793.42288D5B43E58D09E63B1DBC6B8226B2" dx1="10" dx2="120.5" dy="0.625" />
                        <Connection Source="USER_1.LOGGED_OUT" Destination="E_MERGE.EI1" SourceUUID="30AB47904368802B57B0DBA799CFB5B6.9152C1E74D540031C14729B0BD400264" DestinationUUID="9F0FECBE456641E72565298005642793.50C582A4413FE39E3B54FDAAEBB4DD51" dx1="117.5" dx2="13" dy="-15.625" />
                        <Connection Source="E_MERGE.EO" Destination="CHECK_RIGHTS.CHECK" SourceUUID="9F0FECBE456641E72565298005642793.6B6FF0C8463C9F41E4BF49A67F351FD3" DestinationUUID="94D5E58E471BDCB03048CF9AA9C7A9E2.4295C6BA4A8AF8D921ACFBA5AF6D8C51" dx1="104" dx2="103" dy="0.625" />
                        <Connection Source="E_MERGE.EO" Destination="CHECK_RIGHTS_0.CHECK" SourceUUID="9F0FECBE456641E72565298005642793.6B6FF0C8463C9F41E4BF49A67F351FD3" DestinationUUID="6318A631460007CFD13181B179FFD015.4295C6BA4A8AF8D921ACFBA5AF6D8C51" dx1="117.75" dx2="89.25" dy="96.625" />
                        <Connection Source="_Button_Simple.released" Destination="E_MERGE_0.EI0" SourceUUID="FA7E31C244584C1327160FB1F5945C34.1C900A5246AFD9557EA3E4BF291B8624" DestinationUUID="72521F7B4E42C26189D9ABB0FA4D95A1.42288D5B43E58D09E63B1DBC6B8226B2" dx1="96.75" dx2="60.75" dy="183.625" />
                        <Connection Source="_Button_Simple.released" Destination="USER_1.LOGOUT" SourceUUID="FA7E31C244584C1327160FB1F5945C34.1C900A5246AFD9557EA3E4BF291B8624" DestinationUUID="30AB47904368802B57B0DBA799CFB5B6.9AC48D6C44121E8667928E957A1E0969" dx1="455" dx2="10" dy="0.25" />
                        <Connection Source="_Button_Simple_0.released" Destination="USER_1.CHANGE_PASSWORD" SourceUUID="713314334CADF8D86E2D2790073009AE.1C900A5246AFD9557EA3E4BF291B8624" DestinationUUID="30AB47904368802B57B0DBA799CFB5B6.432218CC49D5F359FF3D8EBE9ECDBA77" dx1="384.75" dx2="68.25" dy="-458" />
                        <Connection Source="_Button_Simple_0.released" Destination="E_MERGE_0.EI1" SourceUUID="713314334CADF8D86E2D2790073009AE.1C900A5246AFD9557EA3E4BF291B8624" DestinationUUID="72521F7B4E42C26189D9ABB0FA4D95A1.50C582A4413FE39E3B54FDAAEBB4DD51" dx1="92.75" dx2="61.75" dy="-242.125" />
                        <Connection Source="E_MERGE.EO" Destination="CHECK_RIGHTS_5.CHECK" SourceUUID="9F0FECBE456641E72565298005642793.6B6FF0C8463C9F41E4BF49A67F351FD3" DestinationUUID="9B53BF1C4A1F3179873DB4A1B1029205.4295C6BA4A8AF8D921ACFBA5AF6D8C51" dx1="117.75" dx2="92.25" dy="192.625" />
                        <Connection Source="show" Destination="LoginEvents.copyName" SourceUUID="C7EAA1EB434D26CD0E95FEB5B380ED33" DestinationUUID="3B465CB64DD4ACB787F9299037917EBC.C65561A9455C9AABFE890392D0DA8978" />
                        <Connection Source="USER_1.LOGGED_IN" Destination="LoginEvents.logIn" SourceUUID="30AB47904368802B57B0DBA799CFB5B6.B77A355349DB4A2498EFD381D024A8B1" DestinationUUID="3B465CB64DD4ACB787F9299037917EBC.90654610467C243FCD5B8F9B2E499AB1" dx1="86" dx2="10" dy="280" />
                        <Connection Source="USER_1.LOGGED_OUT" Destination="LoginEvents.logOut" SourceUUID="30AB47904368802B57B0DBA799CFB5B6.9152C1E74D540031C14729B0BD400264" DestinationUUID="3B465CB64DD4ACB787F9299037917EBC.73B8436F44FF94E73FC9D2AC7953B5D6" dx1="86" dx2="10" dy="263.75" />
                        <Connection Source="USER_1.LOGIN_FAILED" Destination="LoginEvents.logFail" SourceUUID="30AB47904368802B57B0DBA799CFB5B6.95E7832241408300FA4F38B96378098E" DestinationUUID="3B465CB64DD4ACB787F9299037917EBC.3C7BE2A1410E3D4A57EE7E87CDAEDA5F" dx1="86" dx2="10" dy="296.25" />
                        <Connection Source="E_MERGE.EO" Destination="CHECK_RIGHTS_3.CHECK" SourceUUID="9F0FECBE456641E72565298005642793.6B6FF0C8463C9F41E4BF49A67F351FD3" DestinationUUID="7D61A54C4EC5E28BAAD886B036088DB7.4295C6BA4A8AF8D921ACFBA5AF6D8C51" dx1="203.5" dx2="10" dy="270.625" />
                        <Connection Source="E_MERGE.EO" Destination="CHECK_RIGHTS_2.CHECK" SourceUUID="9F0FECBE456641E72565298005642793.6B6FF0C8463C9F41E4BF49A67F351FD3" DestinationUUID="4C73F15548A867D1B6D77DAD294640E9.4295C6BA4A8AF8D921ACFBA5AF6D8C51" dx1="203.5" dx2="10" dy="366.625" />
                        <Connection Source="E_MERGE.EO" Destination="CHECK_RIGHTS_1.CHECK" SourceUUID="9F0FECBE456641E72565298005642793.6B6FF0C8463C9F41E4BF49A67F351FD3" DestinationUUID="64456358446A7002A8C0A39A38BE3331.4295C6BA4A8AF8D921ACFBA5AF6D8C51" dx1="206.5" dx2="10" dy="462.625" />
                        <Connection Source="E_MERGE.EO" Destination="CHECK_RIGHTS_4.CHECK" SourceUUID="9F0FECBE456641E72565298005642793.6B6FF0C8463C9F41E4BF49A67F351FD3" DestinationUUID="263FEA014E04C602926DF28076453222.4295C6BA4A8AF8D921ACFBA5AF6D8C51" dx1="203" dx2="10" dy="561.625" />
                    </EventConnections>
                    <DataConnections>
                        <Connection Source="USER_1.USER" Destination="LoginEvents.userName" SourceUUID="30AB47904368802B57B0DBA799CFB5B6.6AD400E248AD0BC2481115BA854797B0" DestinationUUID="3B465CB64DD4ACB787F9299037917EBC.08F5FC924172DB4F6B1B6CB64A0CF283" dx1="10" dx2="86" dy="280" />
                        <Connection Source="CONCAT.OUT" Destination="SEL.IN1" SourceUUID="8ECB2F704EE37B5101F897881F5311F4.CDAEAD5C416802F537E080AC05109DE4" DestinationUUID="5C38EA024668ADB82FACA2A22679E6D1.E7D04E4C409286FE8F07AC896536E91F" dx1="30.5" dx2="27" dy="0.375" />
                        <Connection Source="SEL.OUT" Destination="W2_CONCAT_01.IN2" SourceUUID="5C38EA024668ADB82FACA2A22679E6D1.D94D29B049B6DB4E0A29EA9CB5266805" DestinationUUID="CBF3B5E048FB8A4C3438CAB6AF571A55.8FB380AD43B65A88040562949C387614" dx1="28.7571" dx2="27" dy="-89.8647" />
                        <Connection Source="FORMAT_TIME.OUT" Destination="CONCAT.IN1" SourceUUID="54F992B74DD17B6F144CA19A580AE1BF.0097E3214BF69B5D802FFE988AD40B81" DestinationUUID="8ECB2F704EE37B5101F897881F5311F4.F5D64AAD4F69AC8AB38068B7C818BE14" dx1="73.4268" dx2="27" dy="-38.5652" />
                        <Connection Source="GT.OUT" Destination="SEL.G" SourceUUID="D418BB5E4BDCB8053529B09E4E44E367.EAB9B98842F46230CEA0BBAF1BF92232" DestinationUUID="5C38EA024668ADB82FACA2A22679E6D1.E51CF88C46776F33BF0D21B3F4741605" dx1="266.772" dx2="27" dy="46.2532" />
                        <Connection Source="USER_1.TIME_LEFT" Destination="GT.IN0" SourceUUID="30AB47904368802B57B0DBA799CFB5B6.174573A04D524E9F6439E5B4475071D4" DestinationUUID="D418BB5E4BDCB8053529B09E4E44E367.B2F7D7974405CA1FD0252C9175FD377F" dx1="10" dx2="21.6545" dy="-368.514" />
                        <Connection Source="USER_1.TIME_LEFT" Destination="FORMAT_TIME.IN0" SourceUUID="30AB47904368802B57B0DBA799CFB5B6.174573A04D524E9F6439E5B4475071D4" DestinationUUID="54F992B74DD17B6F144CA19A580AE1BF.F38847D0426484DEDE16F989EB56D1FA" dx1="10" dx2="24" dy="-219.07" />
                        <Connection Source="USER_1.USER" Destination="W2_CONCAT_01.IN1" SourceUUID="30AB47904368802B57B0DBA799CFB5B6.6AD400E248AD0BC2481115BA854797B0" DestinationUUID="CBF3B5E048FB8A4C3438CAB6AF571A55.F5D64AAD4F69AC8AB38068B7C818BE14" dx1="10.25" dx2="681.934" dy="-379.625" />
                        <Connection Source="W2_CONCAT_01.OUT" Destination="knText" SourceUUID="CBF3B5E048FB8A4C3438CAB6AF571A55.CDAEAD5C416802F537E080AC05109DE4" DestinationUUID="91A545CC4D7565BE5D54C6B3866F875B" />
                        <Connection Source="Node" Destination="LoginEvents.source" SourceUUID="1066CBB24613CBF20662A5A36435643D" DestinationUUID="3B465CB64DD4ACB787F9299037917EBC.BFB1D5AF45A55944161A4DBE8313CEB7" />
                        <Connection Source="CHECK_RIGHTS.OUT" Destination="::R_Control" SourceUUID="94D5E58E471BDCB03048CF9AA9C7A9E2.A6BED21940AF6E08713F4CAEC1C4A487" DestinationUUID="::FCFEB2D14D3F0E9874A69F9D87E79E41" />
                        <Connection Source="CHECK_RIGHTS_0.OUT" Destination="::R_SetPoint" SourceUUID="6318A631460007CFD13181B179FFD015.A6BED21940AF6E08713F4CAEC1C4A487" DestinationUUID="::CC780D0447A1103A26E4409AF4F01FA7" />
                        <Connection Source="CHECK_RIGHTS_5.OUT" Destination="::R_Simulate" SourceUUID="9B53BF1C4A1F3179873DB4A1B1029205.A6BED21940AF6E08713F4CAEC1C4A487" DestinationUUID="::BD5213A7428BEFA5F050869D97D45623" />
                        <Connection Source="CHECK_RIGHTS_3.OUT" Destination="::R_CfgEvViewer" SourceUUID="7D61A54C4EC5E28BAAD886B036088DB7.A6BED21940AF6E08713F4CAEC1C4A487" DestinationUUID="::FECBBF4B450CEF8931F4AC8D85059C74" />
                        <Connection Source="CHECK_RIGHTS_2.OUT" Destination="::R_Print" SourceUUID="4C73F15548A867D1B6D77DAD294640E9.A6BED21940AF6E08713F4CAEC1C4A487" DestinationUUID="::CE3F4CAA4D3C816EBF47309CCBF6CA40" />
                        <Connection Source="CHECK_RIGHTS_1.OUT" Destination="::R_ViewArj" SourceUUID="64456358446A7002A8C0A39A38BE3331.A6BED21940AF6E08713F4CAEC1C4A487" DestinationUUID="::55044EB146D13DDC053C96B64115DC9D" />
                        <Connection Source="CHECK_RIGHTS_4.OUT" Destination="::R_QuitAlarm" SourceUUID="263FEA014E04C602926DF28076453222.A6BED21940AF6E08713F4CAEC1C4A487" DestinationUUID="::034021C04AE0477941182098F6475ED1" />
                    </DataConnections>
                </FBNetwork>
            </SubWindowFBType>
            <SubWindowFBType Name="T_DataBaseIB_Wnd" ShowVarTypes="true" UUID="NEHN2R3G67NEJBQONRZIKOVIIU">
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
                        <VarDeclaration Name="size" Type="TSize" TypeUUID="XDTT5M52XMSURN23S57SF26UGU" Comment="размер прямоугольника" Group="Общие" InitialValue="(width:=500,height:=360)" UUID="HC2FKFJ4NBUU3J5U7QZTECI2TM" />
                        <VarDeclaration Name="frame_color" Type="TColor" TypeUUID="EDYJMIBCJR5UJOZWGS3UVJENZA" InitialValue="4293980400" UUID="GS2XRATVXFKEDNVR4AYF2FOHB4" />
                        <VarDeclaration Name="bg_color" Type="TColor" TypeUUID="EDYJMIBCJR5UJOZWGS3UVJENZA" InitialValue="4294967295" UUID="IZCT7UFDEEXEXA45WVKQH4CXO4" />
                        <VarDeclaration Name="caption" Type="STRING" InitialValue="&apos;&apos;" UUID="4SEHRDHYXADETHGWSFVJCJBXGI" />
                        <VarDeclaration Name="caption_font" Type="TFont" TypeUUID="YVT73EACFULUPIWKAFYTDAC3S4" InitialValue="(family:=&apos;PT Sans&apos;,size:=12,bold:=FALSE,italic:=FALSE,underline:=FALSE,strikeout:=FALSE)" UUID="QSRIHPHZL46UPJPPH4M4OB7PS4" />
                        <VarDeclaration Name="closable" Type="BOOL" InitialValue="FALSE" UUID="MHEPWGX4TXFUPIWFJHGMKSAXPA" />
                    </InputVars>
                </InterfaceList>
                <FBNetwork>
                    <FB Name="TLButton_0" Type="TTLButton" TypeUUID="GCLFMT6OHZVEFEJCWS6KYXUKVM" Enabled="true" UUID="X4GXETGRDE2EJP6R4JDKTIESYQ" X="1422.25" Y="2943">
                        <VarValue Variable="highlightColor" Value="4278222848" Type="TColor" TypeUUID="EDYJMIBCJR5UJOZWGS3UVJENZA" />
                        <VarValue Variable="pos" Value="(x:=29,y:=110)" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" />
                        <VarValue Variable="size" Value="(width:=426,height:=23)" Type="TSize" TypeUUID="XDTT5M52XMSURN23S57SF26UGU" />
                        <VarValue Variable="text" Value="&apos;Соединиться с базой данных&apos;" Type="STRING" />
                    </FB>
                    <FB Name="NewString_3" Type="TNewString" TypeUUID="E5KCKMMFJL5ULIXLKXSUHJALFU" Enabled="true" UUID="XRDJXYNKAPIEBGQBAVQ7GF2M6M" X="1434.25" Y="2518">
                        <VarValue Variable="name" Value="&apos;Имя БД ИБ&apos;" Type="STRING" />
                        <VarValue Variable="pos" Value="(x:=34,y:=81)" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" />
                        <VarValue Variable="zValue" Value="1000001.005" Type="LREAL" />
                    </FB>
                    <FB Name="CUR_DATA_5" Type="CUR_DATA" TypeUUID="63RFPIII26GUTO6ECZZ5724EPY" Enabled="true" UUID="E2PTSMMZD6FUROY747FQFEN3T4" X="878" Y="1605.75">
                        <VarValue Variable="VAR" Value="&apos;connectedBD&apos;" Type="STRING" />
                    </FB>
                    <FB Name="SimpleText_1" Type="TSimpleText" TypeUUID="OBURUFGSRT7UVLSMGMSUGBKM5E" Enabled="true" UUID="HDX5VCQM6KWERJAR3JJE3RMYRE" X="1531.75" Y="1346">
                        <VarValue Variable="alignment" Value="8" Type="TAlignment" TypeUUID="IUA2FTZVSF6EVJPPY3ZKXNHV6E" />
                        <VarValue Variable="pos" Value="(x:=33,y:=137)" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" />
                        <VarValue Variable="size" Value="(width:=420,height:=18)" Type="TSize" TypeUUID="XDTT5M52XMSURN23S57SF26UGU" />
                        <VarValue Variable="zValue" Value="1000001.001" Type="LREAL" />
                    </FB>
                    <FB Name="BASE64_DECODE" Type="BASE64_DECODE" TypeUUID="PQ5RU2BZBONURBEKWY3DZ64Q3Y" Enabled="true" UUID="53SXVYMSSW6UTE6XLBH6VMDQFE" X="1104.5" Y="2142.75" />
                    <FB Name="NewString_2" Type="TNewString" TypeUUID="E5KCKMMFJL5ULIXLKXSUHJALFU" Enabled="true" UUID="KYQT5QORCPFU3J2ZF2ODYDW3EU" X="1433.75" Y="2194">
                        <VarValue Variable="name" Value="&apos;Пароль пользователя БД ИБ&apos;" Type="STRING" />
                        <VarValue Variable="pos" Value="(x:=34,y:=58)" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" />
                        <VarValue Variable="zValue" Value="1000001.005" Type="LREAL" />
                    </FB>
                    <FB Name="BASE64_DECODE_1" Type="BASE64_DECODE" TypeUUID="PQ5RU2BZBONURBEKWY3DZ64Q3Y" Enabled="true" UUID="XSKS7VCQIU3ETC5X2MTULEZB6U" X="1111.5" Y="2803.75" />
                    <FB Name="SEL_0" Type="SEL" TypeUUID="VTYYYXK24ZYEFIHECN6CYXIJ5M" Enabled="true" UUID="IT3MSL4FZGGEDALQXMIYEBXDOA" X="1161" Y="1650.625">
                        <VarValue Variable="IN0" Value="4294901760" Type="TColor" TypeUUID="EDYJMIBCJR5UJOZWGS3UVJENZA" />
                        <VarValue Variable="IN1" Value="4278255360" Type="TColor" TypeUUID="EDYJMIBCJR5UJOZWGS3UVJENZA" />
                    </FB>
                    <FB Name="SimpleText" Type="TSimpleText" TypeUUID="OBURUFGSRT7UVLSMGMSUGBKM5E" Enabled="true" UUID="D32DGOCAQEXU7GMPXHZWM5QEIE" X="1422.64910700436" Y="6">
                        <VarValue Variable="pos" Value="(x:=34,y:=9)" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" />
                        <VarValue Variable="size" Value="(width:=119.490058724122,height:=23)" Type="TSize" TypeUUID="XDTT5M52XMSURN23S57SF26UGU" />
                        <VarValue Variable="text" Value="&apos;Текущий пользователь:&apos;" Type="STRING" />
                        <VarValue Variable="zValue" Value="1000001.007" Type="LREAL" />
                    </FB>
                    <FB Name="NewString_1" Type="TNewString" TypeUUID="E5KCKMMFJL5ULIXLKXSUHJALFU" Enabled="true" UUID="UN3TY43F3KKE7J7CE6YIAQW5NY" X="1440.25" Y="1857">
                        <VarValue Variable="name" Value="&apos;Имя пользователя БД ИБ&apos;" Type="STRING" />
                        <VarValue Variable="pos" Value="(x:=34,y:=35)" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" />
                        <VarValue Variable="zValue" Value="1000001.005" Type="LREAL" />
                    </FB>
                    <FB Name="NewString_0" Type="TNewString" TypeUUID="E5KCKMMFJL5ULIXLKXSUHJALFU" Enabled="true" UUID="HVJGNBCKGY7EDGGBHISBNSJIS4" X="290.046828903555" Y="1426.31029706534">
                        <VarValue Variable="name" Value="&apos;Шаблон имени файла&apos;" Type="STRING" />
                        <VarValue Variable="pos" Value="(x:=36,y:=261)" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" />
                        <VarValue Variable="zValue" Value="1000001.005" Type="LREAL" />
                    </FB>
                    <FB Name="CUR_DATA_8" Type="CUR_DATA" TypeUUID="63RFPIII26GUTO6ECZZ5724EPY" Enabled="true" UUID="A5NVTFCEZ4PU7BUCQHPCSKTJFM" X="927" Y="2787.75">
                        <VarValue Variable="VAR" Value="&apos;nameBD&apos;" Type="STRING" />
                    </FB>
                    <FB Name="SimpleText_0" Type="TSimpleText" TypeUUID="OBURUFGSRT7UVLSMGMSUGBKM5E" Enabled="true" UUID="5AJ4A3P4AMOETFHO5YHCBWVG5A" X="1409.25623297326" Y="403.655841085254">
                        <VarValue Variable="pos" Value="(x:=155,y:=9)" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" />
                        <VarValue Variable="size" Value="(width:=202,height:=23)" Type="TSize" TypeUUID="XDTT5M52XMSURN23S57SF26UGU" />
                        <VarValue Variable="zValue" Value="1000001.007" Type="LREAL" />
                    </FB>
                    <FB Name="E_SR" Type="E_SR" TypeUUID="RRP6KOL3Q66ERAUTY4G4XHPSJ4" Enabled="true" UUID="YNVWXKEPM4QEVE2SLQ2V5FETSE" X="2045.5" Y="2207.75" />
                    <FB Name="NewString" Type="TNewString" TypeUUID="E5KCKMMFJL5ULIXLKXSUHJALFU" Enabled="true" UUID="PFR5M7YYKSEUHHHTT43YJSR5NE" X="299.75" Y="1029">
                        <VarValue Variable="name" Value="&apos;Путь сохранения базы данных&apos;" Type="STRING" />
                        <VarValue Variable="pos" Value="(x:=36,y:=238)" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" />
                        <VarValue Variable="zValue" Value="1000001.005" Type="LREAL" />
                    </FB>
                    <FB Name="CUR_DATA_0" Type="CUR_DATA" TypeUUID="63RFPIII26GUTO6ECZZ5724EPY" Enabled="true" UUID="ISBWJDSE23KUTPMPFT75WJZ7RE" X="13.624629258726" Y="607.741102209433">
                        <VarValue Variable="VAR" Value="&apos;countWarningEvents&apos;" Type="STRING" />
                    </FB>
                    <FB Name="CUR_DATA_7" Type="CUR_DATA" TypeUUID="63RFPIII26GUTO6ECZZ5724EPY" Enabled="true" UUID="7GDALRY2XLKEZN52ELZGBWLBQY" X="920" Y="2444.75">
                        <VarValue Variable="VAR" Value="&apos;passBD&apos;" Type="STRING" />
                    </FB>
                    <FB Name="CUR_DATA_6" Type="CUR_DATA" TypeUUID="63RFPIII26GUTO6ECZZ5724EPY" Enabled="true" UUID="BUJECE6WKPXUDBVD2M5WS5ZHOA" X="921" Y="2127.75">
                        <VarValue Variable="VAR" Value="&apos;userBD&apos;" Type="STRING" />
                    </FB>
                    <FB Name="NewEditor" Type="TNewEditor" TypeUUID="OYKZWYZHFTIUXAJILU4I2UEWGM" Enabled="true" UUID="Q7BTTRLOTDJERBQTGODKQLLIBQ" X="315.25">
                        <VarValue Variable="name" Value="&apos;Количество событий&apos;" Type="STRING" />
                        <VarValue Variable="pos" Value="(x:=36,y:=169)" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" />
                        <VarValue Variable="zValue" Value="1000001" Type="LREAL" />
                    </FB>
                    <FB Name="TLButton" Type="TTLButton" TypeUUID="GCLFMT6OHZVEFEJCWS6KYXUKVM" Enabled="true" UUID="32BTZNKEPIWENGZ6DGUPXHAY6A" X="1403.27316389796" Y="848.173464562541">
                        <VarValue Variable="pos" Value="(x:=30,y:=287)" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" />
                        <VarValue Variable="size" Value="(width:=426,height:=23)" Type="TSize" TypeUUID="XDTT5M52XMSURN23S57SF26UGU" />
                        <VarValue Variable="text" Value="&apos;Сохранить изменения&apos;" Type="STRING" />
                    </FB>
                    <FB Name="CUR_DATA_3" Type="CUR_DATA" TypeUUID="63RFPIII26GUTO6ECZZ5724EPY" Enabled="true" UUID="RA23RFEB5VMUFAQQBTMRM2I6WI" X="18.060798172975" Y="1696.40314410213">
                        <VarValue Variable="VAR" Value="&apos;nameFile&apos;" Type="STRING" />
                    </FB>
                    <FB Name="BASE64_DECODE_0" Type="BASE64_DECODE" TypeUUID="PQ5RU2BZBONURBEKWY3DZ64Q3Y" Enabled="true" UUID="EQ4HQC5P22YEBOFWEGQKVI7MRQ" X="1120" Y="2480.75" />
                    <FB Name="NewEditor_0" Type="TNewEditor" TypeUUID="OYKZWYZHFTIUXAJILU4I2UEWGM" Enabled="true" UUID="EOWQXBFNJCRUHMPWMNPW67MW7E" X="303.75" Y="338">
                        <VarValue Variable="name" Value="&apos;Пред. о переполнении при кол-ве&apos;" Type="STRING" />
                        <VarValue Variable="pos" Value="(x:=36,y:=192)" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" />
                        <VarValue Variable="zValue" Value="1000001" Type="LREAL" />
                    </FB>
                    <FB Name="BASE64_ENCODE_1" Type="BASE64_ENCODE" TypeUUID="45JIHQYHCM6ETEH34ZAYY4K67U" Enabled="true" UUID="2CWFGX477LWURBCCD6KVTPNQVI" X="2170" Y="2659.875" />
                    <FB Name="SEL" Type="SEL" TypeUUID="VTYYYXK24ZYEFIHECN6CYXIJ5M" Enabled="true" UUID="HWIEQZI3DV4UREUSLJPO7B53OY" X="1163.5" Y="1561.625">
                        <VarValue Variable="IN0" Value="&apos;Не подключено&apos;" Type="STRING" />
                        <VarValue Variable="IN1" Value="&apos;Подключено&apos;" Type="STRING" />
                    </FB>
                    <FB Name="BASE64_ENCODE_0" Type="BASE64_ENCODE" TypeUUID="45JIHQYHCM6ETEH34ZAYY4K67U" Enabled="true" UUID="XLQS3BBQHHLURJPK5CZNC2MTOA" X="2172.5" Y="2418.875" />
                    <FB Name="E_MERGE" Type="E_MERGE" TypeUUID="JXEGZ46GJOGE7GKSENPHVM3FKE" Enabled="true" UUID="XQKROMQX4TJE7EWOMSPU2VLDII" X="1720.5" Y="2229.25">
                        <InterfaceList>
                            <EventInputs>
                                <Event Name="EI0" Comment="первое событие" UUID="LOGSQQQJRXSUHPA5HPTLEJUCNM" />
                                <Event Name="EI1" Comment="второе событие" UUID="USBMKUE64M7UDKX5KQ5VDXNU5M" />
                                <Event Name="EI2" UUID="UWAB3XPMNUNUBL4XSXZM77EJI4" />
                            </EventInputs>
                            <EventOutputs>
                                <Event Name="EO" Comment="результирующее событие, возникает при возникновении любого из входных" UUID="ZDYG622BT46ENJSJX7SNGHZVP4" />
                            </EventOutputs>
                        </InterfaceList>
                    </FB>
                    <FB Name="NewEditor_1" Type="TNewEditor" TypeUUID="OYKZWYZHFTIUXAJILU4I2UEWGM" Enabled="true" UUID="TQCYGT5CQJEUXEV7EJVFZVOEPM" X="304.25" Y="691">
                        <VarValue Variable="name" Value="&apos;Период выдачи событий в сек.&apos;" Type="STRING" />
                        <VarValue Variable="pos" Value="(x:=36,y:=215)" Type="TPos" TypeUUID="CUUMQF3SQNRUHD62PGG7FSXXFY" />
                        <VarValue Variable="zValue" Value="1000001" Type="LREAL" />
                    </FB>
                    <FB Name="CUR_DATA_1" Type="CUR_DATA" TypeUUID="63RFPIII26GUTO6ECZZ5724EPY" Enabled="true" UUID="R2PPRIXZY7BUNGC5MDDD4AQBSA" X="42.058607216627" Y="960.92878758007">
                        <VarValue Variable="VAR" Value="&apos;timePeriod&apos;" Type="STRING" />
                    </FB>
                    <FB Name="CUR_DATA_2" Type="CUR_DATA" TypeUUID="63RFPIII26GUTO6ECZZ5724EPY" Enabled="true" UUID="27JOXGSPEBBUFDMMV73CRER37Q" X="24.686202405542" Y="1299.86721443325">
                        <VarValue Variable="VAR" Value="&apos;dir&apos;" Type="STRING" />
                    </FB>
                    <FB Name="CUR_DATA" Type="CUR_DATA" TypeUUID="63RFPIII26GUTO6ECZZ5724EPY" Enabled="true" UUID="LZZK6N4YOQJU5OKGSQIUTWDRFY" Y="269.75">
                        <VarValue Variable="VAR" Value="&apos;countEvents&apos;" Type="STRING" />
                    </FB>
                    <FB Name="BASE64_ENCODE" Type="BASE64_ENCODE" TypeUUID="45JIHQYHCM6ETEH34ZAYY4K67U" Enabled="true" UUID="ABWH3RXPPV2UNCNVJGNZ4OQFJU" X="1776.5" Y="2010.875" />
                    <FB Name="CUR_DATA_4" Type="CUR_DATA" TypeUUID="63RFPIII26GUTO6ECZZ5724EPY" Enabled="true" UUID="WSBNMUFIDZNEJLETA7IX6MVSBI" X="987" Y="940.75">
                        <VarValue Variable="VAR" Value="&apos;save&apos;" Type="STRING" />
                    </FB>
                    <FB Name="SEL_1" Type="SEL" TypeUUID="VTYYYXK24ZYEFIHECN6CYXIJ5M" Enabled="true" UUID="UQOLG2RPN7JU7L2QAHOE535B6E" X="1196.25" Y="1050.625">
                        <VarValue Variable="IN1" Value="4278222848" Type="TColor" TypeUUID="EDYJMIBCJR5UJOZWGS3UVJENZA" />
                    </FB>
                    <FB Name="E2RegEventButton_0" Type="TIS2RegEventButton" TypeUUID="ZNZZ47LTYMZUNHA2UGTJLLMH7E" Enabled="true" UUID="KLTZVNQID6QEBLYQ3EU7B4UYBY" X="1852.25" Y="2959.25">
                        <VarValue Variable="Caption" Value="&apos;Окно настройки БД&apos;" Type="STRING" />
                        <VarValue Variable="M_Type" Value="&apos;Кнопка&apos;" Type="STRING" />
                        <VarValue Variable="NameButton" Value="&apos;Соединие с базой данных&apos;" Type="STRING" />
                        <VarValue Variable="Other" Value="&apos;IS&apos;" Type="STRING" />
                    </FB>
                    <FB Name="E_MERGE_0" Type="E_MERGE" TypeUUID="JXEGZ46GJOGE7GKSENPHVM3FKE" Enabled="true" UUID="CQ4KWTWVFVSUXARJELRQNH3V2Y" X="1833.25" Y="2785.25">
                        <InterfaceList>
                            <EventInputs>
                                <Event Name="EI0" Comment="первое событие" UUID="LOGSQQQJRXSUHPA5HPTLEJUCNM" />
                                <Event Name="EI1" Comment="второе событие" UUID="USBMKUE64M7UDKX5KQ5VDXNU5M" />
                            </EventInputs>
                            <EventOutputs>
                                <Event Name="EO" Comment="результирующее событие, возникает при возникновении любого из входных" UUID="ZDYG622BT46ENJSJX7SNGHZVP4" />
                            </EventOutputs>
                        </InterfaceList>
                    </FB>
                    <FB Name="E2RegEventButton_1" Type="TIS2RegEventButton" TypeUUID="ZNZZ47LTYMZUNHA2UGTJLLMH7E" Enabled="true" UUID="GEH6MD5AMOEUBEFDQPC3LXT3PE" X="1806.5" Y="1001.75">
                        <VarValue Variable="Caption" Value="&apos;Окно настройки БД&apos;" Type="STRING" />
                        <VarValue Variable="M_Type" Value="&apos;Кнопка&apos;" Type="STRING" />
                        <VarValue Variable="NameButton" Value="&apos;Соединить настройки БД&apos;" Type="STRING" />
                        <VarValue Variable="Other" Value="&apos;IS&apos;" Type="STRING" />
                    </FB>
                    <FB Name="SET_SIGNAL_DATA" Type="SET_SIGNAL_DATA" TypeUUID="DD2Z7RQDF3WU7JTZYWZ2CNRCYQ" Enabled="true" UUID="SNQYVXTWKANUNKUPZF54IRDM44" X="2509.25" Y="2617.375">
                        <VarValue Variable="NAME" Value="&apos;nameBD&apos;" Type="STRING" />
                    </FB>
                    <FB Name="SET_SIGNAL_DATA_0" Type="SET_SIGNAL_DATA" TypeUUID="DD2Z7RQDF3WU7JTZYWZ2CNRCYQ" Enabled="true" UUID="DTENRAPVN4YEJJSAWIH7ZMXVEY" X="2598.25" Y="2374.375">
                        <VarValue Variable="NAME" Value="&apos;passBD&apos;" Type="STRING" />
                    </FB>
                    <FB Name="SET_SIGNAL_DATA_1" Type="SET_SIGNAL_DATA" TypeUUID="DD2Z7RQDF3WU7JTZYWZ2CNRCYQ" Enabled="true" UUID="2KHVMW2TTS3U5EBRX4KW4WD4EQ" X="2594.25" Y="2208.375">
                        <VarValue Variable="NAME" Value="&apos;connectBD&apos;" Type="STRING" />
                    </FB>
                    <FB Name="SET_SIGNAL_DATA_2" Type="SET_SIGNAL_DATA" TypeUUID="DD2Z7RQDF3WU7JTZYWZ2CNRCYQ" Enabled="true" UUID="BPLYBPPCF25EDAEDU7B64KRXX4" X="2191.25" Y="1937.375">
                        <VarValue Variable="NAME" Value="&apos;userBD&apos;" Type="STRING" />
                    </FB>
                    <FB Name="SET_SIGNAL_DATA_3" Type="SET_SIGNAL_DATA" TypeUUID="DD2Z7RQDF3WU7JTZYWZ2CNRCYQ" Enabled="true" UUID="IMBETXDDET7UPA662Q6VB7CLJI" X="2100.25" Y="849.375">
                        <VarValue Variable="NAME" Value="&apos;save&apos;" Type="STRING" />
                        <VarValue Variable="VALUE" Value="TRUE" Type="BOOL" />
                    </FB>
                    <FB Name="SET_SIGNAL_DATA_4" Type="SET_SIGNAL_DATA" TypeUUID="DD2Z7RQDF3WU7JTZYWZ2CNRCYQ" Enabled="true" UUID="V5MNHCGADMEEJA2OPIVTABRQZQ" X="2096.25" Y="651.375">
                        <VarValue Variable="NAME" Value="&apos;nameUser&apos;" Type="STRING" />
                    </FB>
                    <FB Name="SET_SIGNAL_DATA_5" Type="SET_SIGNAL_DATA" TypeUUID="DD2Z7RQDF3WU7JTZYWZ2CNRCYQ" Enabled="true" UUID="FB3A5WKCYNMU7OEGH5QLLXLDYM" X="824.25" Y="114.375">
                        <VarValue Variable="NAME" Value="&apos;countEvents&apos;" Type="STRING" />
                    </FB>
                    <FB Name="SET_SIGNAL_DATA_6" Type="SET_SIGNAL_DATA" TypeUUID="DD2Z7RQDF3WU7JTZYWZ2CNRCYQ" Enabled="true" UUID="RB7I2INKDWPUNINQZF5CGREKIE" X="831.25" Y="444.375">
                        <VarValue Variable="NAME" Value="&apos;countWarningEvents&apos;" Type="STRING" />
                    </FB>
                    <FB Name="SET_SIGNAL_DATA_7" Type="SET_SIGNAL_DATA" TypeUUID="DD2Z7RQDF3WU7JTZYWZ2CNRCYQ" Enabled="true" UUID="P2KKDGNH5OHUFG23XUNKSXOTKU" X="830.25" Y="787.375">
                        <VarValue Variable="NAME" Value="&apos;timePeriod&apos;" Type="STRING" />
                    </FB>
                    <FB Name="SET_SIGNAL_DATA_8" Type="SET_SIGNAL_DATA" TypeUUID="DD2Z7RQDF3WU7JTZYWZ2CNRCYQ" Enabled="true" UUID="DI234FR5RO5UJAO533OSIMVERU" X="744.25" Y="1143.375">
                        <VarValue Variable="NAME" Value="&apos;dir&apos;" Type="STRING" />
                    </FB>
                    <FB Name="SET_SIGNAL_DATA_9" Type="SET_SIGNAL_DATA" TypeUUID="DD2Z7RQDF3WU7JTZYWZ2CNRCYQ" Enabled="true" UUID="XZS7RL2GBSUUNJI2MFT3FWUMXU" X="748.25" Y="1405.375">
                        <VarValue Variable="NAME" Value="&apos;nameFile&apos;" Type="STRING" />
                    </FB>
                    <FB Name="B_Change" Type="B_Change" TypeUUID="NZWRQBU33QQUXBOX3J3FMZ24BE" Enabled="true" UUID="RBTKPT5XT2SUNGWQND6IV6P4RQ" X="2315.75" Y="2207.875" />
                    <EventConnections>
                        <Connection Source="E_MERGE.EO" Destination="E_SR.R" SourceUUID="321715BC4FD2E4179F64CE924263554D.6B6FF0C8463C9F41E4BF49A67F351FD3" DestinationUUID="A86B6BC34A20678F355C52939193945E.7DA8AA7346A8B200581116B130862F54" dx1="131" dx2="135" dy="-5.25" />
                        <Connection Source="NewString_3.edited" Destination="E_MERGE.EI2" SourceUUID="E19B46BC40D003AA6105019AF34C17F3.C671D71E4C003A870294048C2105C0B1" DestinationUUID="321715BC4FD2E4179F64CE924263554D.DD1D80A5401B6DECF29597AF4789FCCF" dx1="45.75" dx2="53" dy="-370" />
                        <Connection Source="NewString_1.edited" Destination="E_MERGE.EI0" SourceUUID="733C77A34F94DA65B027E2A76EDD4280.C671D71E4C003A870294048C2105C0B1" DestinationUUID="321715BC4FD2E4179F64CE924263554D.42288D5B43E58D09E63B1DBC6B8226B2" dx1="10" dx2="82.75" dy="258.5" />
                        <Connection Source="NewString_2.edited" Destination="E_MERGE.EI1" SourceUUID="C13E21564DCB13D19C2E59A725DB0E3C.C671D71E4C003A870294048C2105C0B1" DestinationUUID="321715BC4FD2E4179F64CE924263554D.50C582A4413FE39E3B54FDAAEBB4DD51" dx1="10" dx2="89.25" dy="-62.25" />
                        <Connection Source="::INIT" Destination="E_MERGE_0.EI0" SourceUUID="::39706FA947703CDDA1CE85A0E7A334B1" DestinationUUID="4EAB38144B652DD5E3222982D6759F06.42288D5B43E58D09E63B1DBC6B8226B2" />
                        <Connection Source="E_MERGE_0.EO" Destination="E_SR.S" SourceUUID="4EAB38144B652DD5E3222982D6759F06.6B6FF0C8463C9F41E4BF49A67F351FD3" DestinationUUID="A86B6BC34A20678F355C52939193945E.CA109EE94AEC00A1D0AAFA857E3712F8" dx1="68.25" dx2="73" dy="-577.5" />
                        <Connection Source="TLButton_0.pressed" Destination="E2RegEventButton_0.Registrer" SourceUUID="4C720DBF443419D146E2D1BFC492A0A9.8009D6224C2F388DDFFFF5AA7C8FED14" DestinationUUID="B69AE75240A01F0829D910AF0E98F2F0.F4863EC2452A178A4460539D5B716C64" dx1="205.5" dx2="11" />
                        <Connection Source="TLButton_0.pressed" Destination="E_MERGE_0.EI1" SourceUUID="4C720DBF443419D146E2D1BFC492A0A9.8009D6224C2F388DDFFFF5AA7C8FED14" DestinationUUID="4EAB38144B652DD5E3222982D6759F06.50C582A4413FE39E3B54FDAAEBB4DD51" dx1="132.5" dx2="65" dy="-157.75" />
                        <Connection Source="TLButton.clicked" Destination="E2RegEventButton_1.Registrer" SourceUUID="B53C83DE462C7A44A8193E9BF0189CFB.A24F9CF5410E51D044BD3D8F84270DD4" DestinationUUID="0FE60F31408963A0C583A390797BDEB5.F4863EC2452A178A4460539D5B716C64" dx1="152.727" dx2="37" dy="153.577" />
                        <Connection Source="NewString_3.edited" Destination="SET_SIGNAL_DATA.SET" SourceUUID="E19B46BC40D003AA6105019AF34C17F3.C671D71E4C003A870294048C2105C0B1" DestinationUUID="DE8A6193461B50767BC98FAAE76C44C4.EEC8DDD84177096204868498B840BA96" dx1="10" dx2="877.5" dy="-14.375" />
                        <Connection Source="NewString_2.edited" Destination="SET_SIGNAL_DATA_0.SET" SourceUUID="C13E21564DCB13D19C2E59A725DB0E3C.C671D71E4C003A870294048C2105C0B1" DestinationUUID="81D8C81C44306FF50FB240A626F5B2FC.EEC8DDD84177096204868498B840BA96" dx1="10" dx2="967" dy="66.625" />
                        <Connection Source="NewString_1.edited" Destination="SET_SIGNAL_DATA_2.SET" SourceUUID="733C77A34F94DA65B027E2A76EDD4280.C671D71E4C003A870294048C2105C0B1" DestinationUUID="BD80D70B41BA2EE2C3A78380BF372AEE.EEC8DDD84177096204868498B840BA96" dx1="10" dx2="553.5" dy="-33.375" />
                        <Connection Source="TLButton.clicked" Destination="SET_SIGNAL_DATA_3.SET" SourceUUID="B53C83DE462C7A44A8193E9BF0189CFB.A24F9CF5410E51D044BD3D8F84270DD4" DestinationUUID="DC49024347FF24633DD4DE834A4BFC50.EEC8DDD84177096204868498B840BA96" dx1="10" dx2="473.477" dy="1.20154" />
                        <Connection Source="show" Destination="SET_SIGNAL_DATA_4.SET" SourceUUID="C7EAA1EB434D26CD0E95FEB5B380ED33" DestinationUUID="88D358AF44081BC02B7A4E83CC300630.EEC8DDD84177096204868498B840BA96" />
                        <Connection Source="NewEditor.edited" Destination="SET_SIGNAL_DATA_5.SET" SourceUUID="C539C38748D2986E863313860C682DA8.6819504249310186BD04BEA5044BADBD" DestinationUUID="D90E76284F59C342603F86B8C363DDB5.EEC8DDD84177096204868498B840BA96" dx1="10" dx2="314.5" dy="0.625" />
                        <Connection Source="NewEditor_0.edited" Destination="SET_SIGNAL_DATA_6.SET" SourceUUID="840BAD2343A348AD5F63F6B1F9967D6F.6819504249310186BD04BEA5044BADBD" DestinationUUID="218D7E88469F1DAA7AC9B0A1418A4423.EEC8DDD84177096204868498B840BA96" dx1="10" dx2="333" dy="-7.375" />
                        <Connection Source="NewEditor_1.edited" Destination="SET_SIGNAL_DATA_7.SET" SourceUUID="4F83059C4B4982A26A22BF927BC4D55C.6819504249310186BD04BEA5044BADBD" DestinationUUID="99A1947E428FEBA71ABD5B9B55D35DA9.EEC8DDD84177096204868498B840BA96" dx1="10" dx2="331.5" dy="-17.375" />
                        <Connection Source="NewString.edited" Destination="SET_SIGNAL_DATA_8.SET" SourceUUID="7FD6637943895418379FF39C693DCA84.C671D71E4C003A870294048C2105C0B1" DestinationUUID="16BE351A44BB8B3DDDDEDD818DA43224.EEC8DDD84177096204868498B840BA96" dx1="10" dx2="247" dy="0.625" />
                        <Connection Source="NewString_0.edited" Destination="SET_SIGNAL_DATA_9.SET" SourceUUID="8466523D413E364A243AC1989728C916.C671D71E4C003A870294048C2105C0B1" DestinationUUID="AFF865BE46A90C4667611AA5BD8CDAB2.EEC8DDD84177096204868498B840BA96" dx1="10" dx2="260.703" dy="-134.685" />
                        <Connection Source="B_Change.CHANGED" Destination="SET_SIGNAL_DATA_1.SET" SourceUUID="CFA7668846A59EB7FC68D09A8CFCF98A.DB0225DB4786CDB51E8F53A6A8B7DB6E" DestinationUUID="5B568FD24EB79C5315BF3190247C586E.EEC8DDD84177096204868498B840BA96" dx1="10" dx2="434.25" dy="0.5" />
                    </EventConnections>
                    <DataConnections>
                        <Connection Source="CUR_DATA_7.DATA" Destination="BASE64_DECODE_0.IN0" SourceUUID="C70586F94CD4BA1AF222BAB78661D960.F0CAC1EA4C932AC826D10A9E03B0BDB8" DestinationUUID="0B78382440B0D6AFA021B6B88CECA3AA.4172BDE54B39395C5A9BB59235D80362" />
                        <Connection Source="CUR_DATA_5.DATA" Destination="SEL_0.G" SourceUUID="31399F26488B1F99CBE71FBB9FBB9102.F0CAC1EA4C932AC826D10A9E03B0BDB8" DestinationUUID="2FC9F644418CC98511BB708170E30682.E51CF88C46776F33BF0D21B3F4741605" />
                        <Connection Source="CUR_DATA.DATA" Destination="NewEditor.i_value" SourceUUID="37AF725E4E137498119446B92E71D849.F0CAC1EA4C932AC826D10A9E03B0BDB8" DestinationUUID="C539C38748D2986E863313860C682DA8.B3C8AD45487F0C3EB832F3927CBB7484" />
                        <Connection Source="CUR_DATA_5.DATA" Destination="SEL.G" SourceUUID="31399F26488B1F99CBE71FBB9FBB9102.F0CAC1EA4C932AC826D10A9E03B0BDB8" DestinationUUID="6548903D48791D1B5E5A929276BB87EF.E51CF88C46776F33BF0D21B3F4741605" />
                        <Connection Source="CUR_DATA_3.DATA" Destination="NewString_0.i_value" SourceUUID="94B835884259ED81D90C1082B21E6916.F0CAC1EA4C932AC826D10A9E03B0BDB8" DestinationUUID="8466523D413E364A243AC1989728C916.B3C8AD45487F0C3EB832F3927CBB7484" />
                        <Connection Source="CUR_DATA_6.DATA" Destination="BASE64_DECODE.IN0" SourceUUID="1341120D41EF53D63BD3A38670277769.F0CAC1EA4C932AC826D10A9E03B0BDB8" DestinationUUID="E17AE5EE49BD95924F58D7932970B0EA.4172BDE54B39395C5A9BB59235D80362" />
                        <Connection Source="BASE64_DECODE.OUT" Destination="NewString_1.i_value" SourceUUID="E17AE5EE49BD95924F58D7932970B0EA.9C72057C42E48D0148694E9A088D5878" DestinationUUID="733C77A34F94DA65B027E2A76EDD4280.B3C8AD45487F0C3EB832F3927CBB7484" />
                        <Connection Source="SEL_0.OUT" Destination="SimpleText_1.text_color" SourceUUID="2FC9F644418CC98511BB708170E30682.D94D29B049B6DB4E0A29EA9CB5266805" DestinationUUID="8ADAEF3848ACF20C52DA11A48998C54D.06FF323D4ED2482B827E2BA3B99D3647" />
                        <Connection Source="BASE64_DECODE_1.OUT" Destination="NewString_3.i_value" SourceUUID="D42F95BC4936455027D3B78BF5219345.9C72057C42E48D0148694E9A088D5878" DestinationUUID="E19B46BC40D003AA6105019AF34C17F3.B3C8AD45487F0C3EB832F3927CBB7484" />
                        <Connection Source="CUR_DATA_2.DATA" Destination="NewString.i_value" SourceUUID="9AEBD2D74243204FF6AF8C8DFC3B9228.F0CAC1EA4C932AC826D10A9E03B0BDB8" DestinationUUID="7FD6637943895418379FF39C693DCA84.B3C8AD45487F0C3EB832F3927CBB7484" />
                        <Connection Source="NewString_1.o_value" Destination="BASE64_ENCODE.IN0" SourceUUID="733C77A34F94DA65B027E2A76EDD4280.28F406AE4E9179498A48A4A36A6F356C" DestinationUUID="C67D6C0046757DEF9B49B5894D053A9E.64FA25CF4845BF6FE251BB9EDAB15B36" dx1="10" dx2="138.75" dy="14.125" />
                        <Connection Source="NewString_2.o_value" Destination="BASE64_ENCODE_0.IN0" SourceUUID="C13E21564DCB13D19C2E59A725DB0E3C.28F406AE4E9179498A48A4A36A6F356C" DestinationUUID="842DE1BA48D73930B2E8EAA5709369D1.64FA25CF4845BF6FE251BB9EDAB15B36" dx1="10" dx2="541.25" dy="85.125" />
                        <Connection Source="BASE64_DECODE_0.OUT" Destination="NewString_2.i_value" SourceUUID="0B78382440B0D6AFA021B6B88CECA3AA.9C72057C42E48D0148694E9A088D5878" DestinationUUID="C13E21564DCB13D19C2E59A725DB0E3C.B3C8AD45487F0C3EB832F3927CBB7484" />
                        <Connection Source="CUR_DATA_1.DATA" Destination="NewEditor_1.i_value" SourceUUID="A2F89E8E46C3C7F9C6605D989001023E.F0CAC1EA4C932AC826D10A9E03B0BDB8" DestinationUUID="4F83059C4B4982A26A22BF927BC4D55C.B3C8AD45487F0C3EB832F3927CBB7484" />
                        <Connection Source="CUR_DATA_8.DATA" Destination="BASE64_DECODE_1.IN0" SourceUUID="94595B074F1FCF44DE8182862B692A29.F0CAC1EA4C932AC826D10A9E03B0BDB8" DestinationUUID="D42F95BC4936455027D3B78BF5219345.4172BDE54B39395C5A9BB59235D80362" />
                        <Connection Source="NewString_3.o_value" Destination="BASE64_ENCODE_1.IN0" SourceUUID="E19B46BC40D003AA6105019AF34C17F3.28F406AE4E9179498A48A4A36A6F356C" DestinationUUID="5F53ACD048EDFA9F951F4284AAB0BD59.64FA25CF4845BF6FE251BB9EDAB15B36" dx1="10" dx2="538.25" dy="2.125" />
                        <Connection Source="SEL.OUT" Destination="SimpleText_1.text" SourceUUID="6548903D48791D1B5E5A929276BB87EF.D94D29B049B6DB4E0A29EA9CB5266805" DestinationUUID="8ADAEF3848ACF20C52DA11A48998C54D.6197985F4F26DAD792BB4698C1EFE1AA" />
                        <Connection Source="::USER_NAME" Destination="SimpleText_0.text" SourceUUID="::363B8EF54CA4EB7E312A77A4997EF6E7" DestinationUUID="6DC013E8491C03FC0EEEEE94E8A6DA20.6197985F4F26DAD792BB4698C1EFE1AA" />
                        <Connection Source="CUR_DATA_0.DATA" Destination="NewEditor_0.i_value" SourceUUID="8E64834449D5D644FF2C8FBD893F27DB.F0CAC1EA4C932AC826D10A9E03B0BDB8" DestinationUUID="840BAD2343A348AD5F63F6B1F9967D6F.B3C8AD45487F0C3EB832F3927CBB7484" />
                        <Connection Source="CUR_DATA_4.DATA" Destination="SEL_1.G" SourceUUID="50D682B4445A1EA8D10793AC0AB2327F.F0CAC1EA4C932AC826D10A9E03B0BDB8" DestinationUUID="6AB31CA44FD36F2FDC0150AFF1A1EF4E.E51CF88C46776F33BF0D21B3F4741605" dx1="42.75" dx2="14" dy="93.625" />
                        <Connection Source="SEL_1.OUT" Destination="TLButton.color" SourceUUID="6AB31CA44FD36F2FDC0150AFF1A1EF4E.D94D29B049B6DB4E0A29EA9CB5266805" DestinationUUID="B53C83DE462C7A44A8193E9BF0189CFB.FC86BB724660D6AD0CA251B07BFAB891" dx1="10" dx2="83.5232" dy="2.29846" />
                        <Connection Source="BASE64_ENCODE_1.OUT" Destination="SET_SIGNAL_DATA.VALUE" SourceUUID="5F53ACD048EDFA9F951F4284AAB0BD59.8218898C4D95EE6BB82364B547537858" DestinationUUID="DE8A6193461B50767BC98FAAE76C44C4.2FB1E6714C1F6C26DB3A2C826BF999F2" dx1="10" dx2="177.75" dy="-0.25" />
                        <Connection Source="BASE64_ENCODE_0.OUT" Destination="SET_SIGNAL_DATA_0.VALUE" SourceUUID="842DE1BA48D73930B2E8EAA5709369D1.8218898C4D95EE6BB82364B547537858" DestinationUUID="81D8C81C44306FF50FB240A626F5B2FC.2FB1E6714C1F6C26DB3A2C826BF999F2" dx1="10" dx2="264.25" dy="-2.25" />
                        <Connection Source="E_SR.Q" Destination="SET_SIGNAL_DATA_1.VALUE" SourceUUID="A86B6BC34A20678F355C52939193945E.5758CA974978140FA5F3308319BA6292" DestinationUUID="5B568FD24EB79C5315BF3190247C586E.2FB1E6714C1F6C26DB3A2C826BF999F2" dx1="43" dx2="434.25" dy="0.625" />
                        <Connection Source="BASE64_ENCODE.OUT" Destination="SET_SIGNAL_DATA_2.VALUE" SourceUUID="C67D6C0046757DEF9B49B5894D053A9E.8218898C4D95EE6BB82364B547537858" DestinationUUID="BD80D70B41BA2EE2C3A78380BF372AEE.2FB1E6714C1F6C26DB3A2C826BF999F2" dx1="10" dx2="255.25" dy="-31.25" />
                        <Connection Source="::USER_NAME" Destination="SET_SIGNAL_DATA_4.VALUE" SourceUUID="::363B8EF54CA4EB7E312A77A4997EF6E7" DestinationUUID="88D358AF44081BC02B7A4E83CC300630.2FB1E6714C1F6C26DB3A2C826BF999F2" />
                        <Connection Source="NewEditor.o_value" Destination="SET_SIGNAL_DATA_5.VALUE" SourceUUID="C539C38748D2986E863313860C682DA8.28F406AE4E9179498A48A4A36A6F356C" DestinationUUID="D90E76284F59C342603F86B8C363DDB5.2FB1E6714C1F6C26DB3A2C826BF999F2" dx1="10" dx2="314.5" dy="16.875" />
                        <Connection Source="NewEditor_0.o_value" Destination="SET_SIGNAL_DATA_6.VALUE" SourceUUID="840BAD2343A348AD5F63F6B1F9967D6F.28F406AE4E9179498A48A4A36A6F356C" DestinationUUID="218D7E88469F1DAA7AC9B0A1418A4423.2FB1E6714C1F6C26DB3A2C826BF999F2" dx1="10" dx2="333" dy="8.875" />
                        <Connection Source="NewEditor_1.o_value" Destination="SET_SIGNAL_DATA_7.VALUE" SourceUUID="4F83059C4B4982A26A22BF927BC4D55C.28F406AE4E9179498A48A4A36A6F356C" DestinationUUID="99A1947E428FEBA71ABD5B9B55D35DA9.2FB1E6714C1F6C26DB3A2C826BF999F2" dx1="10" dx2="331.5" dy="-1.125" />
                        <Connection Source="NewString.o_value" Destination="SET_SIGNAL_DATA_8.VALUE" SourceUUID="7FD6637943895418379FF39C693DCA84.28F406AE4E9179498A48A4A36A6F356C" DestinationUUID="16BE351A44BB8B3DDDDEDD818DA43224.2FB1E6714C1F6C26DB3A2C826BF999F2" dx1="10" dx2="247" dy="16.875" />
                        <Connection Source="NewString_0.o_value" Destination="SET_SIGNAL_DATA_9.VALUE" SourceUUID="8466523D413E364A243AC1989728C916.28F406AE4E9179498A48A4A36A6F356C" DestinationUUID="AFF865BE46A90C4667611AA5BD8CDAB2.2FB1E6714C1F6C26DB3A2C826BF999F2" dx1="10" dx2="260.703" dy="-118.435" />
                        <Connection Source="E_SR.Q" Destination="B_Change.value" SourceUUID="A86B6BC34A20678F355C52939193945E.5758CA974978140FA5F3308319BA6292" DestinationUUID="CFA7668846A59EB7FC68D09A8CFCF98A.DD57BAF249D55A29F1FBA081C0E1CF30" dx1="188.75" dx2="10" dy="-16.125" />
                        <Connection Source="enabled" Destination="NewEditor.enabled" SourceUUID="15B097034B9BBE7CCD78E0A466A64239" DestinationUUID="C539C38748D2986E863313860C682DA8.15B097034B9BBE7CCD78E0A466A64239" />
                        <Connection Source="enabled" Destination="NewEditor_0.enabled" SourceUUID="15B097034B9BBE7CCD78E0A466A64239" DestinationUUID="840BAD2343A348AD5F63F6B1F9967D6F.15B097034B9BBE7CCD78E0A466A64239" />
                        <Connection Source="enabled" Destination="NewEditor_1.enabled" SourceUUID="15B097034B9BBE7CCD78E0A466A64239" DestinationUUID="4F83059C4B4982A26A22BF927BC4D55C.15B097034B9BBE7CCD78E0A466A64239" />
                        <Connection Source="enabled" Destination="NewString.enabled" SourceUUID="15B097034B9BBE7CCD78E0A466A64239" DestinationUUID="7FD6637943895418379FF39C693DCA84.15B097034B9BBE7CCD78E0A466A64239" />
                        <Connection Source="enabled" Destination="NewString_0.enabled" SourceUUID="15B097034B9BBE7CCD78E0A466A64239" DestinationUUID="8466523D413E364A243AC1989728C916.15B097034B9BBE7CCD78E0A466A64239" />
                        <Connection Source="enabled" Destination="NewString_1.enabled" SourceUUID="15B097034B9BBE7CCD78E0A466A64239" DestinationUUID="733C77A34F94DA65B027E2A76EDD4280.15B097034B9BBE7CCD78E0A466A64239" />
                        <Connection Source="enabled" Destination="NewString_2.enabled" SourceUUID="15B097034B9BBE7CCD78E0A466A64239" DestinationUUID="C13E21564DCB13D19C2E59A725DB0E3C.15B097034B9BBE7CCD78E0A466A64239" />
                        <Connection Source="enabled" Destination="NewString_3.enabled" SourceUUID="15B097034B9BBE7CCD78E0A466A64239" DestinationUUID="E19B46BC40D003AA6105019AF34C17F3.15B097034B9BBE7CCD78E0A466A64239" />
                        <Connection Source="enabled" Destination="TLButton_0.enabled" SourceUUID="15B097034B9BBE7CCD78E0A466A64239" DestinationUUID="4C720DBF443419D146E2D1BFC492A0A9.15B097034B9BBE7CCD78E0A466A64239" />
                        <Connection Source="enabled" Destination="TLButton.enabled" SourceUUID="15B097034B9BBE7CCD78E0A466A64239" DestinationUUID="B53C83DE462C7A44A8193E9BF0189CFB.15B097034B9BBE7CCD78E0A466A64239" />
                    </DataConnections>
                </FBNetwork>
            </SubWindowFBType>
        </Folder>
    """
    IS_addition = """
                <File Name="IS" UUID="TSZBAJRW4K6UBGKF2VINFIFPXA" Kind="png"><![CDATA[iVBORw0KGgoAAAANSUhEUgAAAL4AAADICAYAAABWD1tBAAAACXBIWXMAAC4jAAAuIwF4pT92AAAGb2lUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4gPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iQWRvYmUgWE1QIENvcmUgNS42LWMxNDIgNzkuMTYwOTI0LCAyMDE3LzA3LzEzLTAxOjA2OjM5ICAgICAgICAiPiA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPiA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtbG5zOnhtcE1NPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvbW0vIiB4bWxuczpzdEV2dD0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL3NUeXBlL1Jlc291cmNlRXZlbnQjIiB4bWxuczpwaG90b3Nob3A9Imh0dHA6Ly9ucy5hZG9iZS5jb20vcGhvdG9zaG9wLzEuMC8iIHhtbG5zOmRjPSJodHRwOi8vcHVybC5vcmcvZGMvZWxlbWVudHMvMS4xLyIgeG1wOkNyZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ0MgMjAxOCAoV2luZG93cykiIHhtcDpDcmVhdGVEYXRlPSIyMDE5LTA4LTE0VDE1OjUzOjI1KzAzOjAwIiB4bXA6TWV0YWRhdGFEYXRlPSIyMDE5LTA4LTE0VDE1OjUzOjI1KzAzOjAwIiB4bXA6TW9kaWZ5RGF0ZT0iMjAxOS0wOC0xNFQxNTo1MzoyNSswMzowMCIgeG1wTU06SW5zdGFuY2VJRD0ieG1wLmlpZDo1OTM2Y2ZhNC1lOGM1LWM3NDgtODI2My0zMmNhODk4YTE0NTIiIHhtcE1NOkRvY3VtZW50SUQ9ImFkb2JlOmRvY2lkOnBob3Rvc2hvcDo4MzNjYzBkNy0yNDUxLTM1NGQtODUxNi02ODkxNTIwOTk2MDciIHhtcE1NOk9yaWdpbmFsRG9jdW1lbnRJRD0ieG1wLmRpZDpmZDU0ZDE3My0wZDc2LWM1NDAtYjU0MC1lYjI5YTAxMzhkNzQiIHBob3Rvc2hvcDpDb2xvck1vZGU9IjMiIGRjOmZvcm1hdD0iaW1hZ2UvcG5nIj4gPHhtcE1NOkhpc3Rvcnk+IDxyZGY6U2VxPiA8cmRmOmxpIHN0RXZ0OmFjdGlvbj0iY3JlYXRlZCIgc3RFdnQ6aW5zdGFuY2VJRD0ieG1wLmlpZDpmZDU0ZDE3My0wZDc2LWM1NDAtYjU0MC1lYjI5YTAxMzhkNzQiIHN0RXZ0OndoZW49IjIwMTktMDgtMTRUMTU6NTM6MjUrMDM6MDAiIHN0RXZ0OnNvZnR3YXJlQWdlbnQ9IkFkb2JlIFBob3Rvc2hvcCBDQyAyMDE4IChXaW5kb3dzKSIvPiA8cmRmOmxpIHN0RXZ0OmFjdGlvbj0ic2F2ZWQiIHN0RXZ0Omluc3RhbmNlSUQ9InhtcC5paWQ6NTkzNmNmYTQtZThjNS1jNzQ4LTgyNjMtMzJjYTg5OGExNDUyIiBzdEV2dDp3aGVuPSIyMDE5LTA4LTE0VDE1OjUzOjI1KzAzOjAwIiBzdEV2dDpzb2Z0d2FyZUFnZW50PSJBZG9iZSBQaG90b3Nob3AgQ0MgMjAxOCAoV2luZG93cykiIHN0RXZ0OmNoYW5nZWQ9Ii8iLz4gPC9yZGY6U2VxPiA8L3htcE1NOkhpc3Rvcnk+IDxwaG90b3Nob3A6RG9jdW1lbnRBbmNlc3RvcnM+IDxyZGY6QmFnPiA8cmRmOmxpPmFkb2JlOmRvY2lkOnBob3Rvc2hvcDphZjY2ZmE2Ny1hZGI1LTEwNGQtYWUxMy1kMDVhNTVjYmY3NzE8L3JkZjpsaT4gPC9yZGY6QmFnPiA8L3Bob3Rvc2hvcDpEb2N1bWVudEFuY2VzdG9ycz4gPC9yZGY6RGVzY3JpcHRpb24+IDwvcmRmOlJERj4gPC94OnhtcG1ldGE+IDw/eHBhY2tldCBlbmQ9InIiPz7RhM7BAACitElEQVR4nOT9ebwlSXbfh30jMvPe++7b19r33nt69hkAQ0AAd1IkIEuUZdqSRZm2rA8pWR9bsmhbEm1QsizLJiRBH1E0P6IoUBspkZSohaQgkCBB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]]></File>
    """
    try:
        # Чтение содержимого файла
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.readlines()

        # Обновление содержимого файла
        updated_content = []
        for line in content:
            updated_content.append(line)
            if '<FBLibrary>' in line:
                updated_content.append(HMI_addition + '\n')
            if '<Folder Name="Ресурс"' in line:
                updated_content.append(IS_addition + '\n')
        
        # Запись обновленного содержимого в новый файл
        with open('result.iec_hmi', 'w', encoding='utf-8') as file:
            file.writelines(updated_content)

        print("Файл успешно обновлен.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")



def add_event_to_files(file_path, event_name):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.readlines()

        RegEventButton = """
                    <FB Name="IS2RegEventButton" Type="TIS2RegEventButton" TypeUUID="ZNZZ47LTYMZUNHA2UGTJLLMH7E" Enabled="true" UUID="WVWDMROK7HWUDJ2WFJRPSFBNGA" X="-1501.38179770448" Y="120.968912041041">
                        <VarValue Variable="M_Severity" Value="5" Type="INT" />
                        <VarValue Variable="NameButton" Value="&apos;Фильтр&apos;" Type="STRING" />
                    </FB>
                    <FB Name="IS2RegEventButton_5" Type="TIS2RegEventButton" TypeUUID="ZNZZ47LTYMZUNHA2UGTJLLMH7E" Enabled="true" UUID="TIRNUSD5OJYEZJ4YP227YLN7GY" X="-600.64666123907" Y="1180.47153478163">
                        <VarValue Variable="M_Severity" Value="5" Type="INT" />
                        <VarValue Variable="NameButton" Value="&apos;Квитировать все&apos;" Type="STRING" />
                    </FB>
                    <FB Name="IS2RegEventButton_2" Type="TIS2RegEventButton" TypeUUID="ZNZZ47LTYMZUNHA2UGTJLLMH7E" Enabled="true" UUID="T2XYXOALZNUE3JIA3TGRIZ6AQA" X="-769.4657670543" Y="496.476959637174">
                        <VarValue Variable="M_Severity" Value="5" Type="INT" />
                        <VarValue Variable="NameButton" Value="&apos;Квитировать&apos;" Type="STRING" />
                    </FB>
                    <FB Name="IS2RegEventButton_1" Type="TIS2RegEventButton" TypeUUID="ZNZZ47LTYMZUNHA2UGTJLLMH7E" Enabled="true" UUID="SZJXFVFUJVWEVHYZ64OGCPVVQY" X="-994.4657670543" Y="131.476959637174">
                        <VarValue Variable="M_Severity" Value="5" Type="INT" />
                        <VarValue Variable="NameButton" Value="&apos;Печать&apos;" Type="STRING" />
                    </FB>
                    <FB Name="IS2RegEventButton_3" Type="TIS2RegEventButton" TypeUUID="ZNZZ47LTYMZUNHA2UGTJLLMH7E" Enabled="true" UUID="7LYR4OMLQAFUVE4YJG5UQRJFFQ" X="-1265.76738195231" Y="1239.4656896405">
                        <VarValue Variable="M_Severity" Value="5" Type="INT" />
                        <VarValue Variable="NameButton" Value="&apos;Сохранить все&apos;" Type="STRING" />
                    </FB>
                    <FB Name="IS2RegEventButton_0" Type="TIS2RegEventButton" TypeUUID="ZNZZ47LTYMZUNHA2UGTJLLMH7E" Enabled="true" UUID="MFUXDMQCZCRUPEP4R2OXZCJJIU" X="-1318.86138942027" Y="669.301322992051">
                        <VarValue Variable="M_Severity" Value="5" Type="INT" />
                        <VarValue Variable="NameButton" Value="&apos;Сохранить&apos;" Type="STRING" />
                    </FB>
                    <FB Name="IS2RegEventButton_4" Type="TIS2RegEventButton" TypeUUID="ZNZZ47LTYMZUNHA2UGTJLLMH7E" Enabled="true" UUID="4DRQJXEUYT6ENJSW54NIF3NKQE" X="-935.64666123907" Y="853.471534781628">
                        <VarValue Variable="M_Severity" Value="5" Type="INT" />
                        <VarValue Variable="NameButton" Value="&apos;Печатать все&apos;" Type="STRING" />
                    </FB>
        """
        
        search_values = [
            "&apos;Квитировать&apos;",
            "&apos;Квитировать все&apos;",
            "&apos;Печатать все&apos;",
            "&apos;Фильтр&apos;",
            "&apos;Печать&apos;",
            "&apos;Сохранить все&apos;",
            "&apos;Сохранить&apos;"
        ]

        in_event_block = False
        in_fb_block = False
        in_event_connections = False
        in_data_connections = False
        current_fb_name = ""
        updated_content = []
        fb_source_uuids = {}
        data_connections_added = False
        event_connections_added = False

        fb_names_dict = {value: [] for value in search_values}

        for line in content:
            if f'<GraphicsCompositeFBType Name="{event_name}"' in line:
                in_event_block = True
            
            if in_event_block and '</GraphicsCompositeFBType>' in line:
                in_event_block = False

            if in_event_block and '<FB Name=' in line:
                in_fb_block = True
                match = re.search(r'Name="([^"]+)"', line)
                if match:
                    current_fb_name = match.group(1)

            if in_fb_block:
                for value in search_values:
                    if value in line:
                        fb_names_dict[value].append(current_fb_name)
                        break
                        
            if in_fb_block and '</FB>' in line:
                in_fb_block = False
                current_fb_name = ""

            if in_event_block and '<EventConnections>' in line:
                in_event_connections = True
                updated_content.append(RegEventButton)
            
            if in_event_connections and '<Connection' in line:
                source_match = re.search(r'Source="([^"]+)"', line)
                uuid_match = re.search(r'SourceUUID="([^"]+)\.', line)
                if source_match and uuid_match:
                    source_name = source_match.group(1).split('.')[0]
                    source_uuid = uuid_match.group(1)
                    fb_source_uuids[source_name] = source_uuid
            
            if in_event_connections and '</EventConnections>' in line:
                if not event_connections_added:
                    new_connections = []

                    for value, fb_names in fb_names_dict.items():
                        for fb_name in fb_names:
                            if fb_name in fb_source_uuids:
                                if value == "&apos;Фильтр&apos;":
                                    new_connections.append(f'                        <Connection Source="{fb_name}.mouseLBPress" Destination="IS2RegEventButton.Registrer" SourceUUID="{fb_source_uuids[fb_name]}.299295AF47A6CCAC26009C964C5B47C5" DestinationUUID="45366CB541EDF9CA622A56A7302D14F9.F4863EC2452A178A4460539D5B716C64" dx1="10" dx2="10" dy="-37" />\n')
                                elif value == "&apos;Квитировать&apos;":
                                    new_connections.append(f'                        <Connection Source="{fb_name}.mouseLBPress" Destination="IS2RegEventButton_2.Registrer" SourceUUID="{fb_source_uuids[fb_name]}.299295AF47A6CCAC26009C964C5B47C5" DestinationUUID="B88BAF9E4D68CB0BCDDC00A580C06714.F4863EC2452A178A4460539D5B716C64" dx1="106" dx2="10" dy="106" />\n')
                                elif value == "&apos;Квитировать все&apos;":
                                    new_connections.append(f'                        <Connection Source="{fb_name}.mouseLBPress" Destination="IS2RegEventButton_5.Registrer" SourceUUID="{fb_source_uuids[fb_name]}.299295AF47A6CCAC26009C964C5B47C5" DestinationUUID="48DA229A4C70727DB57E98A736BF2DFC.F4863EC2452A178A4460539D5B716C64" dx1="172" dx2="10" dy="191" />\n')
                                elif value == "&apos;Печатать все&apos;":
                                    new_connections.append(f'                        <Connection Source="{fb_name}.mouseLBPress" Destination="IS2RegEventButton_4.Registrer" SourceUUID="{fb_source_uuids[fb_name]}.299295AF47A6CCAC26009C964C5B47C5" DestinationUUID="DC04E3E046FCC4941AEF56A681AAED82.F4863EC2452A178A4460539D5B716C64" dx1="0" dx2="0" dy="39" />\n')
                                elif value == "&apos;Печать&apos;":
                                    new_connections.append(f'                        <Connection Source="{fb_name}.mouseLBPress" Destination="IS2RegEventButton_1.Registrer" SourceUUID="{fb_source_uuids[fb_name]}.299295AF47A6CCAC26009C964C5B47C5" DestinationUUID="D47253964A6C4DB41CF7199F86B53E61.F4863EC2452A178A4460539D5B716C64" dx1="0" dx2="0" dy="0" />\n')
                                elif value == "&apos;Сохранить все&apos;":
                                    new_connections.append(f'                        <Connection Source="{fb_name}.mouseLBPress" Destination="IS2RegEventButton_3.Registrer" SourceUUID="{fb_source_uuids[fb_name]}.299295AF47A6CCAC26009C964C5B47C5" DestinationUUID="391EF1FA4A0B808BBB4998932C254548.F4863EC2452A178A4460539D5B716C64" dx1="0" dx2="0" dy="0" />\n')
                                elif value == "&apos;Сохранить&apos;":
                                    new_connections.append(f'                        <Connection Source="{fb_name}.mouseLBPress" Destination="IS2RegEventButton_0.Registrer" SourceUUID="{fb_source_uuids[fb_name]}.299295AF47A6CCAC26009C964C5B47C5" DestinationUUID="B271696147A3C8029D8EFC914529897C.F4863EC2452A178A4460539D5B716C64" dx1="0" dx2="0" dy="0" />\n')

                    updated_content.extend(new_connections)
                    event_connections_added = True

                in_event_connections = False

            if in_event_block and '<DataConnections>' in line:
                in_data_connections = True
            
            if in_data_connections and '</DataConnections>' in line:
                if not data_connections_added:
                    new_connections = []

                    for value, fb_names in fb_names_dict.items():
                        for fb_name in fb_names:
                            if fb_name in fb_source_uuids:
                                if value == "&apos;Фильтр&apos;":
                                    new_connections.append(f'                        <Connection Source="::R_CfgEvViewer" Destination="{fb_name}.enabled" SourceUUID="::FECBBF4B450CEF8931F4AC8D85059C74" DestinationUUID="{fb_source_uuids[fb_name]}.15B097034B9BBE7CCD78E0A466A64239" />\n')
                                elif value == "&apos;Квитировать&apos;" or value == "&apos;Квитировать все&apos;":
                                    new_connections.append(f'                        <Connection Source="::R_QuitAlarm" Destination="{fb_name}.enabled" SourceUUID="::034021C04AE0477941182098F6475ED1" DestinationUUID="{fb_source_uuids[fb_name]}.15B097034B9BBE7CCD78E0A466A64239" />\n')
                                elif value == "&apos;Печатать все&apos;" or value == "&apos;Печать&apos;" or value == "&apos;Сохранить все&apos;" or value == "&apos;Сохранить&apos;":
                                    new_connections.append(f'                        <Connection Source="::R_Print" Destination="{fb_name}.enabled" SourceUUID="::CE3F4CAA4D3C816EBF47309CCBF6CA40" DestinationUUID="{fb_source_uuids[fb_name]}.15B097034B9BBE7CCD78E0A466A64239" />\n')

                    updated_content.extend(new_connections)
                    data_connections_added = True

                in_data_connections = False

            if in_event_block and '</FBNetwork>' in line and not data_connections_added:
                data_connections_content = []

                for value, fb_names in fb_names_dict.items():
                    for fb_name in fb_names:
                        if fb_name in fb_source_uuids:
                            if value == "&apos;Фильтр&apos;":
                                data_connections_content.append(f'                        <Connection Source="::R_CfgEvViewer" Destination="{fb_name}.enabled" SourceUUID="::FECBBF4B450CEF8931F4AC8D85059C74" DestinationUUID="{fb_source_uuids[fb_name]}.15B097034B9BBE7CCD78E0A466A64239" />\n')
                            elif value == "&apos;Квитировать&apos;" or value == "&apos;Квитировать все&apos;":
                                data_connections_content.append(f'                        <Connection Source="::R_QuitAlarm" Destination="{fb_name}.enabled" SourceUUID="::034021C04AE0477941182098F6475ED1" DestinationUUID="{fb_source_uuids[fb_name]}.15B097034B9BBE7CCD78E0A466A64239" />\n')
                            elif value == "&apos;Печатать все&apos;" or value == "&apos;Печать&apos;" or value == "&apos;Сохранить все&apos;" or value == "&apos;Сохранить&apos;":
                                data_connections_content.append(f'                        <Connection Source="::R_Print" Destination="{fb_name}.enabled" SourceUUID="::CE3F4CAA4D3C816EBF47309CCBF6CA40" DestinationUUID="{fb_source_uuids[fb_name]}.15B097034B9BBE7CCD78E0A466A64239" />\n')

                if data_connections_content:
                    updated_content.append('                    <DataConnections>\n')
                    updated_content.extend(data_connections_content)
                    updated_content.append('                    </DataConnections>\n')

                updated_content.append(line)
                data_connections_added = True
                continue

            updated_content.append(line)

        with open('result.iec_hmi', 'w', encoding='utf-8') as file:
            file.writelines(updated_content)

        print(f'Файл {file_path} успешно обработан и сохранен как result.iec_hmi.')

    except FileNotFoundError:
        print(f'Ошибка: Файл {file_path} не найден.')



#ГЕНЕРАЦИЯ UUID, И ПРОВЕРКА НА УНИКАЛЬНОСТЬ (ТОКА ХУЛИ ДЕЛАТЬ С AT_SettingsPgSQL)
#def generate_uuid(existing_uuids):
#    while True:
#        new_uuid = uuid.uuid4().hex.upper()[:26]
#        if new_uuid not in existing_uuids:
#            return new_uuid
#
#def extract_uuids(content):
#    return set(re.findall(r'UUID="([A-Z0-9]{26})"', content))
#
#def add_variables_to_files(prj_file, mnemo_file, event_logger_file):
#    signals = [
#        ('countEvents', 'REAL', 'TRUE', 'persistent', 'ИБ: Количество событий, хранящихся в пределах одной базы данных'),
#        ('countWarningEvents', 'REAL', 'TRUE', 'persistent', 'ИБ: Количество событий, при которых будут выдаваться предупредительные события'),
#        ('timePeriod', 'REAL', 'TRUE', 'persistent', 'ИБ: Период выдачи событий о переполнении'),
#        ('dir', 'STRING', 'TRUE', 'persistent', 'ИБ: Путь для сохранения выгрузки базы данных в CSV при переполнении'),
#        ('nameFile', 'STRING', 'TRUE', 'persistent', 'ИБ: Имя файла данных ИБ CSV'),
#        ('nameUser', 'STRING', 'TRUE', 'persistent', 'ИБ: Имя пользователя от имени, которого будут формироваться служебные события'),
#        ('save', 'BOOL', 'TRUE', None, 'ИБ: Флаг записи настроек БД в энергонезависимую память'),
#        ('connectBD', 'BOOL', 'TRUE', 'persistent', 'ИБ: Флаг соединения с БД после ввода имени пользователя, пароля, имени БД'),
#        ('userBD', 'STRING', 'TRUE', 'persistent', 'ИБ: Имя пользователя БД (зашифрованное)'),
#        ('passBD', 'STRING', 'TRUE', 'persistent', 'ИБ: Пароль пользователя БД (зашифрованный)'),
#        ('nameBD', 'STRING', 'TRUE', 'persistent', 'ИБ: Имя БД (зашифрованное)'),
#        ('connectedBD', 'BOOL', 'TRUE', None, 'ИБ: Флаг наличия связи с БД'),
#        ('DumpBD', 'BOOL', 'TRUE', None, 'ИБ: Флаг принудительной записи данных в csv файл'),
#    ]
#    
#    # Signals specific to mnemo and event_logger files
#    mnemo_specific_signals = [
#        ('ThisNode', 'STRING', '', None, None),
#        ('R_Control', 'BOOL', '', None, None),
#        ('R_SetPoint', 'BOOL', '', None, None),
#        ('R_Print', 'BOOL', '', None, None),
#        ('R_ViewArj', 'BOOL', '', None, None),
#        ('R_QuitAlarm', 'BOOL', '', None, None),
#        ('R_CfgEvViewer', 'BOOL', '', None, None),
#        ('R_Simulate', 'BOOL', '', None, None),
#    ]
#    
#    try:
#        # Read files content
#        with open(prj_file, 'r', encoding='utf-8') as f:
#            prj_content = f.read()
#        with open(mnemo_file, 'r', encoding='utf-8') as f:
#            mnemo_content = f.read()
#        with open(event_logger_file, 'r', encoding='utf-8') as f:
#            event_logger_content = f.read()
#        
#        # Extract existing UUIDs
#        existing_uuids = extract_uuids(prj_content) | extract_uuids(mnemo_content) | extract_uuids(event_logger_content)
#        
#        # Create a dictionary to store UUIDs for each signal
#        signal_uuids = {}
#        
#        # Generate UUIDs for signals
#        for name, signal_type, global_flag, storage, comment in signals:
#            signal_uuids[name] = generate_uuid(existing_uuids)
#            existing_uuids.add(signal_uuids[name])
#        
#        def create_signal_block(signals):
#            block = ""
#            for name, signal_type, global_flag, storage, comment in signals:
#                new_uuid = signal_uuids.get(name, generate_uuid(existing_uuids))
#                block += f'\t\t<Signal Name="{name}" UUID="{new_uuid}" Type="{signal_type}"'
#                if global_flag:
#                    block += f' Global="{global_flag}"'
#                if storage:
#                    block += f' Storage="{storage}"'
#                if comment:
#                    block += f' Comment="{comment}"'
#                block += ' />\n'
#            return block
#        
#        prj_addition = create_signal_block(signals)
#        mnemo_addition = create_signal_block(signals + mnemo_specific_signals)
#        event_logger_addition = create_signal_block([s for s in signals if s[0] in {'connectBD', 'userBD', 'passBD', 'nameBD'}])
#
#        # Replace content in files
#        prj_content = prj_content.replace('</Globals>', prj_addition + '</Globals>')
#        mnemo_content = mnemo_content.replace('</InterfaceList>', mnemo_addition + '</InterfaceList>')
#        event_logger_content = event_logger_content.replace('</InterfaceList>', event_logger_addition + '</InterfaceList>')
#
#        # Write back modified content
#        with open(prj_file, 'w', encoding='utf-8') as f:
#            f.write(prj_content)
#        with open(mnemo_file, 'w', encoding='utf-8') as f:
#            f.write(mnemo_content)
#        with open(event_logger_file, 'w', encoding='utf-8') as f:
#            f.write(event_logger_content)
#
#    except Exception as e:
#        print(f"Error adding variables to files: {e}")
#