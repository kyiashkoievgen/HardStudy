import tkinter as tk
from db import DB
from voice_unit import play_sound
from comport import SerialDevice
from unidecode import unidecode


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
        self.help_flag = False
        self.help = None
        self.add_sent_num = 0
        self.right_answer_count = 0
        self.shock_count = 0
        self.total_answer = 0
        self.root = None
        self.meaning = None
        self.phrase = None
        self.study_data = None
        self.main_win = main_win
        self.cur_les = None
        self.id_phrase = ''
        self.id_stat = 0
        self.phrase_sent = ''
        self.phrase_audio = ''
        self.phrase_meaning = ''
        self.phrase_meaning_audio = ''
        self.mistake = False
        self.settings = None
        self.comport = None
        self.right_first_time_count = 0
        self.right_first_time = 10
        self.db = DB()
        self.id_stat = 0
        self.mode = None

        #  получить список того что будем учить

    def get_study_sent_id(self):
        num_new_sent = int(self.settings['sent_in_less'].get())
        right_answer = 0
        # находим предложения которые в обучении но на которые не было отвечено правильно
        list_sent_id_in_progress = self.db.get_progress_sentance(self.cur_les, self.mode, right_answer)
        self.add_sent_num = num_new_sent - len(list_sent_id_in_progress)
        if self.add_sent_num < 0:
            self.add_sent_num = 0
        # если таких предложений меньше чем количества новых в уроке добавляем из общего числа те которые еще не учились
        if self.add_sent_num > 0:
            list_sent_id_add_to_progress = self.db.get_new_sentance(self.cur_les, self.mode, self.add_sent_num)
            list_sent_id_in_progress.extend(list_sent_id_add_to_progress)
        # добавляем предложения которые нужно повторять
        for right_answer in range(1, 7):
            time_for_new_sent = self.settings[f'time_beetween_study_{right_answer}'].get()
            # print(right_answer, time_for_new_sent)
            list_sent_id_for_repiet = self.db.get_progress_sentance(self.cur_les, self.mode, right_answer,
                                                                    time_for_new_sent)
            list_sent_id_in_progress.extend(list_sent_id_for_repiet)
        return list_sent_id_in_progress

    def get_short_study_sent_id(self):
        self.add_sent_num = 0
        # находим предложения которые в обучении но на которые не было отвечено правильно
        list_sent_id_in_progress = [] # self.db.get_progress_sentance(self.cur_les, self.mode, 0)
        for right_answer in range(1, 2):
            time_for_new_sent = self.settings[f'time_beetween_study_{right_answer}'].get()
            # print(right_answer, time_for_new_sent)
            list_sent_id_for_repiet = self.db.get_progress_sentance(self.cur_les, self.mode, right_answer,
                                                                    time_for_new_sent)
            list_sent_id_in_progress.extend(list_sent_id_for_repiet)
        return list_sent_id_in_progress

        # получаем все пердложения в уроке

    def get_study_data(self, study_id_sent_list):
        for each in self.db.get_sent_data(study_id_sent_list):
            yield each

    # открыть окно с подсказкой
    def open_window_help(self, text, delay):
        # закрыть окно с подсказкой
        def close_window(window):
            window.destroy()
            # root.deiconify()
            self.meaning.config(state="normal")
            # root.attributes('-disabled', False)

        # Создаем новое окно
        new_window = tk.Toplevel(self.root)
        center_window(new_window, 200, 100)
        # Добавляем текстовую метку в новое окно
        label = tk.Label(new_window, text=text, font=("Arial", 12))
        label.pack()
        self.meaning.config(state="disabled")
        # root.iconify()  # .attributes('-disabled', True)

        new_window.after(100, lambda: play_sound(f'audio\\{self.phrase_audio}.mp3'))
        new_window.after(delay, lambda: close_window(new_window))

    # заполнить переменные содержащие обучающий материал если они закончились закрыть окно
    def next_sent(self):
        try:
            self.mistake = False
            next_phrase = next(self.study_data)
            self.id_phrase = next_phrase['id']
            self.phrase_sent = next_phrase['study_phrase']
            self.phrase_audio = next_phrase['phrase_audio']
            self.phrase_meaning = next_phrase['phrase_meaning']
            self.phrase_meaning_audio = next_phrase['meaning_audio']
            self.phrase.config(text=self.phrase_meaning)
            self.root.after(100, play_sound(f'audio\\{self.phrase_meaning_audio}.mp3'))
            self.root.after(100, play_sound(f'audio\\{self.phrase_audio}.mp3'))
            if self.db.is_show_first_time(self.id_phrase, self.cur_les, self.mode):
                self.open_window_help(self.phrase_sent, int(self.settings['show_time_sent'].get()))
        except StopIteration:
            self.db.save_statistic(self.id_stat, self.right_answer_count, self.shock_count, self.total_answer,
                                   self.add_sent_num)
            self.root.destroy()
            if len(self.get_short_study_sent_id()) > 0:
                self.main_win.after(self.settings['time_beetween_study_1'].get(),
                                    self.show_study_window(self.cur_les, self.settings, short=True))
            self.main_win.attributes('-disabled', False)

    def show_study_window(self, cur_les, settings, short=False):
        # действия при закрытии окна обучения
        def on_closing():
            self.comport.close()
            self.db.save_statistic(self.id_stat, self.right_answer_count, self.shock_count, self.total_answer,
                                   self.add_sent_num)
            self.main_win.attributes('-disabled', False)
            self.main_win.deiconify()
            self.root.destroy()

        # действия при вводе ответа
        def on_entry_change(event):
            # Получаем текущий текст из строки ввода
            text = self.meaning.get()
            text_len = len(text)
            if self.mode == '2':
                text = unidecode(text)
                self.phrase_sent = unidecode(self.phrase_sent)
            if (text_len > 0) and (text[text_len - 1].lower() != self.phrase_sent[text_len - 1].lower()):
                self.meaning.delete(0, tk.END)
                self.meaning.insert(0, text[0:text_len - 1])
                self.open_window_help(self.phrase_sent, int(self.settings['show_time_sent'].get()))
                if self.db.is_show_first_time(self.id_phrase, self.cur_les, self.mode):
                    if self.right_first_time_count >= self.right_first_time // 2:
                        self.comport.send_data(b'Shock100\n')
                        self.shock_count += 1
                        print('Shock')
                else:
                    self.comport.send_data(b'Shock100\n')
                    self.shock_count += 1
                    print('Shock')

                self.db.inc_dec_right_count(self.id_phrase, self.cur_les, self.mode, inc=False)
                self.mistake = True
                self.right_first_time_count = 0
            elif text_len == len(self.phrase_sent):
                self.meaning.delete(0, tk.END)
                if not self.mistake:
                    if self.right_first_time_count >= self.right_first_time:
                        self.db.inc_dec_right_count(self.id_phrase, self.cur_les, self.mode, inc=True)
                        self.comport.send_data(b'Viber1000\n')
                        self.right_answer_count += 1
                        print('Viber')
                        self.right_first_time_count = 0
                        play_sound(f'audio\\{self.phrase_audio}.mp3')
                        self.total_answer += 1
                        self.next_sent()
                    else:
                        self.right_first_time_count += 1
                        play_sound(f'audio\\{self.phrase_audio}.mp3')
                else:
                    self.total_answer += 1
                    self.next_sent()

        def on_help():
            if not self.help_flag:
                self.help_flag = True
                self.db.inc_dec_right_count(self.id_phrase, self.cur_les, self.mode, inc=False)
                self.db.inc_dec_right_count(self.id_phrase, self.cur_les, self.mode, inc=False)
            self.open_window_help(self.phrase_sent, int(self.settings['show_time_sent'].get()))

        self.total_answer = 0
        self.right_answer_count = 0
        self.shock_count = 0
        self.cur_les = cur_les
        self.settings = settings
        self.mode = self.settings['mode'].get()
        self.comport = SerialDevice(settings['comport'].get())
        self.comport.open()
        if short:
            study_sent_list = self.get_short_study_sent_id()
        else:
            study_sent_list = self.get_study_sent_id()
        self.study_data = self.get_study_data(study_sent_list)
        self.id_stat = self.db.insert_new_statistic(self.cur_les, self.mode)
        self.main_win.attributes('-disabled', True)
        self.main_win.iconify()
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", on_closing)
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
        self.phrase = tk.Label(self.root, text='', font=("Arial", 12))
        self.phrase.grid(row=1, column=2, padx=3, pady=3)
        tk.Label(self.root, text="Значение:").grid(row=2, column=1, padx=3, pady=3)
        self.meaning = tk.Entry(self.root, width=30, font=("Arial", 12))
        self.meaning.grid(row=2, column=2, padx=3, pady=3)
        self.meaning.bind("<KeyRelease>", on_entry_change)
        self.help = tk.Button(self.root, text='Помощь', command=on_help)
        self.help.grid(row=2, column=3, padx=3, pady=3)
        self.next_sent()

        self.root.mainloop()
