import tkinter as tk
from tkinter import simpledialog
from db import DB
from tkinter import filedialog
from comport import available_ports, SerialDevice
from create_lesson import create_new_lesson_from_txt, create_new_lesson_from_mp4


class SelectLesson:
    def __init__(self, root):
        self.db = DB()
        self.current_lesson_name = tk.StringVar()
        cur_less = self.db.get_current_lesson()
        self.current_lesson_name.set(cur_less[1])
        self.current_lesson_id = cur_less[0]
        self.root = root
        self.select_dialog = None
        self.text_file_path = ''
        self.name_lesson = tk.StringVar()
        self.descr_lesson = tk.StringVar()
        self.dropdown_lesson_name = tk.StringVar()
        self.first_lang = tk.StringVar()
        self.second_lang = tk.StringVar()

    # def update_dropdown(self):
    #     items = self.db.fetch_lesson_name()
    #     self.dropdown_lesson_name_list['values'] = items

    def show_select_dialog(self):
        def clc_ok_btm(dial):

            selected_item = self.current_lesson_name.get()
            if selected_item in name_lesson:
                index = name_lesson.index(selected_item)
                self.db.set_default_lesson([id_lesson[index]])
                self.current_lesson_id = id_lesson[index]
                # print(f"id: {id_lesson[index]}")
            on_closing(dial)

        def on_closing(dial):
            self.root.attributes('-disabled', False)
            self.root.deiconify()
            dial.destroy()

        dialog = tk.Toplevel(self.root)
        dialog.protocol("WM_DELETE_WINDOW", lambda: on_closing(dialog))
        label_name = tk.Label(dialog, text="Урок")
        label_name.grid(row=0, column=0)

        dialog.title("Выбор урока")
        option = self.db.fetch_lesson_name()
        id_lesson = [item[0] for item in option]
        name_lesson = [item[1] for item in option]
        # print(option)
        item_dropdown = tk.OptionMenu(dialog, self.current_lesson_name, *name_lesson)
        # Привязать обработчик события выбора элемента
        # def on_select(event):
        #     lesson_name.config(text=self.dropdown_lesson_name.get())

        # item_dropdown.bind('<Configure>', on_select)
        item_dropdown.grid(row=0, column=1)

        tk.Button(dialog, text="Создать урок",
                  command=lambda: self.create_lesson_dialog(file_type='txt')).grid(row=1, column=0)
        tk.Button(dialog, text="Создать видео урок",
                  command=lambda: self.create_lesson_dialog(file_type='mp4')).grid(row=1, column=1)
        tk.Button(dialog, text="OK", command=lambda: clc_ok_btm(dialog)).grid(row=2, column=0)

        self.select_dialog = dialog
        self.root.attributes('-disabled', True)

    def create_lesson_dialog(self, file_type):
        def open_file_dialog():
            file_path = filedialog.askopenfilename(
                title="Выберите файл",
                filetypes=(("Текстовые файлы", f"*.{file_type}"), ("Все файлы", "*.*"))
            )
            if file_path:
                file_name.config(text=file_path)
                self.text_file_path = file_path

        def create_lesson():
            if self.text_file_path != '' and self.name_lesson.get() != '' and self.descr_lesson.get() != '':
                if file_type == 'txt':
                    create_new_lesson_from_txt(self.text_file_path, self.first_lang.get(),  self.second_lang.get(),
                                               self.name_lesson.get(), self.descr_lesson.get())
                    print(self.text_file_path, self.name_lesson.get(), self.descr_lesson.get())
                elif file_type == 'mp4':
                    create_new_lesson_from_mp4(self.text_file_path, self.first_lang.get(),  self.second_lang.get(),
                                               self.name_lesson.get(), self.descr_lesson.get())
            else:
                tk.messagebox.showwarning("Предупреждение", "Заполните все поля", icon="warning", default="ok")

        dialog = tk.Toplevel(self.select_dialog)
        dialog.title("Введите название урока")

        # Виджеты для ввода данных
        tk.Label(dialog, text="Название:").grid(row=0, column=0)
        tk.Entry(dialog, textvariable=self.name_lesson).grid(row=0, column=1)
        tk.Label(dialog, text="Описание:").grid(row=1, column=0)
        tk.Entry(dialog, textvariable=self.descr_lesson).grid(row=1, column=1)
        tk.Label(dialog, text='Язык который учишь').grid(row=2, column=0)
        tk.OptionMenu(dialog, self.first_lang, *self.db.get_lang_list()).grid(row=2, column=1)
        tk.Label(dialog, text='Родной язык').grid(row=2, column=2)
        tk.OptionMenu(dialog, self.second_lang, *self.db.get_lang_list()).grid(row=2, column=3)
        tk.Label(dialog, text="Файл:").grid(row=3, column=0)
        file_name = tk.Label(dialog, text='')
        file_name.grid(row=3, column=1)
        tk.Button(dialog, text="Файл", command=open_file_dialog).grid(row=4, columnspan=2)
        tk.Button(dialog, text="OK", command=create_lesson).grid(row=5, columnspan=2)

        dialog.wait_window(dialog)  # Ожидание закрытия диалогового окна


# self.db.create_new_lesson(file_path, name_lesson, description_lesson, 1)
# return value1.get(), value2.get()


class AppSettings:
    def __init__(self, root):
        self.root = root
        self.db = DB()
        raw_setting = self.db.app_setting_init()
        self.settings = {
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
            'right_answer_1': tk.StringVar(),
            'right_answer_2': tk.StringVar(),
            'apostrophe': tk.BooleanVar()
        }
        print(raw_setting)
        for key, var in self.settings.items():
            var.set(raw_setting[key])

        self.comport_available = available_ports()
        print(str(self.comport_available[0]))
        # device = SerialDevice(str(self.comport_available[0]), baudrate=9600, timeout=1)

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

        def on_select(event):
            new_options = available_ports()
            #print(available_ports())
            item_dropdown['menu'].delete(0, 'end')

            # Добавляем новые элементы в OptionMenu
            for option in new_options:
                item_dropdown['menu'].add_command(label=option, command=tk._setit(self.settings['comport'], option))

        def on_select_profile(event):
            new_options = self.db.get_settings_profile()
            item_dropdown['menu'].delete(0, 'end')
            # Добавляем новые элементы в OptionMenu
            for option in new_options:
                item_dropdown['menu'].add_command(label=option['name'], command=tk._setit(selected_profile_name, option['name']))

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

        tk.Label(dialog, text="Ответов для выучено первый раз").grid(row=5, column=2, padx=5, pady=5)
        tk.Entry(dialog, textvariable=self.settings['right_answer_1']).grid(row=5, column=3, padx=5, pady=5)

        tk.Label(dialog, text="Ответов для выучено последующий").grid(row=5, column=4, padx=5, pady=5)
        tk.Entry(dialog, textvariable=self.settings['right_answer_2']).grid(row=5, column=5, padx=5, pady=5)

        tk.Checkbutton(dialog, variable=self.settings['apostrophe'], text='Учитывать апострофы').grid(row=4, column=4, pady=5, padx=5)

        def save_setting():
            self.db.save_settings(self.settings)

        def insert_setting():
            self.db.insert_settings(self.settings)

        add_button = tk.Button(dialog, text="Сохранить изменения", command=save_setting)
        add_button.grid(row=10, column=1, padx=5, pady=5)

        add_button = tk.Button(dialog, text="Создать новый профайл", command=insert_setting)
        add_button.grid(row=10, column=2, padx=5, pady=5)
