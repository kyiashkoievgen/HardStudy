import tkinter as tk
from select_lession import open_select_lesson_dialog as sel_less_dial
import pyttsx3
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






def speek():
    engine.say(text)
    engine.runAndWait()

engine = pyttsx3.init()

# Установите желаемый язык для генерации речи (португальский)
engine.setProperty('rate', 150)  # Настройте скорость произношения (опционально)
engine.setProperty('volume', 1.0)  # Настройте громкость (опционально)
engine.setProperty('voice', 'pt-br')  # Установите голос на португальский (Бразилия)

# Преобразуйте текст на португальском языке в речь и воспроизведите его
text = "Olá, mundo! Isto é um exemplo de texto que será transformado em fala."

root = tk.Tk()
root.title("HardStudy")
window_width = 400
window_height = 300
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x}+{y}")


# Кнопка
button_file = tk.Button(root, text="Урок", command=lambda: sel_less_dial(root))
button_file.grid(row=1, column=1)

# Метка для отображения текста
label = tk.Label(root, text="")
label.grid(row=1, column=2)

settings_button = tk.Button(root, text="Settings", command=lambda: sel_less_dial(root))
settings_button.grid(row=1, column=3)

speek_button = tk.Button(root, text="Speek", command=speek)
speek_button.grid(row=2, column=2)
root.mainloop()
