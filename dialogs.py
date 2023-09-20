import tkinter as tk
from tkinter import simpledialog
from db import DB
from tkinter import filedialog
from comport import available_ports


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

    # def update_dropdown(self):
    #     items = self.db.fetch_lesson_name()
    #     self.dropdown_lesson_name_list['values'] = items

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
        self.root = root
        self.db = DB()
        self.mode = None
        raw_setting = self.db.app_setting_init()
        self.settings = {
            'name': tk.StringVar(),
            'comport': tk.StringVar(),
            'profile_name': tk.StringVar(),
            'lesson_per_day': tk.StringVar(),
            'time_beetween_study_1': tk.StringVar(),
            'time_beetween_study_2': tk.StringVar(),
            'time_beetween_study_3': tk.StringVar(),
            'time_beetween_study_4': tk.StringVar(),
            'time_beetween_study_5': tk.StringVar(),
            'time_beetween_study_6': tk.StringVar(),
            'sent_in_less': tk.StringVar(),
            'show_time_sent': tk.StringVar(),
            'punish_time_1': tk.StringVar(),
            'punish_time_2': tk.StringVar(),
            'punish_time_3': tk.StringVar()
        }
        for key, var in self.settings.items():
            var.set(raw_setting[key])

            self.comport_available = available_ports()

    def open_settings_dialog(self):
        def on_closing(dial):
            self.root.attributes('-disabled', False)
            self.root.deiconify()
            dial.destroy()

        dropdown_lesson_value = ''
        dialog = tk.Toplevel(self.root)
        dialog.protocol("WM_DELETE_WINDOW", lambda: on_closing(dialog))
        dialog.title("Настройки")

        self.root.attributes('-disabled', True)

        #dropdown_mode_value = self.settings['name'].get()
        tk.Label(dialog, text="Режим").grid(row=1, column=0, padx=5, pady=5)
        item_dropdown = tk.OptionMenu(dialog, self.settings['name'], *self.db.fetch_mode_name())
        item_dropdown.grid(row=1, column=1, padx=5, pady=5)

        def on_select(event):
            new_options = available_ports()
            print(available_ports())
            item_dropdown['menu'].delete(0, 'end')

            # Добавляем новые элементы в OptionMenu
            for option in new_options:
                item_dropdown['menu'].add_command(label=option, command=tk._setit(self.settings['comport'], option))

        def on_select_profile(event):
            new_options = self.db.get_settings_profile()
            item_dropdown['menu'].delete(0, 'end')
            # Добавляем новые элементы в OptionMenu
            for option in new_options:
                item_dropdown['menu'].add_command(label=option, command=tk._setit(selected_profile_name, option))

        def on_select_name_profile(*args):
            selected_item = selected_profile_name.get()
            raw_setting = self.db.app_setting_init(selected_item)
            for key, var in self.settings.items():
                var.set(raw_setting[key])
            # print("Выбран элемент:", selected_item)

        tk.Label(dialog, text="Com Port").grid(row=1, column=2, padx=5, pady=5)
        item_dropdown = tk.OptionMenu(dialog, self.settings['comport'], *self.comport_available)
        item_dropdown.grid(row=1, column=3, padx=5, pady=5)
        item_dropdown.bind('<Button-1>', on_select)

        tk.Label(dialog, text="Имя профеля настроек").grid(row=0, column=1, padx=5, pady=5)
        tk.Entry(dialog, textvariable=self.settings['profile_name']).grid(row=0, column=2, padx=5, pady=5)

        selected_profile_name = tk.StringVar()
        selected_profile_name.set('')
        item_dropdown = tk.OptionMenu(dialog, selected_profile_name, *self.db.get_settings_profile())
        item_dropdown.grid(row=0, column=3, padx=5, pady=5)
        item_dropdown.bind('<Button-1>', on_select_profile)
        selected_profile_name.trace_add("write", on_select_name_profile)

        tk.Label(dialog, text="Количество занятий в день").grid(row=1, column=4, padx=5, pady=5)
        tk.Entry(dialog, textvariable=self.settings['lesson_per_day']).grid(row=1, column=5, padx=5, pady=5)

        tk.Label(dialog, text="Время после 1-го правильного ответа ").grid(row=2, column=0, padx=5, pady=5)
        tk.Entry(dialog, textvariable=self.settings['time_beetween_study_1']).grid(row=2, column=1, padx=5, pady=5)

        tk.Label(dialog, text="Время после 2-го правильного ответа ").grid(row=2, column=2, padx=5, pady=5)
        tk.Entry(dialog, textvariable=self.settings['time_beetween_study_2']).grid(row=2, column=3, padx=5, pady=5)

        tk.Label(dialog, text="Время после 3-го правильного ответа ").grid(row=2, column=4, padx=5, pady=5)
        tk.Entry(dialog, textvariable=self.settings['time_beetween_study_3']).grid(row=2, column=5, padx=5, pady=5)

        tk.Label(dialog, text="Время после 4-го правильного ответа ").grid(row=3, column=0, padx=5, pady=5)
        tk.Entry(dialog, textvariable=self.settings['time_beetween_study_4']).grid(row=3, column=1, padx=5, pady=5)

        tk.Label(dialog, text="Время после 5-го правильного ответа ").grid(row=3, column=2, padx=5, pady=5)
        tk.Entry(dialog, textvariable=self.settings['time_beetween_study_6']).grid(row=3, column=3, padx=5, pady=5)

        tk.Label(dialog, text="Время после 6-го правильного ответа ").grid(row=3, column=4, padx=5, pady=5)
        tk.Entry(dialog, textvariable=self.settings['time_beetween_study_6']).grid(row=3, column=5, padx=5, pady=5)

        tk.Label(dialog, text="Количество предложений в уроке ").grid(row=4, column=0, padx=5, pady=5)
        tk.Entry(dialog, textvariable=self.settings['sent_in_less']).grid(row=4, column=1, padx=5, pady=5)

        tk.Label(dialog, text="Время показа подсказки ").grid(row=4, column=2, padx=5, pady=5)
        tk.Entry(dialog, textvariable=self.settings['show_time_sent']).grid(row=4, column=3, padx=5, pady=5)

        tk.Label(dialog, text="Время наказания 1").grid(row=5, column=0, padx=5, pady=5)
        tk.Entry(dialog, textvariable=self.settings['punish_time_1']).grid(row=5, column=1, padx=5, pady=5)

        tk.Label(dialog, text="Время наказания 2").grid(row=5, column=2, padx=5, pady=5)
        tk.Entry(dialog, textvariable=self.settings['punish_time_2']).grid(row=5, column=3, padx=5, pady=5)

        tk.Label(dialog, text="Время наказания 3").grid(row=5, column=4, padx=5, pady=5)
        tk.Entry(dialog, textvariable=self.settings['punish_time_3']).grid(row=5, column=5, padx=5, pady=5)

        def save_setting():
            self.db.save_settings(self.settings)

        def insert_setting():
            self.db.insert_settings(self.settings)

        add_button = tk.Button(dialog, text="Сохранить изменения", command=save_setting)
        add_button.grid(row=10, column=1, padx=5, pady=5)

        add_button = tk.Button(dialog, text="Создать новый профайл", command=insert_setting)
        add_button.grid(row=10, column=2, padx=5, pady=5)
