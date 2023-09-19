import tkinter as tk
from tkinter import simpledialog
from db import DB
from tkinter import filedialog


class SelectLesson:
    def __init__(self, root):
        self.db = DB()
        self.current_lesson = self.db.get_current_lesson()
        self.root = root
        self.select_dialog = ''
        self.text_file_path = ''
        self.name_lesson = tk.StringVar()
        self.descr_lesson = tk.StringVar()
        self.dropdown_lesson_name = tk.StringVar()
        self.dropdown_lesson_name.set(self.current_lesson[1])

    def show_select_dialog(self):
        def clc_ok_btm(dial):
            self.db.set_default_lesson(self.dropdown_lesson_name.get())
            on_closing(dial)

        def on_closing(dial):
            self.root.attributes('-disabled', False)
            self.root.deiconify()
            dial.destroy()

        dialog = tk.Toplevel(self.root)
        dialog.protocol("WM_DELETE_WINDOW", lambda: on_closing(dialog))
        label_name = tk.Label(dialog, text="Урок")
        label_name.pack()
        dropdown_lesson_value = ''

        dialog.title("Выбор урока")
        item_dropdown = tk.OptionMenu(dialog, self.dropdown_lesson_name, dropdown_lesson_value,
                                      *self.db.fetch_lesson_name())
        # Привязать обработчик события выбора элемента
        # def on_select(event):
        #     lesson_name.config(text=self.dropdown_lesson_name.get())

        # item_dropdown.bind('<Configure>', on_select)
        item_dropdown.pack()

        tk.Button(dialog, text="Создать урок", command=self.create_lesson_dialog).pack()
        tk.Button(dialog, text="OK", command=lambda: clc_ok_btm(dialog)).pack()

        self.select_dialog = dialog
        self.root.attributes('-disabled', True)

    def create_lesson_dialog(self):
        def open_file_dialog():
            file_path = filedialog.askopenfilename(
                title="Выберите файл",
                filetypes=(("Текстовые файлы", "*.txt"), ("Все файлы", "*.*"))
            )
            if file_path:
                file_name.config(text=file_path)
                self.text_file_path = file_path

        def create_lesson():
            if self.text_file_path != '' and self.name_lesson.get() != '' and self.descr_lesson.get() != '':
                print(self.text_file_path, self.name_lesson.get(), self.descr_lesson.get())
            else:
                tk.messagebox.showwarning("Предупреждение", "Заполните все поля", icon="warning", default="ok")

        dialog = tk.Toplevel(self.select_dialog)
        dialog.title("Введите название урока")

        # Виджеты для ввода данных
        label1 = tk.Label(dialog, text="Название:")
        name_lesson = tk.Entry(dialog, textvariable=self.name_lesson)

        label2 = tk.Label(dialog, text="Описание:")
        description_lesson = tk.Entry(dialog, textvariable=self.descr_lesson)

        label3 = tk.Label(dialog, text="Файл:")
        file_name = tk.Label(dialog, text='')

        # Разместить виджеты на форме
        label1.grid(row=0, column=0)
        name_lesson.grid(row=0, column=1)

        label2.grid(row=1, column=0)
        description_lesson.grid(row=1, column=1)

        label3.grid(row=2, column=0)
        file_name.grid(row=2, column=1)

        # Кнопка "select file"
        select_file = tk.Button(dialog, text="Файл", command=open_file_dialog)
        select_file.grid(row=3, columnspan=2)

        # Кнопка "OK" для завершения ввода
        ok_button = tk.Button(dialog, text="OK", command=create_lesson)
        ok_button.grid(row=4, columnspan=2)

        dialog.wait_window(dialog)  # Ожидание закрытия диалогового окна


# self.db.create_new_lesson(file_path, name_lesson, description_lesson, 1)
# return value1.get(), value2.get()


class AppSettings:
    def __init__(self, root):
        self.punish_time_3 = None
        self.time_beetween_study_6 = None
        self.punish_time_1 = None
        self.show_time_sent = None
        self.sent_in_less = None
        self.punish_time_2 = None
        self.time_beetween_study_5 = None
        self.time_beetween_study_4 = None
        self.time_beetween_study_3 = None
        self.time_beetween_study_2 = None
        self.time_between_study_1 = None
        self.lesson_per_day = None
        self.profile_name = None
        self.comport = None
        self.root = root
        self.db = DB()
        self.mode = None

        self.db.app_setting_init(self.mode, self.comport, self.profile_name, self.lesson_per_day,
                                 self.time_between_study_1, self.time_beetween_study_2, self.time_beetween_study_3,
                                 self.time_beetween_study_4, self.time_beetween_study_5, self.time_beetween_study_6,
                                 self.sent_in_less, self.show_time_sent, self.punish_time_1, self.punish_time_2,
                                 self.punish_time_3, )

    def open_settings_dialog(self):
        dropdown_lesson_value = ''

        def get_name_lesson_dialog():
            dialog = tk.Toplevel(self.root)
            dialog.title("Введите название урока")
            value1 = tk.StringVar()
            value2 = tk.StringVar()
            # Виджеты для ввода данных
            label1 = tk.Label(dialog, text="Название:")
            name_lesson = tk.Entry(dialog, textvariable=value1)

            label2 = tk.Label(dialog, text="Описание:")
            description_lesson = tk.Entry(dialog, textvariable=value2)

            # Разместить виджеты на форме
            label1.grid(row=0, column=0)
            name_lesson.grid(row=0, column=1)

            label2.grid(row=1, column=0)
            description_lesson.grid(row=1, column=1)

            # Кнопка "OK" для завершения ввода
            ok_button = tk.Button(dialog, text="OK", command=dialog.destroy)
            ok_button.grid(row=2, columnspan=2)

            dialog.wait_window(dialog)  # Ожидание закрытия диалогового окна

            return value1.get(), value2.get()

        def open_file_dialog():
            file_path = filedialog.askopenfilename(
                title="Выберите файл",
                filetypes=(("Текстовые файлы", "*.txt"), ("Все файлы", "*.*"))
            )
            if file_path:
                name_lesson, description_lesson = get_name_lesson_dialog()
                dialog.destroy()
                db.create_new_lesson(file_path, name_lesson, description_lesson, 1)

        def on_select(event):
            if dropdown_lesson_value != "":
                print(f"Выбранное значение: {dropdown_lesson_value}")

        db = DB()
        dialog = tk.Toplevel(self.root)
        label_name = tk.Label(dialog, text="Урок")
        label_name.pack()
        dialog.title("Выбор урока")
        item_dropdown = tk.OptionMenu(dialog, db.dropdown_lesson_name, dropdown_lesson_value, *db.fetch_lesson_name())
        # Привязать обработчик события выбора элемента
        item_dropdown.bind('<Configure>', on_select)
        item_dropdown.pack()

        add_button = tk.Button(dialog, text="Создать урок", command=open_file_dialog)
        add_button.pack()
