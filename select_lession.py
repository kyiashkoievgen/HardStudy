import tkinter as tk
from db import DB
from tkinter import filedialog

def open_select_lesson_dialog(root):
    dropdown_lesson_value = ''

    def get_name_lesson_dialog():
        dialog = tk.Toplevel(root)
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
    dialog = tk.Toplevel(root)
    label_name = tk.Label(dialog, text="Урок")
    label_name.pack()
    dialog.title("Выбор урока")
    item_dropdown = tk.OptionMenu(dialog, db.dropdown_lesson_name, dropdown_lesson_value, *db.fetch_lesson_name())
    # Привязать обработчик события выбора элемента
    item_dropdown.bind('<Configure>', on_select)
    item_dropdown.pack()

    add_button = tk.Button(dialog, text="Создать урок", command=open_file_dialog)
    add_button.pack()





