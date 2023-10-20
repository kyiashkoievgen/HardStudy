import tkinter as tk
from db import DB
from voice_unit import play_sound
from comport import SerialDevice
from unidecode import unidecode
from random import shuffle
from moviepy.editor import VideoFileClip


def center_window(window, width, height):
    # Получите ширину и высоту экрана
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Вычислите координаты центра родительского окна
    center_x = int((screen_width - width) / 2)
    center_y = int((screen_height - height) / 2)

    # Установите координаты и размеры дочернего окна для позиционирования его по центру
    window.geometry(f"{width}x{height}+{center_x}+{center_y}")


class Study:
    def __init__(self, main_win):
        self.sound_help_flag = None
        self.clip = None
        self.study_data = None
        self.root = None
        self.meaning = None
        self.phrase = None
        self.settings = None
        self.cur_les = None
        self.shock_count = None
        self.answer_count = None
        self.total_answer = None
        self.comport = None
        self.main_win = main_win
        self.video_id = []
        self.start_time = []
        self.db = DB()
        self.count_sent = 0
        self.phrase_sent = ''
        self.phrase_video = ''
        self.phrase_meaning = ''
        self.help_flag = None
        self.pause_time = 60000

        # открыть окно с подсказкой

    def open_window_help(self, text, delay):
        # закрыть окно с подсказкой
        def close_window(window):
            window.destroy()
            self.meaning.config(state="normal")

        new_window = tk.Toplevel(self.root)
        center_window(new_window, 200, 100)
        tk.Label(new_window, wraplength=250, text=text, font=("Arial", 12)).pack()
        self.meaning.config(state="disabled")
        self.sound_help_flag = True
        new_window.after(delay, lambda: close_window(new_window))

    def on_closing_study_window(self):
        self.comport.close()

        self.main_win.attributes('-disabled', False)
        self.main_win.deiconify()
        self.root.destroy()

    def open_window_pause(self):
        # закрыть окно
        def close_window_pause(window):
            window.destroy()
            # root.deiconify()
            self.meaning.config(state="normal")
            # root.attributes('-disabled', False)

        self.comport.send_data(b'Smoke60000\n')
        # Создаем новое окно
        window_pause = tk.Toplevel(self.root)
        center_window(window_pause, 200, 100)
        # Добавляем текстовую метку в новое окно
        tk.Label(window_pause, text='Перекур', font=("Arial", 12)).pack()
        self.meaning.config(state="disabled")
        # root.iconify()  # .attributes('-disabled', True)
        window_pause.after(self.pause_time, lambda: close_window_pause(window_pause))

    def show_study_window(self, cur_les, settings):
        def on_help():
            if not self.help_flag:
                self.help_flag = True
            self.open_window_help(self.phrase_sent, int(self.settings['show_time_sent'].get()))

            # действия при вводе ответа
        def on_entry_change(event):
            # Получаем текущий текст из строки ввода
            text = self.meaning.get()
            text_len = len(text)
            # режим 2 не учитывает апострофические знаки
            if self.settings['apostrophe']:
                text = unidecode(text)
                self.phrase_sent = unidecode(self.phrase_sent)
            # проверка правильности введенного символа
            if (text_len > 0) and (text[text_len - 1].lower() != self.phrase_sent[text_len - 1].lower()):
                # если не правильно то удаляем этот символ
                self.meaning.delete(0, tk.END)
                self.meaning.insert(0, text[0:text_len - 1])
                self.comport.send_data(b'Shock100\n')
                print('Shock')

            # если все правильно проверяем окончание фразы
            elif text_len == len(self.phrase_sent):
                self.meaning.delete(0, tk.END)
                if self.count_sent > 20:
                    if not self.help_flag:
                        self.db.set_video_studied(self.study_data)
                        self.comport.send_data(b'Viber1000\n')
                        self.open_window_pause()
                    self.count_sent = 0
                    self.study_data = self.db.get_video_study_data(cur_les, limit='LIMIT 5')
                    self.help_flag = False
                self.next()

        self.help_flag = False
        self.total_answer = 0
        self.shock_count = 0
        self.cur_les = cur_les
        self.settings = settings
        self.comport = SerialDevice(settings['comport'].get())
        self.comport.open()
        # self.main_win.attributes('-disabled', True)
        self.main_win.iconify()
        self.root = tk.Tk()
        # self.root.protocol("WM_DELETE_WINDOW", self.on_closing_study_window)
        self.root.title("HardStudy")
        self.root.iconbitmap('icon.ico')

        window_width = 600
        window_height = 300
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        tk.Label(self.root, text="Переведите:").grid(row=1, column=1, padx=3, pady=3)
        self.phrase = tk.Label(self.root, wraplength=250, text='', font=("Arial", 12))
        self.phrase.grid(row=1, column=2, padx=3, pady=3)
        tk.Label(self.root, text="Значение:").grid(row=2, column=1, padx=3, pady=3)
        self.meaning = tk.Entry(self.root, width=30, font=("Arial", 12))
        self.meaning.grid(row=2, column=2, padx=3, pady=3)
        tk.Button(self.root, text='Помощь', command=on_help).grid(row=2, column=3, padx=3, pady=3)
        tk.Button(self.root, text='Произнести', command=lambda: self.clip.preview()).grid(row=2, column=4, padx=3,
                                                                                      pady=3)
        self.meaning.bind("<KeyRelease>", on_entry_change)
        self.count_sent = 0
        self.study_data = self.db.get_video_study_data(cur_les, limit='LIMIT 5')
        self.next()
        # print(self.study_data)

    def next(self):
        if len(self.study_data) > 0:
            self.phrase_sent = self.study_data[self.count_sent]['first_leng']
            self.phrase_video = f'video\\split_file\\{self.study_data[self.count_sent]["id"]}{self.study_data[self.count_sent]["video_id"]}.mp4'
            self.phrase_meaning = self.study_data[self.count_sent]['sec_leng']
            self.phrase.config(text=self.phrase_meaning)
            self.clip = VideoFileClip(self.phrase_video)
            self.clip.preview()
            self.count_sent += 1

