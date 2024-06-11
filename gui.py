import os
import sys
import subprocess
import customtkinter as ctk
from tkinter import filedialog




class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("IEC HMI Tool")
        self.geometry("1200x600")

        self.selected_files = {'iec_hmi': None, 'graphics': None, 'subwindow': None}

        # Окно выбора файла .iec_hmi
        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.pack(pady=(20, 5), padx=50, fill="x")

        self.file_label = ctk.CTkLabel(self.file_frame, text="Выберите файл .iec_hmi:", font=("TimesNewRoman", 16))
        self.file_label.grid(row=0, column=0, padx=(10, 10), sticky="w")

        self.file_button = ctk.CTkButton(self.file_frame, text="Выбрать файл", command=lambda: self.select_file('iec_hmi'), width=200, height=50)
        self.file_button.grid(row=0, column=1, sticky="e")

        self.file_frame.grid_columnconfigure(1, weight=1)

        # Окно выбора файла GraphicsCompositeType.txt
        self.graphics_frame = ctk.CTkFrame(self)
        self.graphics_frame.pack(pady=(10, 5), padx=50, fill="x")

        self.graphics_label = ctk.CTkLabel(self.graphics_frame, text="Выберите файл GraphicsCompositeType.txt:", font=("TimesNewRoman", 16))
        self.graphics_label.grid(row=0, column=0, padx=(10, 10), sticky="w")

        self.graphics_button = ctk.CTkButton(self.graphics_frame, text="Выбрать файл", command=lambda: self.select_file('graphics'), width=200, height=50)
        self.graphics_button.grid(row=0, column=1, sticky="e")

        self.graphics_frame.grid_columnconfigure(1, weight=1)

        # Окно выбора файла TSubWindowType.txt
        self.subwindow_frame = ctk.CTkFrame(self)
        self.subwindow_frame.pack(pady=(10, 5), padx=50, fill="x")

        self.subwindow_label = ctk.CTkLabel(self.subwindow_frame, text="Выберите файл TSubWindowType.txt:", font=("TimesNewRoman", 16))
        self.subwindow_label.grid(row=0, column=0, padx=(10, 10), sticky="w")

        self.subwindow_button = ctk.CTkButton(self.subwindow_frame, text="Выбрать файл", command=lambda: self.select_file('subwindow'), width=200, height=50)
        self.subwindow_button.grid(row=0, column=1, sticky="e")

        self.subwindow_frame.grid_columnconfigure(1, weight=1)

        # Окно с сообщениями
        self.message_label = ctk.CTkLabel(self, text="Сообщения:", font=("TimesNewRoman", 16), anchor="w")
        self.message_label.pack(pady=(10, 5), padx=50, anchor="w")

        self.error_text = ctk.CTkTextbox(self, height=5, wrap="word")
        self.error_text.pack(fill="both", expand=True, padx=50)

        # Кнопки
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(padx=50, pady=10, fill="x")

        self.process_button = ctk.CTkButton(self.button_frame, text="Изменить все окна", command=self.run_main, width=300, height=50)
        self.process_button.pack(side="left", padx=(0, 10), expand=True)

        self.graphics_button = ctk.CTkButton(self.button_frame, text="Изменить только на GraphicsComposite", command=self.run_with_graphics, width=300, height=50)
        self.graphics_button.pack(side="left", padx=(0, 10), expand=True)

        self.subwindow_button = ctk.CTkButton(self.button_frame, text="Изменить только на SubWindow", command=self.run_with_subwindow, width=300, height=50)
        self.subwindow_button.pack(side="left", expand=True)

    def select_file(self, file_type):
        file_types = [("IEC_HMI files", "*.iec_hmi")] if file_type == 'iec_hmi' else [("Text files", "*.txt")]
        selected_file = filedialog.askopenfilename(filetypes=file_types)
        if selected_file:
            self.selected_files[file_type] = selected_file
            if file_type == 'iec_hmi':
                self.file_label.configure(text=f"Выбран файл: {selected_file}")
            elif file_type == 'graphics':
                self.graphics_label.configure(text=f"Выбран файл: {selected_file}")
            elif file_type == 'subwindow':
                self.subwindow_label.configure(text=f"Выбран файл: {selected_file}")
        else:
            if file_type == 'iec_hmi':
                self.file_label.configure(text="Выберите файл .iec_hmi:")
            elif file_type == 'graphics':
                self.graphics_label.configure(text="Выберите файл GraphicsCompositeType.txt:")
            elif file_type == 'subwindow':
                self.subwindow_label.configure(text="Выберите файл TSubWindowType.txt:")

    def run_main(self):
        if self.selected_files['iec_hmi']:
            if not self.selected_files['graphics']:
                self.error_text.insert("end", "\n\n   Файл с расширением GraphicsCompositeType.txt не выбран")
                return
            if not self.selected_files['subwindow']:
                self.error_text.insert("end", "\n\n   Файл с расширением TSubWindowType.txt не выбран")
                return
    
            main_py = os.path.join(os.path.dirname(sys.argv[0]), "main.py")
            command = [
                sys.executable,
                main_py,
                self.selected_files['iec_hmi'],
                '--graphics', self.selected_files['graphics'],
                '--subwindow', self.selected_files['subwindow']
            ]
    
            self.execute_command(command)
            self.error_text.insert("end", "\n\n   Изменение всех окон завершено, результат сохранен в файл result.iec_hmi")
        else:
            self.error_text.insert("end", "\n\n   Файл с расширением .iec_hmi не выбран")


    def run_with_graphics(self):
        if self.selected_files['iec_hmi'] and self.selected_files['graphics']:
            main_py = os.path.join(os.path            .dirname(sys.argv[0]), "main.py")
            command = [
                sys.executable,
                main_py,
                self.selected_files['iec_hmi'],
                '--graphics', self.selected_files['graphics']
            ]
            self.execute_command(command)
            self.error_text.insert("end", "\n\n   Изменение окон на GraphicsComposite завершено, результат сохранен в файл result.iec_hmi")
        else:
            self.error_text.insert("end", "\n\n   Файл с расширением .iec_hmi или GraphicsCompositeType.txt не выбран")

    def run_with_subwindow(self):
        if self.selected_files['iec_hmi'] and self.selected_files['subwindow']:
            main_py = os.path.join(os.path.dirname(sys.argv[0]), "main.py")
            command = [
                sys.executable,
                main_py,
                self.selected_files['iec_hmi'],
                '--subwindow', self.selected_files['subwindow']
            ]
            self.execute_command(command)
            self.error_text.insert("end", "\n\n   Изменение окон на SubWindow завершено, результат сохранен в файл result.iec_hmi")
        else:
            self.error_text.insert("end", "\n\n   Файл с расширением .iec_hmi или TSubWindowType.txt не выбран")

    def execute_command(self, command):
        try:
            working_directory = os.path.dirname(os.path.abspath(__file__))
            os.chdir(working_directory)
            result = subprocess.run(command, capture_output=True, text=True)
            print("Executing command:", ' '.join(command))

            self.error_text.delete("1.0", "end")
            if result.returncode == 0:
                self.error_text.insert("end", "Команда успешно выполнена.")
            else:
                self.error_text.insert("end", f"Команда выполнена с ошибкой. Код завершения: {result.returncode}")
        except Exception as e:
            self.error_text.delete("1.0", "end")
            self.error_text.insert("end", f"Ошибка выполнения команды:\n{str(e)}")



    def python_path(self):
        return sys.executable

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = App()
    app.mainloop()

