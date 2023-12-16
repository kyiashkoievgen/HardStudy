from db import DB
from unidecode import unidecode
from random import shuffle
import re


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

    def phrase_to_dict(self):
        return {
            'id_phrase': self.id_phrase,
            'phrase_sent': self.phrase_sent,
            'phrase_audio': self.phrase_audio,
            'phrase_meaning': self.phrase_meaning,
            'phrase_meaning_audio': self.phrase_meaning_audio,
            'was_help_flag': self.was_help_flag,
            'was_help_sound_flag': self.was_help_sound_flag,
            'was_mistake_flag': self.was_mistake_flag,
            'inc_flag': self.inc_flag,
            'dec_flag': self.dec_flag
        }


class Study:
    def __init__(self):
        self.time_pause = None
        self.time_start = None
        self.time_stop = None
        self.duration = None
        self.shock_count = None
        self.know_phrase = None
        self.db = DB()
        self.phrase_list = []
        self.add_sent_num = 0
        self.meaning = None
        self.phrase = None
        self.study_data = None
        self.cur_les = []
        self.id_phrase = ''
        self.cur_les_data = Phrase(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.settings = self.db.app_setting_init()

    #  получить список того что будем учить
    def get_study_sent(self):
        self.know_phrase = set()
        num_new_sent = int(self.settings['sent_in_less'])
        right_answer = 0

        # находим предложения которые в обучении но на которые не было отвечено правильно
        list_sent_id_in_progress = self.db.get_progress_sentance(self.cur_les, right_answer,
                                                                 int(self.settings['right_answer_2']))
        self.add_sent_num = num_new_sent - len(list_sent_id_in_progress)
        if self.add_sent_num < 0:
            self.add_sent_num = 0
        # если таких предложений меньше чем количества новых в уроке добавляем из общего числа те которые еще не учились
        if self.add_sent_num > 0:
            list_sent_id_add_to_progress = self.db.get_new_sentance(self.cur_les, self.add_sent_num)
            list_sent_id_in_progress.extend(list_sent_id_add_to_progress)
            self.add_sent_num = len(list_sent_id_add_to_progress)

        # добавляем в урок предложения с нулевым количеством правильных ответов в количестве 10шт
        z_study = self.db.get_sent_data(list_sent_id_in_progress)
        for each in z_study:
            for i in range(0, int(self.settings['right_answer_1'])):
                if i == 0:
                    self.phrase_list.append(
                        # если хоть одно из 10 предложений введено правильно увеличиваем счетчик правильных ответов
                        Phrase(each['id'], each['study_phrase'], each['phrase_audio'], each['phrase_meaning'],
                               each['meaning_audio'], False, False, False, True, True)
                    )
                else:
                    self.phrase_list.append(
                        # если хоть одно из 10 предложений введено правильно увеличиваем счетчик правильных ответов
                        # при неправильном ответе ничего на убавляется так как и так их 0
                        Phrase(each['id'], each['study_phrase'], each['phrase_audio'], each['phrase_meaning'],
                               each['meaning_audio'], False, False, False, True, False)
                    )

        # добавляем в урок предложения с нулевым количеством правильных ответов для тестирования их изучения
        for each in z_study:
            self.phrase_list.append(
                Phrase(each['id'], each['study_phrase'], each['phrase_audio'], each['phrase_meaning'],
                       each['meaning_audio'], False, False, False, True, True)
            )

        # добавляем предложения которые нужно повторять
        # предложения которые были отвечены правильно 3 раза повторяем 5 раз если при показе в первый раз была ошибка
        # то уменьшаем количество правильных ответов последующие разы не уменьшаем счетчик правильных ответов
        list_sent_id_for_repiet = []
        for right_answer in range(1, 4):
            time_for_new_sent = self.settings[f'time_beetween_study_{right_answer}']
            # print(right_answer, time_for_new_sent)
            list_sent_id_for_repiet.extend(self.db.get_progress_sentance(self.cur_les, right_answer,
                                                                         int(self.settings['right_answer_2']),
                                                                         time_for_new_sent))
        if len(list_sent_id_for_repiet) > 0:
            for each in self.db.get_sent_data(list_sent_id_for_repiet):
                for i in range(0, int(self.settings['right_answer_2'])):
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
            time_for_new_sent = self.settings[f'time_beetween_study_{right_answer}']
            # print(right_answer, time_for_new_sent)
            list_sent_id_for_repiet.extend(self.db.get_progress_sentance(self.cur_les, right_answer,
                                                                         int(self.settings['right_answer_2']),
                                                                         time_for_new_sent))
        if len(list_sent_id_for_repiet) == 0:
            list_sent_id_for_repiet = self.db.get_remember_sent(self.cur_les)
        if len(list_sent_id_for_repiet) > 0:
            repeat_for_understanding = self.db.get_sent_data(list_sent_id_for_repiet)
            for each in repeat_for_understanding:
                self.phrase_list.append(
                    Phrase(each['id'], each['study_phrase'], each['phrase_audio'], each['phrase_meaning'],
                           each['meaning_audio'], False, False, False, True, True)
                )

            for i in range(0, int(self.settings['right_answer_2']) - 1):
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
                        self.db.inc_dec_right_count(each.id_phrase, self.cur_les[0], inc=True, remember=rem)  # !!!!!
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
                self.db.inc_dec_right_count(int(key), self.cur_les[0], inc=True, remember=rem_list[key])
        for key in dec_list.keys():
            if dec_list[key]:
                self.db.inc_dec_right_count(int(key), self.cur_les[0], inc=False, remember=rem_list[key])

        total_shows_now = len(self.phrase_list)
        total_sent_now = len(all_id)
        total_word_now = len(all_word)
        new_sent_now = self.add_sent_num
        total_shock_now = self.shock_count
        all_studied = self.db.get_studied_sent_word(self.cur_les)[0]
        total_sent = len(all_studied['studied_sent'])
        total_word = len(all_studied['studied_word'])
        self.db.save_statistic(self.cur_les, total_shows_now, total_sent_now, total_word_now, right_answer,
                               new_sent_now, total_shock_now, self.duration, total_sent, total_word,
                               self.time_start, self.time_stop, all_studied['full_understand'])

        # print('inc-', inc_list)
        # print('---------------------')
        # print('dec-', dec_list)
        # print('---------------------')
        # print('rem-', rem_list)
        # print('---------------------------------------------------------------------')


class WebStudy(Study):
    def __init__(self, list_sent_id):
        super().__init__()
        self.cur_les = list_sent_id
        self.db.set_default_lesson(self.cur_les)

    def get_study_data_as_list(self):
        self.get_study_sent()
        result = []
        for phrase in self.phrase_list:
            phrase_dict = phrase.phrase_to_dict()
            # если не учитываем апострофические знаки
            if self.settings['apostrophe'] == "False":
                phrase_dict['phrase_sent'] = unidecode(phrase_dict['phrase_sent'])
            result.append(phrase_dict)
        return result, self.add_sent_num

    def save_progress_from_web(self, phrase_list, add_sent_num, shock_count, time_start, time_stop, duration):
        self.add_sent_num = add_sent_num
        self.shock_count = shock_count
        self.time_start = time_start
        self.time_stop = time_stop
        self.duration = duration
        for phrase in phrase_list:
            self.phrase_list.append(
                Phrase(phrase['id_phrase'], phrase['phrase_sent'], '', '', '', phrase['was_help_flag'],
                       phrase['was_help_sound_flag'], phrase['was_mistake_flag'],
                       phrase['inc_flag'], phrase['dec_flag']))
        self.progress_save()
        return self.db.get_statistic()
