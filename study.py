from datetime import datetime, timedelta
import tkinter as tk
from db import DB
from voice_unit import play_sound
from comport import SerialDevice
from unidecode import unidecode
from random import shuffle
import re


def center_window(window, width, height, dx=0, dy=0):
    # Получите ширину и высоту экрана
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Вычислите координаты центра родительского окна
    center_x = int((screen_width - width) / 2) + dx
    center_y = int((screen_height - height) / 2) + dy

    # Установите координаты и размеры дочернего окна для позиционирования его по центру
    window.geometry(f"{width}x{height}+{center_x}+{center_y}")


class Phrase:
    def __init__(self, id_phrase, phrase_sent, phrase_audio, phrase_meaning, phrase_meaning_audio, was_help_flag,
                 was_help_sound_flag, was_mistake_flag, inc_flag, dec_flag):
        self.id_phrase = id_phrase
        self.phrase_sent = phrase_sent
        self.phrase_audio = phrase_audio
        self.phrase_meaning = phrase_meaning
        self.phrase_meaning_audio = phrase_meaning_audio
        self.was_help_flag = was_help_flag
        self.was_help_sound_flag = was_help_sound_flag
        self.was_mistake_flag = was_mistake_flag
        self.inc_flag = inc_flag
        self.dec_flag = dec_flag


