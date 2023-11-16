import tkinter as tk
from dialogs import SelectLesson, AppSettings
from study import StudyPy
import video_study as mode1_study
from db import DB

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


def on_study():
    db = DB()
    mode = db.get_lesson_mode(select_lesson.current_lesson_id)
    study = StudyPy(root)

    study.show_study_window([select_lesson.current_lesson_id])


# Кнопка
button_file = tk.Button(root, text="Урок", command=lambda: select_lesson.show_select_dialog())
button_file.grid(row=1, column=1, padx=3, pady=3)

settings_button = tk.Button(root, text="Settings", command=lambda: app_settings.open_settings_dialog())
settings_button.grid(row=1, column=3, padx=3, pady=3)

tk.Button(root, text="Учить", command=on_study).grid(row=1, padx=3, pady=3)

root.mainloop()
