import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk
import pyperclip

import finder
from changer import (
    add_event_to_files,
    add_files_to_design,
    add_HMI_to_files,
    change_font_in_file,
    execute_ib_command,
)
from core import main_core
from defender import get_allowed_computer_name, isRun

# Настройка конфигурации для шрифтов
computer_fonts = {
    "SPB-CHEPUSOV1": ("Arial", 15),
    "SPB-DENISENKO": ("Verdana", 15),
    "SPB-MYLOV": ("Calibri", 15),
    "SPB-SHEGLOV": ("Georgia", 15),
    "SPB-VERSHININ": ("Lucida Sans", 15),
    "SPB-ERSHOV": ("Trebuchet MS", 15),
    "SPB-NIKITIN": ("Courier New", 15),
    "SPB-VASILIEV": ("Tahoma", 15),
    "SPB-SERGEY": ("Times New Roman", 15),
}


def get_font():
    current_computer_name = get_allowed_computer_name()
    return computer_fonts.get(current_computer_name)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        font = get_font()

        self.title("IB Manager")
        self.geometry("1200x700")

        self.selected_files = {"iec_hmi": None, "graphics": None, "subwindow": None}

        # Top navigation bar
        self.navbar_frame = ctk.CTkFrame(self)
        self.navbar_frame.pack(fill="x")

        self.iec_manager_button = ctk.CTkButton(
            self.navbar_frame,
            text="Перевод",
            command=self.show_iec_manager,
            font=font,
            width=150,
            height=40,
        )
        self.iec_manager_button.grid(row=0, column=0, padx=10, pady=20)

        self.search_button = ctk.CTkButton(
            self.navbar_frame,
            text="Поиск",
            command=self.show_search,
            font=font,
            width=150,
            height=40,
        )
        self.search_button.grid(row=0, column=1, padx=10, pady=20)

        self.ib_manager_button = ctk.CTkButton(
            self.navbar_frame,
            text="Менеджер ИБ",
            command=self.show_ib_manager,
            font=font,
            width=150,
            height=40,
        )
        self.ib_manager_button.grid(row=0, column=2, padx=10, pady=20)

        self.embed_button = ctk.CTkButton(
            self.navbar_frame,
            text="Права",
            command=self.show_embed,
            font=font,
            width=150,
            height=40,
        )
        self.embed_button.grid(row=0, column=3, padx=10, pady=20)

        self.users_button = ctk.CTkButton(
            self.navbar_frame,
            text="Инфо",
            command=self.show_users,
            font=font,
            width=150,
            height=40,
        )
        self.users_button.grid(row=0, column=4, padx=10, pady=20)

        self.navbar_frame.grid_columnconfigure(0, weight=1)
        self.navbar_frame.grid_columnconfigure(1, weight=1)
        self.navbar_frame.grid_columnconfigure(2, weight=1)
        self.navbar_frame.grid_columnconfigure(3, weight=1)
        self.navbar_frame.grid_columnconfigure(4, weight=1)

        # Main container for different frames
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (
            IECManagerFrame,
            SearchFrame,
            IBManagerFrame,
            UsersFrame,
            EmbedFrame,
        ):  # , EmbedFrame
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

    def show_ib_manager(self):
        self.show_frame("IBManagerFrame")

    def show_users(self):
        self.show_frame("UsersFrame")

    def show_embed(self):
        self.show_frame("EmbedFrame")


class IECManagerFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        font = get_font()

        # Окно выбора файла .iec_hmi
        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.pack(pady=(20, 5), padx=50, fill="x")

        self.file_label = ctk.CTkLabel(
            self.file_frame, text="Выберите файл .iec_hmi:", wraplength=880, font=font
        )
        self.file_label.grid(row=0, column=0, padx=(10, 10), sticky="w")

        self.file_button = ctk.CTkButton(
            self.file_frame,
            text="Выбрать файл",
            command=lambda: self.select_file("iec_hmi"),
            font=font,
            width=200,
            height=50,
        )
        self.file_button.grid(row=0, column=1, sticky="e")

        self.file_frame.grid_columnconfigure(1, weight=1)

        # Окно выбора файла GraphicsCompositeType.txt
        self.graphics_frame = ctk.CTkFrame(self)
        self.graphics_frame.pack(pady=(10, 5), padx=50, fill="x")

        self.graphics_label = ctk.CTkLabel(
            self.graphics_frame,
            wraplength=880,
            text="Выберите файл GraphicsCompositeType.txt:",
            font=font,
        )
        self.graphics_label.grid(row=0, column=0, padx=(10, 10), sticky="w")

        self.graphics_button = ctk.CTkButton(
            self.graphics_frame,
            text="Выбрать файл",
            command=lambda: self.select_file("graphics"),
            font=font,
            width=200,
            height=50,
        )
        self.graphics_button.grid(row=0, column=1, sticky="e")

        self.graphics_frame.grid_columnconfigure(1, weight=1)

        # Окно выбора файла TSubWindowType.txt
        self.subwindow_frame = ctk.CTkFrame(self)
        self.subwindow_frame.pack(pady=(10, 5), padx=50, fill="x")

        self.subwindow_label = ctk.CTkLabel(
            self.subwindow_frame,
            wraplength=880,
            text="Выберите файл TSubWindowType.txt:",
            font=font,
        )
        self.subwindow_label.grid(row=0, column=0, padx=(10, 10), sticky="w")

        self.subwindow_button = ctk.CTkButton(
            self.subwindow_frame,
            text="Выбрать файл",
            command=lambda: self.select_file("subwindow"),
            font=font,
            width=200,
            height=50,
        )
        self.subwindow_button.grid(row=0, column=1, sticky="e")

        self.subwindow_frame.grid_columnconfigure(1, weight=1)

        # Окно с сообщениями
        self.message_label = ctk.CTkLabel(
            self, text="Сообщения:", font=font, anchor="w"
        )
        self.message_label.pack(pady=(10, 5), padx=50, anchor="w")

        self.error_text = ctk.CTkTextbox(self, height=5, wrap="word", state="normal")
        self.error_text.pack(fill="both", expand=True, padx=50)

        # Кнопки
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(padx=50, pady=20, fill="x")

        self.process_button = ctk.CTkButton(
            self.button_frame,
            text="Изменить все окна",
            command=self.run_main,
            font=font,
            width=300,
            height=50,
        )
        self.process_button.pack(anchor="w", side="left", padx=(0, 10), expand=True)

        self.graphics_button = ctk.CTkButton(
            self.button_frame,
            text="Изменить только на GraphicsComposite",
            command=self.run_with_graphics,
            font=font,
            width=300,
            height=50,
        )
        self.graphics_button.pack(
            anchor="center", side="left", padx=(0, 10), expand=True
        )

        self.subwindow_button = ctk.CTkButton(
            self.button_frame,
            text="Изменить только на SubWindow",
            command=self.run_with_subwindow,
            font=font,
            width=300,
            height=50,
        )
        self.subwindow_button.pack(anchor="e", side="left", expand=True)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def select_file(self, file_type):
        file_types = (
            [("IEC_HMI files", "*.iec_hmi")]
            if file_type in ["iec_hmi", "ib_iec_hmi"]
            else [("Text files", "*.txt")]
        )
        selected_file = filedialog.askopenfilename(filetypes=file_types)
        if selected_file:
            self.controller.selected_files[file_type] = selected_file
            if file_type == "iec_hmi":
                self.file_label.configure(text=f"Выбран файл: {selected_file}")
            elif file_type == "graphics":
                self.graphics_label.configure(text=f"Выбран файл: {selected_file}")
            elif file_type == "subwindow":
                self.subwindow_label.configure(text=f"Выбран файл: {selected_file}")
            elif file_type == "ib_iec_hmi":
                self.controller.frames["IBManagerFrame"].ib_file_label.configure(
                    text=f"Выбран файл: {selected_file}"
                )
        else:
            if file_type == "iec_hmi":
                self.file_label.configure(text="Выберите файл .iec_hmi:")
            elif file_type == "graphics":
                self.graphics_label.configure(
                    text="Выберите файл GraphicsCompositeType.txt:"
                )
            elif file_type == "subwindow":
                self.subwindow_label.configure(text="Выберите файл TSubWindowType.txt:")
            elif file_type == "ib_iec_hmi":
                self.controller.frames["IBManagerFrame"].ib_file_label.configure(
                    text="Выберите СТАРЫЙ файл .iec_hmi:"
                )

    def run_main(self):
        if self.controller.selected_files["iec_hmi"]:
            if not self.controller.selected_files["graphics"]:
                self.error_text.insert(
                    "end",
                    "\n\n   Файл с расширением GraphicsCompositeType.txt не выбран",
                )
                return
            if not self.controller.selected_files["subwindow"]:
                self.error_text.insert(
                    "end", "\n\n   Файл с расширением TSubWindowType.txt не выбран"
                )
                return

            command = [
                self.controller.selected_files["iec_hmi"],
                "--graphics",
                self.controller.selected_files["graphics"],
                "--subwindow",
                self.controller.selected_files["subwindow"],
            ]
            main_core(command)  # Вызов функции main_core

            self.error_text.insert(
                "end",
                "\n\n   Изменение всех окон завершено, результат сохранен в файл result.iec_hmi",
            )
        else:
            self.error_text.insert(
                "end", "\n\n   Файл с расширением .iec_hmi не выбран"
            )

    def run_with_graphics(self):
        if (
            self.controller.selected_files["iec_hmi"]
            and self.controller.selected_files["graphics"]
        ):
            command = [
                self.controller.selected_files["iec_hmi"],
                "--graphics",
                self.controller.selected_files["graphics"],
            ]
            main_core(command)  # Вызов функции main_core
            self.error_text.insert(
                "end",
                "\n\n   Изменение окон на GraphicsComposite завершено,"
                " результат сохранен в файл result.iec_hmi",
            )
        else:
            self.error_text.insert(
                "end",
                "\n\n   Файл с расширением .iec_hmi или GraphicsCompositeType.txt не выбран",
            )

    def run_with_subwindow(self):
        if (
            self.controller.selected_files["iec_hmi"]
            and self.controller.selected_files["subwindow"]
        ):
            command = [
                self.controller.selected_files["iec_hmi"],
                "--subwindow",
                self.controller.selected_files["subwindow"],
            ]
            main_core(command)  # Вызов функции main_core
            self.error_text.insert(
                "end",
                "\n\n   Изменение окон на SubWindow завершено,"
                " результат сохранен в файл result.iec_hmi",
            )
        else:
            self.error_text.insert(
                "end",
                "\n\n   Файл с расширением .iec_hmi или TSubWindowType.txt не выбран",
            )


