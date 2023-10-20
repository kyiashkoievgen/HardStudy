import tkinter as tk
from db import DB
from voice_unit import play_sound
from comport import SerialDevice
from unidecode import unidecode
from random import shuffle


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
        self.sent_remember_count = None
        self.pause_time = 60000
        self.help_flag = False
        self.sound_help_flag = False
        self.help = None
        self.add_sent_num = 0
        self.right_answer_count_in_lesson = 0
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
        self.right_answer_count = 0
        self.right_answer = 10
        self.db = DB()
        self.id_stat = 0
        self.mode = None
        self.remember = True

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

    # получить короткий список фраз для повторения
    def get_short_study_sent_id(self):
        self.add_sent_num = 0
        # находим предложения которые в обучении но на которые не было отвечено правильно
        # self.db.get_progress_sentance(self.cur_les, self.mode, 0)
        list_sent_id_in_progress = []
        # находим предложения на которые было один раз отвечено правильно
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
        self.sound_help_flag = True
        new_window.after(100, lambda: play_sound(f'audio\\{self.phrase_audio}.mp3'))
        new_window.after(delay, lambda: close_window(new_window))

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
            self.sound_help_flag = False
            self.help_flag = False
            # self.root.after(100, play_sound(f'audio\\{self.phrase_audio}.mp3'))
            # если количество правильных ответов 0 то показываем подсказку
            if self.db.is_show_first_time(self.id_phrase, self.cur_les, self.mode):
                print('first')
                self.open_window_help(self.phrase_sent, int(self.settings['show_time_sent'].get()))
                self.right_answer = int(self.settings['right_answer_1'].get())
            else:
                self.right_answer = int(self.settings['right_answer_2'].get())
        except StopIteration:
            # self.db.save_statistic(self.id_stat, self.right_answer_count_in_lesson, self.shock_count, self.total_answer,
            #                       self.add_sent_num)

            self.on_closing_study_window()

            # есил есть что повторять запускаем обучение с фразами которые только что были отвечены прваельно для закрепления
            if len(self.get_short_study_sent_id()) > 0:
                self.main_win.after(self.settings['time_beetween_study_1'].get(),
                                    self.show_study_window(self.cur_les, self.settings, short=True))

    def on_closing_study_window(self):
        self.comport.close()
        self.db.save_statistic(self.id_stat, self.right_answer_count_in_lesson, self.shock_count, self.total_answer,
                               self.add_sent_num)
        self.total_answer = 0
        self.shock_count = 0
        self.right_answer_count_in_lesson = 0
        self.add_sent_num = 0
        self.main_win.attributes('-disabled', False)
        self.main_win.deiconify()
        self.root.destroy()

    def show_study_window(self, cur_les, settings, short=False):
        # действия при закрытии окна обучения

        def on_entry_change_remember(event):
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
                self.shock_count += 1
                print('Shock')

            # если все правильно проверяем окончание фразы
            elif text_len == len(self.phrase_sent):
                self.meaning.delete(0, tk.END)
                # если слово было введено правильно без произведения звуковой подсказки то показываем одни раз
                if self.help_flag:
                    self.study_data[self.sent_remember_count]['remember'] = 0
                elif self.sound_help_flag:
                    if not self.study_data[self.sent_remember_count]['remember'] == 0:
                        self.study_data[self.sent_remember_count]['remember'] -= 1
                else:
                    self.study_data[self.sent_remember_count]['remember'] += 1
                    if self.study_data[self.sent_remember_count]['remember'] == 5:
                        self.open_window_pause()

                self.help_flag = False
                self.sound_help_flag = False
                self.next_sent_remember()

        # действия при вводе ответа
        def on_entry_change_study(event):
            # Получаем текущий текст из строки ввода
            text = self.meaning.get()
            text_len = len(text)
            # режим 2 не учитывает апострофические знаки
            if self.settings['apostrophe']:
                text = unidecode(text)
                self.phrase_sent = unidecode(self.phrase_sent)
            # проверка правильности введенного символа
            if (text_len > 0) and (text[text_len - 1].lower() != self.phrase_sent[text_len - 1].lower()):
                # если не правильно то удаляем этот символ и Shock
                self.meaning.delete(0, tk.END)
                self.meaning.insert(0, text[0:text_len - 1])
                self.comport.send_data(b'Shock100\n')
                self.shock_count += 1
                print('Shock')
                #self.open_window_help(self.phrase_sent, int(self.settings['show_time_sent'].get()))
                # if self.db.is_show_first_time(self.id_phrase, self.cur_les, self.mode):
                #     # если слово вводится правильно первый раз но уже было введено без ошибок то шок
                #     if self.right_answer_count >= int(self.settings['right_answer_2'].get()):
                #         self.comport.send_data(b'Shock100\n')
                #         self.shock_count += 1
                #         print('Shock')
                # else:
                #     # если слово было до этого уже введено правильно то шок
                #     self.comport.send_data(b'Shock100\n')
                #     self.shock_count += 1
                #     print('Shock')
                if self.right_answer_count < 2 and not self.mistake:
                    self.db.inc_dec_right_count(self.id_phrase, self.cur_les, self.mode, inc=False)
                self.mistake = True
            # если все правильно проверяем окончание фразы
            elif text_len == len(self.phrase_sent):
                self.meaning.delete(0, tk.END)
                # если слово было введено правильно без произведения звуковой подсказки то показываем одни раз
                if not self.sound_help_flag:
                    self.right_answer_count = self.right_answer
                # проверяем количество повторов если повторов столько сколько нужно то следующее предложение
                if self.right_answer_count == self.right_answer:
                    # проверяем были ли ошибки
                    if self.mistake:
                        #self.db.inc_dec_right_count(self.id_phrase, self.cur_les, self.mode, inc=False)
                        self.next_sent()
                    else:
                        self.db.inc_dec_right_count(self.id_phrase, self.cur_les, self.mode,
                                                    inc=True, remember=not self.sound_help_flag)
                        self.comport.send_data(b'Viber1000\n')
                        print('Viber')
                        self.right_answer_count_in_lesson += 1
                        self.next_sent()
                        self.open_window_pause()
                    self.right_answer_count = 0
                    self.total_answer += 1
                else:
                    self.right_answer_count += 1
                    play_sound(f'audio\\{self.phrase_audio}.mp3')

                # else:
                # self.next_sent()

        def on_help():
            if not self.help_flag:
                self.help_flag = True
                self.db.inc_dec_right_count(self.id_phrase, self.cur_les, self.mode, inc=False)
                self.db.inc_dec_right_count(self.id_phrase, self.cur_les, self.mode, inc=False)
            self.open_window_help(self.phrase_sent, int(self.settings['show_time_sent'].get()))

        def on_speak():
            self.sound_help_flag = True
            play_sound(f'audio\\{self.phrase_audio}.mp3')

        self.total_answer = 0
        self.right_answer_count = 0
        self.shock_count = 0
        self.cur_les = cur_les
        self.settings = settings
        self.mode = self.settings['mode'].get()
        self.comport = SerialDevice(settings['comport'].get())
        self.comport.open()
        self.id_stat = self.db.insert_new_statistic(self.cur_les, self.mode)
        self.main_win.attributes('-disabled', True)
        self.main_win.iconify()
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing_study_window)
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
        tk.Button(self.root, text='Помощь', command=on_help).grid(row=2, column=3, padx=3, pady=3)
        tk.Button(self.root, text='Произнести', command=on_speak).grid(row=2, column=4, padx=3, pady=3)

        if self.remember:
            self.study_data = self.db.get_remember_sent(self.cur_les, self.mode,
                                                        n=int(self.settings['sent_in_less'].get()))
            self.meaning.bind("<KeyRelease>", on_entry_change_remember)
            self.sent_remember_count = 0
            self.next_sent_remember()
        else:
            if short:
                self.study_data = self.get_study_data(self.get_short_study_sent_id())
            else:
                self.study_data = self.get_study_data(self.get_study_sent_id())

            self.meaning.bind("<KeyRelease>", on_entry_change_study)
            self.next_sent()

        self.root.mainloop()

    def next_sent_remember(self):
        finish: bool = True
        for each in self.study_data:
            if each['remember'] < 5:
                finish = False
        if not finish:
            next_phrase = self.study_data[self.sent_remember_count]
            self.id_phrase = next_phrase['id']
            self.phrase_sent = next_phrase['study_phrase']
            self.phrase_audio = next_phrase['phrase_audio']
            self.phrase_meaning = next_phrase['phrase_meaning']
            self.phrase_meaning_audio = next_phrase['meaning_audio']
            self.phrase.config(text=self.phrase_meaning)
            self.root.after(100, play_sound(f'audio\\{self.phrase_meaning_audio}.mp3'))
            self.sound_help_flag = False
            self.help_flag = False

            self.sent_remember_count += 1
            if self.sent_remember_count == len(self.study_data):
                self.sent_remember_count = 0
                shuffle(self.study_data)

        else:
            self.on_closing_study_window()
            self.remember = False
            self.show_study_window(self.cur_les, self.settings)
