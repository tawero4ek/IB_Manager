from tkinter import filedialog
import tkinter as tk
import customtkinter as ctk
import finder
from core import main_core


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("IEC HMI Tool")
        self.geometry("1200x700")

        self.selected_files = {'iec_hmi': None, 'graphics': None, 'subwindow': None}

        # Top navigation bar
        self.navbar_frame = ctk.CTkFrame(self)
        self.navbar_frame.pack(fill="x")

        self.iec_manager_button = ctk.CTkButton(self.navbar_frame, text="IEC Manager", command=self.show_iec_manager,font=("TimesNewRoman", 17), width=150, height=40)
        self.iec_manager_button.grid(row=0, column=0, padx=10, pady=20)

        self.search_button = ctk.CTkButton(self.navbar_frame, text="Поиск", command=self.show_search,font=("TimesNewRoman", 17), width=150, height=40)
        self.search_button.grid(row=0, column=1, padx=10, pady=20)

        self.users_button = ctk.CTkButton(self.navbar_frame, text="Инфо", command=self.show_users,font=("TimesNewRoman", 17), width=150, height=40)
        self.users_button.grid(row=0, column=2, padx=10, pady=20)

        self.navbar_frame.grid_columnconfigure(0, weight=1)
        self.navbar_frame.grid_columnconfigure(1, weight=1)
        self.navbar_frame.grid_columnconfigure(2, weight=1)

        # Main container for different frames
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (IECManagerFrame, SearchFrame, UsersFrame):
            page_name = F.__name__
            frame = F(parent=self.main_container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        self.show_frame("IECManagerFrame")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def show_iec_manager(self):
        self.show_frame("IECManagerFrame")

    def show_search(self):
        self.show_frame("SearchFrame")

    def show_users(self):
        self.show_frame("UsersFrame")


class IECManagerFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Окно выбора файла .iec_hmi
        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.pack(pady=(20, 5), padx=50, fill="x")

        self.file_label = ctk.CTkLabel(self.file_frame, text="Выберите файл .iec_hmi:", font=("TimesNewRoman", 17))
        self.file_label.grid(row=0, column=0, padx=(10, 10), sticky="w")

        self.file_button = ctk.CTkButton(self.file_frame, text="Выбрать файл",
                                         command=lambda: self.select_file('iec_hmi'),font=("TimesNewRoman", 15), width=200, height=50)
        self.file_button.grid(row=0, column=1, sticky="e")

        self.file_frame.grid_columnconfigure(1, weight=1)

        # Окно выбора файла GraphicsCompositeType.txt
        self.graphics_frame = ctk.CTkFrame(self)
        self.graphics_frame.pack(pady=(10, 5), padx=50, fill="x")

        self.graphics_label = ctk.CTkLabel(self.graphics_frame, text="Выберите файл GraphicsCompositeType.txt:",
                                           font=("TimesNewRoman", 17))
        self.graphics_label.grid(row=0, column=0, padx=(10, 10), sticky="w")

        self.graphics_button = ctk.CTkButton(self.graphics_frame, text="Выбрать файл",
                                             command=lambda: self.select_file('graphics'),font=("TimesNewRoman", 15), width=200, height=50)
        self.graphics_button.grid(row=0, column=1, sticky="e")

        self.graphics_frame.grid_columnconfigure(1, weight=1)

        # Окно выбора файла TSubWindowType.txt
        self.subwindow_frame = ctk.CTkFrame(self)
        self.subwindow_frame.pack(pady=(10, 5), padx=50, fill="x")

        self.subwindow_label = ctk.CTkLabel(self.subwindow_frame, text="Выберите файл TSubWindowType.txt:",
                                            font=("TimesNewRoman", 16))
        self.subwindow_label.grid(row=0, column=0, padx=(10, 10), sticky="w")

        self.subwindow_button = ctk.CTkButton(self.subwindow_frame, text="Выбрать файл",
                                              command=lambda: self.select_file('subwindow'),font=("TimesNewRoman", 15), width=200, height=50)
        self.subwindow_button.grid(row=0, column=1, sticky="e")

        self.subwindow_frame.grid_columnconfigure(1, weight=1)

        # Окно с сообщениями
        self.message_label = ctk.CTkLabel(self, text="Сообщения:", font=("TimesNewRoman", 15), anchor="w")
        self.message_label.pack(pady=(10, 5), padx=50, anchor="w")

        self.error_text = ctk.CTkTextbox(self, height=5, wrap="word")
        self.error_text.pack(fill="both", expand=True, padx=50)

        # Кнопки
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(padx=50, pady=(20), fill="x")

        self.process_button = ctk.CTkButton(self.button_frame, text="Изменить все окна",
                                            command=self.run_main,font=("TimesNewRoman", 15), width=300, height=50)
        self.process_button.pack(anchor="w", side="left", padx=(0, 10), expand=True)

        self.graphics_button = ctk.CTkButton(self.button_frame, text="Изменить только на GraphicsComposite",
                                             command=self.run_with_graphics,font=("TimesNewRoman", 15), width=300, height=50)
        self.graphics_button.pack(anchor="center", side="left", padx=(0, 10), expand=True)

        self.subwindow_button = ctk.CTkButton(self.button_frame, text="Изменить только на SubWindow",
                                              command=self.run_with_subwindow,font=("TimesNewRoman", 15), width=300, height=50)
        self.subwindow_button.pack(anchor="e", side="left", expand=True)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def select_file(self, file_type):
        file_types = [("IEC_HMI files", "*.iec_hmi")] if file_type == 'iec_hmi' else [("Text files", "*.txt")]
        selected_file = filedialog.askopenfilename(filetypes=file_types)
        if selected_file:
            self.controller.selected_files[file_type] = selected_file
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
        if self.controller.selected_files['iec_hmi']:
            if not self.controller.selected_files['graphics']:
                self.error_text.insert("end", "\n\n   Файл с расширением GraphicsCompositeType.txt не выбран")
                return
            if not self.controller.selected_files['subwindow']:
                self.error_text.insert("end", "\n\n   Файл с расширением TSubWindowType.txt не выбран")
                return

            command = [
                self.controller.selected_files['iec_hmi'],
                '--graphics', self.controller.selected_files['graphics'],
                '--subwindow', self.controller.selected_files['subwindow']
            ]
            main_core(command)  # Вызов функции main_core

            self.error_text.insert("end",
                                   "\n\n   Изменение всех окон завершено, результат сохранен в файл result.iec_hmi")
        else:
            self.error_text.insert("end", "\n\n   Файл с расширением .iec_hmi не выбран")

    def run_with_graphics(self):
        if self.controller.selected_files['iec_hmi'] and self.controller.selected_files['graphics']:
            command = [
                self.controller.selected_files['iec_hmi'],
                '--graphics', self.controller.selected_files['graphics']
            ]
            main_core(command)  # Вызов функции main_core
            self.error_text.insert("end",
                                   "\n\n   Изменение окон на GraphicsComposite завершено,"
                                   " результат сохранен в файл result.iec_hmi")
        else:
            self.error_text.insert("end", "\n\n   Файл с расширением .iec_hmi или GraphicsCompositeType.txt не выбран")

    def run_with_subwindow(self):
        if self.controller.selected_files['iec_hmi'] and self.controller.selected_files['subwindow']:
            command = [
                self.controller.selected_files['iec_hmi'],
                '--subwindow', self.controller.selected_files['subwindow']
            ]
            main_core(command)  # Вызов функции main_core
            self.error_text.insert("end",
                                   "\n\n   Изменение окон на SubWindow завершено,"
                                   " результат сохранен в файл result.iec_hmi")
        else:
            self.error_text.insert("end", "\n\n   Файл с расширением .iec_hmi или TSubWindowType.txt не выбран")


class SearchFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Основной фрейм для кнопок
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=20)

        # Кнопка поиска строк hid to hide
        self.find_hid_to_hide_button = ctk.CTkButton(button_frame, text="Найти все hid to hide",
                                                     command=self.find_hid_to_hide, font=("TimesNewRoman", 15), width=300, height=50)
        self.find_hid_to_hide_button.pack(side=tk.LEFT, padx=(0, 40))

        # Кнопка поиска использования выбранных окон
        self.find_window_usage_button = ctk.CTkButton(button_frame, text="Найти использование окон",
                                                      command=self.find_window_usage, font=("TimesNewRoman", 15), width=300, height=50)
        self.find_window_usage_button.pack(side=tk.LEFT, padx=(40, 0))

        # Окно с сообщениями
        self.message_label = ctk.CTkLabel(self, text="Сообщения:", font=("TimesNewRoman", 17), anchor="w")
        self.message_label.pack(pady=(10, 5), padx=50, anchor="w")

        self.error_text = ctk.CTkTextbox(self, height=5, wrap="word", font=("TimesNewRoman", 15))
        self.error_text.pack(fill="both", expand=True, pady=(0, 50), padx=50)
        # Убрана установка Textbox в "disabled", чтобы текст можно было копировать

    def select_iec_hmi_file(self):
        file_types = [("IEC_HMI files", "*.iec_hmi")]
        selected_file = filedialog.askopenfilename(filetypes=file_types)
        if selected_file:
            # Обработка выбора файла .iec_hmi
            self.controller.selected_files['iec_hmi'] = selected_file
            self.select_iec_hmi_label.configure(text=f"Выбран файл: {selected_file}")

    def find_hid_to_hide(self):
        if not self.controller.selected_files['iec_hmi']:
            # Handle case where no .iec_hmi file is selected
            self.error_text.delete(1.0, tk.END)
            self.error_text.insert(tk.END, "Выберите файл .iec_hmi сначала.")
            return
        
        iec_hmi_file = self.controller.selected_files['iec_hmi']
        matches = finder.find_hid_to_hide(iec_hmi_file)
        
        if matches:
            # Очистка текстового поля перед выводом новых сообщений
            self.error_text.delete(1.0, tk.END)
            
            # Вывод найденных строк в текстовое поле
            self.error_text.insert(tk.END, "Найдены следующие строки:\n")
            for match in matches:
                self.error_text.insert(tk.END, f"{match}\n")
        else:
            self.error_text.delete(1.0, tk.END)
            self.error_text.insert(tk.END, "Не найдено совпадений.")

    def find_window_usage(self):
        if not self.controller.selected_files['iec_hmi']:
            # Handle case where no .iec_hmi file is selected
            self.error_text.delete(1.0, tk.END)
            self.error_text.insert(tk.END, "Выберите файл .iec_hmi сначала.")
            return
        
        iec_hmi_file = self.controller.selected_files['iec_hmi']
        graphics_label_file = self.controller.selected_files['graphics']
        subwindow_label_file = self.controller.selected_files['subwindow']
        matches = finder.find_window_usage(iec_hmi_file, graphics_label_file, subwindow_label_file)
        
        if matches:
            # Очистка текстового поля перед выводом новых сообщений
            self.error_text.delete(1.0, tk.END)
            
            # Вывод найденных строк в текстовое поле
            self.error_text.insert(tk.END, "Найдено использование окон:\n")
            for match in matches:
                self.error_text.insert(tk.END, f"{match}\n")
        else:
            self.error_text.delete(1.0, tk.END)
            self.error_text.insert(tk.END, "Не найдено использование окон.")

class UsersFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Создание текстового виджета с CustomTkinter
        self.text_widget = ctk.CTkTextbox(self, height=5, wrap="word", font=("TimesNewRoman", 17))
        self.text_widget.pack(pady=(20, 50), padx=50, anchor="w", fill="both", expand=True)

        # Добавление текста в виджет
        self.text_widget.insert("1.0", "\nМодная разработка Яцышина и Чепусова\n")
        self.text_widget.insert("end", "\nИнструкция с полным описание работы программы находиться в файле IB_Manager.docx\n")
        self.text_widget.insert("end", "\nВсе вопросы/предложения/сообщения об ошибках - yatsyshin@vega-gaz.ru\n")

        # Отключение редактирования текста
        self.text_widget.configure(state="disabled")

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = App()
    app.mainloop()