class Study:
    def __init__(self, main_win):
        self.pred_time = None
        self.time_pause = None
        self.time_start = None
        self.time_count = 0
        self.phrase_list = []
        self.pause_time = 60000
        self.help_flag = False
        self.sound_help_flag = False
        self.add_sent_num = 0
        self.right_answer_count_in_lesson = 0
        self.shock_count = 0
        self.root = None
        self.meaning = None
        self.phrase = None
        self.study_data = None
        self.main_win = main_win
        self.cur_les = None
        self.id_phrase = ''
        self.cur_les_data = Phrase(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.mistake = False
        self.settings = None
        self.comport = None
        self.db = DB()
        self.mode = None

        #  получить список того что будем учить

    def get_study_sent(self):
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
            self.add_sent_num = len(list_sent_id_add_to_progress)

        # добавляем в урок предложения с нулевым количеством правильных ответов в количестве 10шт
        z_study = self.db.get_sent_data(list_sent_id_in_progress)
        for each in z_study:
            for i in range(0, int(self.settings['right_answer_1'].get())):
                self.phrase_list.append(
                    # если хоть одно из 10 предложений введено правильно увеличиваем счетчик правильных ответов
                    # при неправильном ответе ничего на убавляется так как и так их 0
                    Phrase(each['id'], each['study_phrase'], each['phrase_audio'], each['phrase_meaning'],
                           each['meaning_audio'], False, False, False, True, False)
                )

        # добавляем предложения которые нужно повторять
        # предложения которые были отвечены правильно 3 раза повторяем 5 раз если при показе в первый раз была ошибка
        # то уменьшаем количество правильных ответов последующие разы не уменьшаем счетчик правильных ответов
        list_sent_id_for_repiet = []
        for right_answer in range(1, 4):
            time_for_new_sent = self.settings[f'time_beetween_study_{right_answer}'].get()
            # print(right_answer, time_for_new_sent)
            list_sent_id_for_repiet.extend(self.db.get_progress_sentance(self.cur_les, self.mode, right_answer,
                                                                         time_for_new_sent))
        if len(list_sent_id_for_repiet) > 0:
            for each in self.db.get_sent_data(list_sent_id_for_repiet):
                for i in range(0, int(self.settings['right_answer_2'].get())):
                    if i == 0:
                        self.phrase_list.append(
                            # если 1-е предложений введено правильно увеличиваем счетчик правильных ответов
                            # при неправильном ответе уменьшаем
                            Phrase(each['id'], each['study_phrase'], each['phrase_audio'], each['phrase_meaning'],
                                   each['meaning_audio'], False, False, False, True, True)
                        )
                    else:
                        self.phrase_list.append(
                            # последующие ответы не влияют на счетчик правильных ответов мотивация через никотин и шок
                            Phrase(each['id'], each['study_phrase'], each['phrase_audio'], each['phrase_meaning'],
                                   each['meaning_audio'], False, False, False, False, False)
                        )

        # предложения которые были отвечены правильно больше 4 раз повторяем 5 раз
        # если при показе в первый раз была ошибка то уменьшаем количество правильных ответов
        # последующие разы перемешиваем и они не влияют на счетчик правильных ответов
        list_sent_id_for_repiet = []
        for right_answer in range(4, 7):
            time_for_new_sent = self.settings[f'time_beetween_study_{right_answer}'].get()
            # print(right_answer, time_for_new_sent)
            list_sent_id_for_repiet.extend(self.db.get_progress_sentance(self.cur_les, self.mode, right_answer,
                                                                         time_for_new_sent))
        if len(list_sent_id_for_repiet) == 0:
            list_sent_id_for_repiet = self.db.get_remember_sent(self.cur_les, self.mode)
        if len(list_sent_id_for_repiet) > 0:
            repeat_for_understanding = self.db.get_sent_data(list_sent_id_for_repiet)
            for each in repeat_for_understanding:
                self.phrase_list.append(
                    Phrase(each['id'], each['study_phrase'], each['phrase_audio'], each['phrase_meaning'],
                           each['meaning_audio'], False, False, False, True, True)
                )

            for i in range(0, int(self.settings['right_answer_2'].get()) - 1):
                shuffle(repeat_for_understanding)
                for each in repeat_for_understanding:
                    self.phrase_list.append(
                        Phrase(each['id'], each['study_phrase'], each['phrase_audio'], each['phrase_meaning'],
                               each['meaning_audio'], False, False, False, False, False)
                    )

        # добавляем в урок предложения с нулевым количеством правильных ответов для тестирования их изучения
        for each in z_study:
            self.phrase_list.append(
                Phrase(each['id'], each['study_phrase'], each['phrase_audio'], each['phrase_meaning'],
                       each['meaning_audio'], False, False, False, True, True)
            )

    # получаем все пердложения в уроке
    def get_study_data(self):
        for each in self.phrase_list:
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
        new_window.after(100, lambda: play_sound(f'audio\\{self.cur_les_data.phrase_audio}.mp3'))
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
    def next_sent(self, next_id=False):
        try:
            if next_id:
                id_sent = self.cur_les_data.id_phrase
                while id_sent == self.cur_les_data.id_phrase:
                    self.cur_les_data = next(self.study_data)
            else:
                self.cur_les_data = next(self.study_data)

            self.phrase.config(text=self.cur_les_data.phrase_meaning)
            self.root.after(100, play_sound(f'audio\\{self.cur_les_data.phrase_meaning_audio}.mp3'))
            self.sound_help_flag = False
            self.help_flag = False
            self.mistake = False

        except StopIteration:
            self.progress_save()
            self.on_closing_study_window()

    def progress_save(self):
        inc_list = dict()
        dec_list = dict()
        rem_list = dict()
        all_id = set()
        all_word = set()
        right_answer = 0
        # если в предложении each.inc_flag поднят только этот атрибут то значит что предложение училось только в первом
        # режиме для вновь прибывших предложений, и в последнем режиме пройдет проверка на знание этого предложения
        # в первом режиме можно только увеличить счетчик правильных ответов что бы в режим проверки не зависел от
        # режима пред обучения проверяем поднят ли флаг each.dec_flag и есть ли уже фраза в inc_list если есть то
        # увеличиваем счетчик и удаляем из списка что бы потом заново внести
        for each in self.phrase_list:
            all_id.add(each.id_phrase)
            for word in re.findall('(\\w+)', each.phrase_sent):
                all_word.add(word)

            if each.inc_flag:
                if each.dec_flag and (f'{each.id_phrase}' in inc_list):
                    if not (each.was_mistake_flag or each.was_help_flag):
                        right_answer += 1
                        rem = not (each.was_mistake_flag or each.was_help_sound_flag or each.was_help_flag)
                        self.db.inc_dec_right_count(each.id_phrase, self.cur_les, self.mode, inc=True, remember=rem)
                    del (inc_list[f'{each.id_phrase}'])
                if not (f'{each.id_phrase}' in inc_list):
                    inc_list[f'{each.id_phrase}'] = not (each.was_mistake_flag or each.was_help_flag)
                else:
                    inc_list[f'{each.id_phrase}'] = inc_list[f'{each.id_phrase}'] and not \
                        (each.was_mistake_flag or each.was_help_flag)
                if not (f'{each.id_phrase}' in rem_list):
                    rem_list[f'{each.id_phrase}'] = not (each.was_mistake_flag or each.was_help_sound_flag
                                                         or each.was_help_flag)
                else:
                    rem_list[f'{each.id_phrase}'] = rem_list[f'{each.id_phrase}'] and \
                                                    (not (each.was_mistake_flag or each.was_help_sound_flag or
                                                          each.was_help_flag))
            if each.dec_flag:
                if not (f'{each.id_phrase}' in dec_list):
                    dec_list[f'{each.id_phrase}'] = each.was_mistake_flag or each.was_help_flag
                else:
                    dec_list[f'{each.id_phrase}'] = dec_list[f'{each.id_phrase}'] or \
                                                    (each.was_mistake_flag or each.was_help_flag)
                if not (f'{each.id_phrase}' in rem_list):
                    rem_list[f'{each.id_phrase}'] = not (each.was_mistake_flag or each.was_help_sound_flag
                                                         or each.was_help_flag)

        for key in inc_list.keys():
            if inc_list[key]:
                right_answer += 1
                self.db.inc_dec_right_count(int(key), self.cur_les, self.mode, inc=True, remember=rem_list[key])
        for key in dec_list.keys():
            if dec_list[key]:
                self.db.inc_dec_right_count(int(key), self.cur_les, self.mode, inc=False, remember=rem_list[key])

        total_shows_now = len(self.phrase_list)
        total_sent_now = len(all_id)
        total_word_now = len(all_word)
        new_sent_now = self.add_sent_num
        total_shock_now = self.shock_count
        all_sent, all_words = self.db.get_studied_sent_word([self.cur_les], self.mode)
        total_sent = len(all_sent)
        total_word = len(all_words)
        total_time_now = (datetime.now() - self.time_start - timedelta(seconds=self.time_pause)).seconds
        self.db.save_statistic(self.cur_les, total_shows_now, total_sent_now, total_word_now, right_answer,
                               new_sent_now, total_shock_now, total_time_now, total_sent, total_word)

        # print('inc-', inc_list)
        # print('---------------------')
        # print('dec-', dec_list)
        # print('---------------------')
        # print('rem-', rem_list)
        # print('---------------------------------------------------------------------')

    def on_closing_study_window(self):
        self.comport.close()
        self.shock_count = 0
        self.right_answer_count_in_lesson = 0
        self.add_sent_num = 0
        self.main_win.attributes('-disabled', False)
        self.main_win.deiconify()
        self.root.destroy()

    def show_study_window(self, cur_les, settings, short=False):

        # действия при вводе ответа
        def on_entry_change_study(event):
            delta_time = (datetime.now() - self.pred_time).seconds
            if delta_time > 180:
                self.time_pause += delta_time
            self.pred_time = datetime.now()
            # Получаем текущий текст из строки ввода
            text = self.meaning.get()
            text_len = len(text)
            # режим 2 не учитывает апострофические знаки
            if self.settings['apostrophe']:
                text = unidecode(text)
                self.cur_les_data.phrase_sent = unidecode(self.cur_les_data.phrase_sent)
            # проверка правильности введенного символа
            if (text_len > 0) and (text[text_len - 1].lower() != self.cur_les_data.phrase_sent[text_len - 1].lower()):
                # если не правильно то удаляем этот символ и Shock
                self.meaning.delete(0, tk.END)
                self.meaning.insert(0, text[0:text_len - 1])
                self.comport.send_data(b'Shock100\n')
                self.shock_count += 1
                print('Shock')
                self.mistake = True

            # если все правильно проверяем окончание фразы
            elif text_len == len(self.cur_les_data.phrase_sent):
                self.meaning.delete(0, tk.END)

                # проверяем были ли ошибки
                if self.mistake:
                    self.right_answer_count_in_lesson = 0
                    self.mistake = False
                    self.cur_les_data.was_mistake_flag = True

                else:
                    self.cur_les_data.was_mistake_flag = False
                    self.right_answer_count_in_lesson += 1
                    if self.right_answer_count_in_lesson == 5:
                        self.open_window_pause()
                        self.right_answer_count_in_lesson = 0

                play_sound(f'audio\\{self.cur_les_data.phrase_audio}.mp3')
                # если слово было введено правильно без произведения звуковой подсказки то показываем одни раз

                self.cur_les_data.was_help_flag = self.help_flag
                self.cur_les_data.was_help_sound_flag = self.sound_help_flag

                # for each in self.phrase_list:
                #     print(each.phrase_sent, each.was_help_flag, each.was_help_sound_flag, each.was_mistake_flag,
                #           each.inc_flag, each.dec_flag)
                # print('-------------------------------------------------------------')

                if not (self.sound_help_flag or self.help_flag) and self.cur_les_data.dec_flag:
                    self.next_sent(next_id=True)
                else:
                    self.next_sent(next_id=False)

        def on_help():
            if not self.help_flag:
                self.help_flag = True
            self.open_window_help(self.cur_les_data.phrase_sent, int(self.settings['show_time_sent'].get()))

        def on_speak():
            self.sound_help_flag = True
            play_sound(f'audio\\{self.cur_les_data.phrase_audio}.mp3')

        self.time_start = datetime.now()
        self.pred_time = datetime.now()
        self.time_pause = 0
        self.shock_count = 0
        self.cur_les = cur_les
        self.settings = settings
        self.mode = self.settings['mode'].get()
        self.comport = SerialDevice(settings['comport'].get())
        self.comport.open()
        # self.id_stat = self.db.insert_new_statistic(self.cur_les, self.mode)
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

        self.get_study_sent()
        self.meaning.bind("<KeyRelease>", on_entry_change_study)
        self.study_data = self.get_study_data()
        self.next_sent()

        self.root.mainloop()
