import re
import shutil
import os

def execute_ib_command(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Найти все вхождения <FB Name="AlarmViewer\d+" Type="TAlarmViewer" TypeUUID="[^"]+".*?<Palette>...</Palette> и извлечь их содержимое
        alarm_palettes = re.findall(r'<FB Name="AlarmViewer\d+" Type="TAlarmViewer" TypeUUID="[^"]+".*?<Palette>(.*?)</Palette>', content, re.DOTALL)
        
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