import tkinter as tk
from dialogs import SelectLesson, AppSettings
import study

from tkinter import simpledialog
# import serial
#
# # Открываем COM-порт (замените 'COM3' на актуальное имя вашего порта)
# ser = serial.Serial('COM3', 9600)
#
# # Данные, которые вы хотите отправить
# data_to_send = b'Hello, COM port!'
#
# # Отправляем данные
# ser.write(data_to_send)
#
# # Закрываем COM-порт после передачи данных
# ser.close()

root = tk.Tk()
root.title("HardStudy")
root.iconbitmap('icon.ico')
window_width = 200
window_height = 60
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x}+{y}")
select_lesson = SelectLesson(root)
app_settings = AppSettings(root)

# Кнопка
button_file = tk.Button(root, text="Урок", command=lambda: select_lesson.show_select_dialog())
button_file.grid(row=1, column=1, padx=3, pady=3)

# Метка для отображения текста
label = tk.Label(root, text="")
label.grid(row=1, column=2, padx=3, pady=3)

settings_button = tk.Button(root, text="Settings", command=lambda: app_settings.open_settings_dialog())
settings_button.grid(row=1, column=3, padx=3, pady=3)

tk.Button(root, text="Учить", command=lambda: study.show_study_window(root, app_settings)).grid(row=1, column=4, padx=3, pady=3)
# def on_entry_change(event):
#     # Получаем текущий текст из строки ввода
#     text = entry.get()
#
#     # Выполняем желаемые операции с текстом (например, проверка и фильтрация символов)
#     filtered_text = ''.join(c for c in text if c.isalnum())  # Пример: оставить только буквы и цифры
#
#     # Устанавливаем отфильтрованный текст обратно в строку ввода
#     entry.delete(0, tk.END)
#     entry.insert(0, filtered_text)


# # Создаем строку ввода
# entry = tk.Entry(root, width=30)
# entry.grid(row=6, column=1)
#
# # Привязываем событие к строке ввода, чтобы отслеживать изменения
# entry.bind("<KeyRelease>", on_entry_change)

root.mainloop()