def copy_selected_text(event):
    selected_text = event.widget.selection_get()
    pyperclip.copy(selected_text)


def show_notification():
    notification_window = tk.Toplevel()
    notification_window.overrideredirect(True)  # Без границ и заголовка
    notification_label = tk.Label(
        notification_window, text="Текст скопирован!", font=("Arial", 12), fg="black"
    )
    notification_label.pack()

    # Указываем координаты для верхнего левого угла экрана
    x_pos = 0  # координата X
    y_pos = 0  # координата Y
    notification_window.geometry("+{}+{}".format(x_pos, y_pos))

    notification_window.after(1500, lambda: notification_window.destroy())


class SearchFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.select_iec_hmi_label = None
        self.controller = controller
        font = get_font()

        # Основной фрейм для кнопок
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(pady=(10, 10), padx=50, fill="x")

        # Кнопка поиска hid to hide
        self.find_hid_to_hide_button = ctk.CTkButton(
            self.button_frame,
            text="Найти hid to hide",
            command=self.find_hid_to_hide,
            font=font,
            width=300,
            height=50,
        )
        self.find_hid_to_hide_button.grid(row=0, column=0, padx=(0, 5))

        # Кнопка поиска использования окон
        self.find_window_usage_button = ctk.CTkButton(
            self.button_frame,
            text="Найти использование окон",
            command=self.find_window_usage,
            font=font,
            width=300,
            height=50,
        )
        self.find_window_usage_button.grid(row=0, column=1, padx=5)

        # Кнопка поиска неиспользуемых окон
        self.find_unused_windows_button = ctk.CTkButton(
            self.button_frame,
            text="Найти неиспользуемые окна",
            command=self.find_unused_windows,
            font=font,
            width=300,
            height=50,
        )
        self.find_unused_windows_button.grid(row=0, column=2, padx=5)

        # Кнопка поиска неиспользуемых окон
        self.find_users_button = ctk.CTkButton(
            self.button_frame,
            text="Найти user",
            command=self.find_users,
            font=font,
            width=300,
            height=50,
        )
        self.find_users_button.grid(row=0, column=3, padx=(5, 0))

        # Конфигурация столбцов фрейма
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)
        self.button_frame.grid_columnconfigure(2, weight=1)
        self.button_frame.grid_columnconfigure(3, weight=1)

        # Окно с сообщениями
        self.message_label = ctk.CTkLabel(
            self, text="Сообщения:", font=font, anchor="w"
        )
        self.message_label.pack(pady=(10, 5), padx=50, anchor="w")

        self.error_text = ctk.CTkTextbox(self, height=5, wrap="word", font=font)

        self.error_text.pack(fill="both", expand=True, pady=(0, 50), padx=50)

        def on_right_click(event):
            copy_selected_text(event)
            show_notification()

        self.error_text.bind("<Button-3>", on_right_click)

    def select_iec_hmi_file(self):
        file_types = [("IEC_HMI files", "*.iec_hmi")]
        selected_file = filedialog.askopenfilename(filetypes=file_types)
        if selected_file:
            # Обработка выбора файла .iec_hmi
            self.controller.selected_files["iec_hmi"] = selected_file
            self.select_iec_hmi_label.configure(text=f"Выбран файл: {selected_file}")

    def find_hid_to_hide(self):
        self.error_text.configure(state="normal")
        if not self.controller.selected_files["iec_hmi"]:
            # Handle case where no .iec_hmi file is selected
            self.error_text.delete(1.0, tk.END)
            self.error_text.insert(tk.END, "Выберите файл .iec_hmi сначала.")
            self.error_text.configure(state="disabled")
            return

        iec_hmi_file = self.controller.selected_files["iec_hmi"]
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
        self.error_text.configure(state="disabled")

    def find_window_usage(self):
        self.error_text.configure(state="normal")
        if not self.controller.selected_files["iec_hmi"]:
            # Handle case where no .iec_hmi file is selected

            self.error_text.delete(1.0, tk.END)
            self.error_text.insert(tk.END, "Выберите файл .iec_hmi сначала.")
            self.error_text.configure(state="disabled")
            return

        iec_hmi_file = self.controller.selected_files["iec_hmi"]
        graphics_label_file = self.controller.selected_files["graphics"]
        subwindow_label_file = self.controller.selected_files["subwindow"]
        matches = finder.find_window_usage(
            iec_hmi_file, graphics_label_file, subwindow_label_file
        )

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

        self.error_text.configure(state="disabled")

    def find_unused_windows(self):
        self.error_text.configure(state="normal")
        if not self.controller.selected_files["iec_hmi"]:
            # Handle case where no .iec_hmi file is selected
            self.error_text.delete(1.0, tk.END)
            self.error_text.insert(tk.END, "Выберите файл .iec_hmi сначала.")
            self.error_text.configure(state="disabled")
            return

        iec_hmi_file = self.controller.selected_files["iec_hmi"]
        unused_windows = finder.find_unused_windows(iec_hmi_file)

        if unused_windows:
            # Очистка текстового поля перед выводом новых сообщений
            self.error_text.delete(1.0, tk.END)

            # Вывод найденных строк в текстовое поле
            self.error_text.insert(tk.END, "Неиспользуемые окна:\n")
            for window in unused_windows:
                self.error_text.insert(tk.END, f"{window}\n")
        else:
            self.error_text.delete(1.0, tk.END)
            self.error_text.insert(tk.END, "Все окна используются.")

        self.error_text.configure(state="disabled")

    def find_users(self):
        self.error_text.configure(state="normal")

        if not self.controller.selected_files["iec_hmi"]:
            # Handle case where no .iec_hmi file is selected
            self.error_text.delete(1.0, tk.END)
            self.error_text.insert(tk.END, "Выберите файл .iec_hmi сначала.")
            self.error_text.configure(state="disabled")
            return

        iec_hmi_file = self.controller.selected_files["iec_hmi"]

        # Вызов функции из finder.py для поиска пользователей
        matches = finder.find_user_blocks(iec_hmi_file)

        if matches:
            # Очистка текстового поля перед выводом новых сообщений
            self.error_text.delete(1.0, tk.END)

            # Вывод найденных строк в текстовое поле
            self.error_text.insert(
                tk.END, "Найдены следующие блоки с использованием USER:\n"
            )
            for match in matches:
                self.error_text.insert(tk.END, f"{match}\n")
        else:
            self.error_text.delete(1.0, tk.END)
            self.error_text.insert(tk.END, "Не найдено совпадений.")

        self.error_text.configure(state="disabled")


class IBManagerFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        font = get_font()

        # Окно выбора файла .iec_hmi
        self.ib_file_frame = ctk.CTkFrame(self)
        self.ib_file_frame.pack(pady=(20, 5), padx=50, fill="x")

        self.ib_file_label = ctk.CTkLabel(
            self.ib_file_frame,
            text="Выберите СТАРЫЙ файл .iec_hmi:",
            wraplength=880,
            font=font,
        )
        self.ib_file_label.grid(row=0, column=0, padx=(10, 10), sticky="w")

        self.ib_file_button = ctk.CTkButton(
            self.ib_file_frame,
            text="Выбрать файл",
            command=lambda: self.select_file("ib_iec_hmi", self.ib_file_label),
            font=font,
            width=200,
            height=50,
        )
        self.ib_file_button.grid(row=0, column=1, sticky="e")

        self.ib_file_frame.grid_columnconfigure(1, weight=1)

        # Окно выбора папки Design
        self.design_folder_frame = ctk.CTkFrame(self)
        self.design_folder_frame.pack(pady=(10, 5), padx=50, fill="x")

        self.design_folder_label = ctk.CTkLabel(
            self.design_folder_frame,
            wraplength=880,
            text="Выберите папку Design:",
            font=font,
        )
        self.design_folder_label.grid(row=0, column=0, padx=(10, 10), sticky="w")

        self.design_folder_button = ctk.CTkButton(
            self.design_folder_frame,
            text="Выбрать папку",
            command=self.select_folder,
            font=font,
            width=200,
            height=50,
        )
        self.design_folder_button.grid(row=0, column=1, sticky="e")

        self.design_folder_frame.grid_columnconfigure(1, weight=1)

        # Окно выбора файла .prj
        self.prj_file_frame = ctk.CTkFrame(self)
        self.prj_file_frame.pack(pady=(10, 5), padx=50, fill="x")

        self.prj_file_label = ctk.CTkLabel(
            self.prj_file_frame, text="Выберите файл .prj:", wraplength=880, font=font
        )
        self.prj_file_label.grid(row=0, column=0, padx=(10, 10), sticky="w")

        self.prj_file_button = ctk.CTkButton(
            self.prj_file_frame,
            text="Выбрать файл",
            command=lambda: self.select_file("prj", self.prj_file_label),
            font=font,
            width=200,
            height=50,
        )
        self.prj_file_button.grid(row=0, column=1, sticky="e")

        self.prj_file_frame.grid_columnconfigure(1, weight=1)

        # Окно выбора файла .int mnemo
        self.mnemo_file_frame = ctk.CTkFrame(self)
        self.mnemo_file_frame.pack(pady=(10, 5), padx=50, fill="x")

        self.mnemo_file_label = ctk.CTkLabel(
            self.mnemo_file_frame,
            wraplength=880,
            text="Выберите файл .int mnemo:",
            font=font,
        )
        self.mnemo_file_label.grid(row=0, column=0, padx=(10, 10), sticky="w")

        self.mnemo_file_button = ctk.CTkButton(
            self.mnemo_file_frame,
            text="Выбрать файл",
            command=lambda: self.select_file("int_mnemo", self.mnemo_file_label),
            font=font,
            width=200,
            height=50,
        )
        self.mnemo_file_button.grid(row=0, column=1, sticky="e")

        self.mnemo_file_frame.grid_columnconfigure(1, weight=1)

        # Окно выбора файла .int event logger
        self.event_logger_file_frame = ctk.CTkFrame(self)
        self.event_logger_file_frame.pack(pady=(10, 5), padx=50, fill="x")

        self.event_logger_file_label = ctk.CTkLabel(
            self.event_logger_file_frame,
            text="Выберите файл .int event logger:",
            wraplength=880,
            font=font,
        )
        self.event_logger_file_label.grid(row=0, column=0, padx=(10, 10), sticky="w")

        self.event_logger_file_button = ctk.CTkButton(
            self.event_logger_file_frame,
            text="Выбрать файл",
            command=lambda: self.select_file(
                "int_event_logger", self.event_logger_file_label
            ),
            font=font,
            width=200,
            height=50,
        )
        self.event_logger_file_button.grid(row=0, column=1, sticky="e")

        self.event_logger_file_frame.grid_columnconfigure(1, weight=1)

        # Ряд кнопок
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(pady=(10, 10), padx=50, fill="x")

        self.ib_manager_button = ctk.CTkButton(
            self.button_frame,
            text="Перенести палитры",
            command=self.run_ib_command,
            font=font,
            width=300,
            height=50,
        )
        self.ib_manager_button.grid(row=0, column=0, padx=(0, 5))

        self.change_font_button = ctk.CTkButton(
            self.button_frame,
            text="Изменить шрифт",
            command=self.change_font,
            font=font,
            width=300,
            height=50,
        )
        self.change_font_button.grid(row=0, column=1, padx=5)

        self.add_variables_button = ctk.CTkButton(
            self.button_frame,
            text="Добавить переменные",
            command=self.add_variables,
            font=font,
            width=300,
            height=50,
        )
        self.add_variables_button.grid(row=0, column=2, padx=5)

        self.add_files_button = ctk.CTkButton(
            self.button_frame,
            text="Добавить файлы",
            command=self.add_files,
            font=font,
            width=300,
            height=50,
        )
        self.add_files_button.grid(row=0, column=3, padx=(5, 5))

        self.add_HMI_button = ctk.CTkButton(
            self.button_frame,
            text="Добавить в HMI",
            command=self.add_HMI,
            font=font,
            width=300,
            height=50,
        )
        self.add_HMI_button.grid(row=0, column=4, padx=(5, 0))

        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)
        self.button_frame.grid_columnconfigure(2, weight=1)
        self.button_frame.grid_columnconfigure(3, weight=1)
        self.button_frame.grid_columnconfigure(4, weight=1)

        #        # Второй ряд кнопок
        #        self.button_frame = ctk.CTkFrame(self)
        #        self.button_frame.pack(pady=(0, 10), padx=50, fill="x")
        #
        #        self.add_HMI_button = ctk.CTkButton(self.button_frame, text="Добавить в HMI",
        #                                               command=self.add_HMI, font=font, width=300,
        #                                               height=50)
        #        self.add_HMI_button.grid(row=0, column=0, padx=(0, 5))
        #
        #       self.change_font_button = ctk.CTkButton(self.button_frame, text="Изменить шрифт",
        #                                                 font=font, width=300,
        #                                                height=50)
        #        self.change_font_button.grid(row=0, column=1, padx=5)
        #
        #        self.add_variables_button = ctk.CTkButton(self.button_frame, text="Добавить переменные",
        #                                                   font=font, width=300,
        #                                                  height=50)
        #        self.add_variables_button.grid(row=0, column=2, padx=5)
        #
        #        self.add_files_button = ctk.CTkButton(self.button_frame, text="Добавить файлы",
        #                                               font=font, width=300,
        #                                              height=50)
        #        self.add_files_button.grid(row=0, column=3, padx=(5, 0))

        #        self.button_frame.grid_columnconfigure(0, weight=1)
        #       self.button_frame.grid_columnconfigure(1, weight=1)
        #       self.button_frame.grid_columnconfigure(2, weight=1)
        #       self.button_frame.grid_columnconfigure(3, weight=1)

        # Путь к выбранной папке Design
        self.selected_folder = None

        # Окно с сообщениями
        self.message_label = ctk.CTkLabel(
            self, text="Сообщения:", font=font, anchor="w"
        )
        self.message_label.pack(pady=(0, 5), padx=50, anchor="w")

        self.error_text = ctk.CTkTextbox(self, height=5, wrap="word", state="normal")
        self.error_text.pack(fill="both", expand=True, padx=50, pady=(0, 10))

    def select_file(self, file_type, label):
        file_types = {
            "ib_iec_hmi": [("IEC HMI Files", "*.iec_hmi")],
            "prj": [("PRJ Files", "*.prj")],
            "int_mnemo": [("INT Mnemo Files", "*.int")],
            "int_event_logger": [("INT Event Logger Files", "*.int")],
        }

        file_path = filedialog.askopenfilename(filetypes=file_types[file_type])
        if file_path:
            self.controller.selected_files[file_type] = file_path
            label.configure(text=f"Выбран файл: {file_path}")
            self.controller.frames["IBManagerFrame"].error_text.insert(
                "end", f"\n\n   Выбран файл ({file_type}): {file_path}"
            )
            self.controller.frames["IBManagerFrame"].error_text.see("end")

    def select_folder(self):
        try:
            folder_path = filedialog.askdirectory()
            if folder_path:
                self.selected_folder = folder_path
                self.design_folder_label.configure(text=f"Выбрана папка: {folder_path}")
                self.controller.frames["IBManagerFrame"].error_text.insert(
                    "end", f"\n\n   Выбрана папка: {folder_path}"
                )
                self.controller.frames["IBManagerFrame"].error_text.see("end")
        except Exception as e:
            print(f"Error selecting folder: {e}")  # Отладочное сообщение

    def run_ib_command(self):
        if self.controller.selected_files["ib_iec_hmi"]:
            file_path = self.controller.selected_files["ib_iec_hmi"]
            execute_ib_command(file_path)  # Вызов функции из changer.py

            self.controller.frames["IBManagerFrame"].error_text.insert(
                "end", "\n\n   Файл успешно обновлен."
            )
            self.controller.frames["IBManagerFrame"].error_text.see("end")
        else:
            self.controller.frames["IBManagerFrame"].error_text.insert(
                "end", "\n\n   Файл с расширением iec_hmi не выбран"
            )
            self.controller.frames["IBManagerFrame"].error_text.see("end")

    def change_font(self):
        if self.controller.selected_files["iec_hmi"]:
            file_path = self.controller.selected_files["iec_hmi"]
            change_font_in_file(file_path)  # Вызов функции из changer.py

            self.controller.frames["IBManagerFrame"].error_text.insert(
                "end", "\n\n   Шрифты успешно обновлены."
            )
            self.controller.frames["IBManagerFrame"].error_text.see("end")
        else:
            self.controller.frames["IBManagerFrame"].error_text.insert(
                "end", "\n\n   Файл с расширением iec_hmi не выбран"
            )
            self.controller.frames["IBManagerFrame"].error_text.see("end")

    def add_files(self):
        if self.selected_folder:
            add_files_to_design(self.selected_folder)  # Вызов функции из changer.py

            self.controller.frames["IBManagerFrame"].error_text.insert(
                "end", f"\n\n   Файлы добавлены в папку: {self.selected_folder}"
            )
            self.controller.frames["IBManagerFrame"].error_text.see("end")
        else:
            self.controller.frames["IBManagerFrame"].error_text.insert(
                "end", "\n\n   Папка не выбрана."
            )
            self.controller.frames["IBManagerFrame"].error_text.see("end")

    def add_variables(self):
        try:
            if (
                self.controller.selected_files["prj"]
                and self.controller.selected_files["int_mnemo"]
                and self.controller.selected_files["int_event_logger"]
            ):
                prj_file = self.controller.selected_files["prj"]
                mnemo_file = self.controller.selected_files["int_mnemo"]
                event_logger_file = self.controller.selected_files["int_event_logger"]

                from changer import add_variables_to_files

                add_variables_to_files(
                    prj_file, mnemo_file, event_logger_file
                )  # Вызов функции из changer.py

                self.display_message("Переменные добавлены в файлы.", "success")
            else:
                self.display_message("Один из файлов не выбран.", "error")
        except Exception as e:
            self.display_message(f" при добавлении переменных: {e}", "error")

    def display_message(self, message, message_type):
        if message_type == "error":
            prefix = "Ошибка:"
        elif message_type == "success":
            prefix = "Успех:"
        else:
            prefix = "Сообщение:"

        self.error_text.insert("end", f"\n\n   {prefix} {message}")
        self.error_text.see("end")

    def add_HMI(self):
        if self.controller.selected_files["iec_hmi"]:
            file_path = self.controller.selected_files["iec_hmi"]
            add_HMI_to_files(file_path)  # Вызов функции из changer.py

            self.controller.frames["IBManagerFrame"].error_text.insert(
                "end",
                "\n\n   Добавлена папка IB, ресурс IS.png, а также импортированны TButtonUser и TIS_Admin.",
            )
            self.controller.frames["IBManagerFrame"].error_text.see("end")
        else:
            self.controller.frames["IBManagerFrame"].error_text.insert(
                "end", "\n\n   Файл с расширением iec_hmi не выбран"
            )
            self.controller.frames["IBManagerFrame"].error_text.see("end")


class UsersFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        font = get_font()

        # Создание текстового виджета с CustomTkinter
        self.text_widget = ctk.CTkTextbox(self, height=5, wrap="word", font=font)
        self.text_widget.pack(
            pady=(20, 50), padx=50, anchor="w", fill="both", expand=True
        )

        # Добавление текста в виджет
        self.text_widget.insert("1.0", "\n🤓Модная разработка Яцышина и Чепусова🤓\n")
        self.text_widget.insert(
            "end",
            "\nИнструкция с полным описанием работы программы находиться в файле IB_Manager.docx\n",
        )
        self.text_widget.insert(
            "end",
            "\nВсе вопросы/предложения/сообщения об ошибках - yatsyshin@vega-gaz.ru🙈🙉🙊\n\n\n",
        )
        self.text_widget.insert(
            "end", "\nПО для автоматической аткуализации проектов Sonata V1.0.\n"
        )

        # Отключение редактирования текста
        self.text_widget.configure(state="disabled")


class EmbedFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        font = get_font()

        # Окно выбора файла .iec_hmi
        self.ib_file_frame = ctk.CTkFrame(self)
        self.ib_file_frame.pack(pady=(20, 5), padx=50, fill="x")

        self.ib_file_label = ctk.CTkLabel(
            self.ib_file_frame,
            text="Введите название окна Event:",
            wraplength=880,
            font=font,
        )
        self.ib_file_label.grid(row=0, column=0, padx=(10, 10), sticky="w")

        self.ib_file_entry = ctk.CTkEntry(self.ib_file_frame, font=font, width=300)
        self.ib_file_entry.grid(row=0, column=1, padx=(10, 10), sticky="w")

        self.ib_add_rights_button = ctk.CTkButton(
            self.ib_file_frame,
            text="Добавить права",
            command=lambda: self.add_event(self.ib_file_entry.get()),
            font=font,
            width=200,
            height=50,
        )
        self.ib_add_rights_button.grid(
            row=0, column=2, pady=(0, 0), padx=(10, 10), sticky="e"
        )

        self.ib_file_frame.grid_columnconfigure(1, weight=1)

    def add_event(self, event_name):
        if self.controller.selected_files["iec_hmi"]:
            file_path = self.controller.selected_files["iec_hmi"]
            add_event_to_files(
                file_path, event_name
            )  # Вызов функции с двумя параметрами

            self.controller.frames["IBManagerFrame"].error_text.insert(
                "end", "\n\n   Добавлены права и регистрация сообщения в Event."
            )
            self.controller.frames["IBManagerFrame"].error_text.see("end")
        else:
            self.controller.frames["IBManagerFrame"].error_text.insert(
                "end", "\n\n   Файл с расширением iec_hmi не выбран"
            )
            self.controller.frames["IBManagerFrame"].error_text.see("end")


def show_error_dialog():
    root = tk.Tk()
    root.withdraw()  # Скрыть основное окно приложения
    messagebox.showerror("Ошибка", "Доступ запрещен. Обратитесь к администратору.")


def execute_on_successful_access():
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = App()
    app.mainloop()


if __name__ == "__main__":
    if isRun():
        execute_on_successful_access()
    else:
        show_error_dialog()
