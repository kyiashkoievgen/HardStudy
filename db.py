import re
import sqlite3
from datetime import datetime, timedelta
from random import shuffle


class DB:
    def __init__(self):
        self.conn = sqlite3.connect('hard_study.db')
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.conn.close()

    def fetch_lesson_name(self):
        self.cursor.execute("SELECT id, name FROM lesson_name")
        items = self.cursor.fetchall()
        return [(item[0], f'{item[0]}.{item[1]}') for item in items]

    def fetch_mode_name(self):
        self.cursor.execute("SELECT name FROM mode_study")
        items = self.cursor.fetchall()
        return [item[0] for item in items]

    #
    # def update_dropdown(self):
    #     items = self.fetch_lesson_name()
    #     self.dropdown_lesson_name['values'] = items

    def get_current_lesson(self):
        self.cursor.execute("SELECT id, name FROM lesson_name WHERE default_lesson=1")
        items = self.cursor.fetchall()
        result = ('', 'Не выбрано')
        if len(items) != 0:
            result = (items[0][0], items[0][1])
        return result

    def set_default_lesson(self, id_lesson):
        self.cursor.execute("UPDATE lesson_name SET default_lesson=0 WHERE default_lesson=1")
        self.conn.commit()
        self.cursor.execute(f"UPDATE lesson_name SET default_lesson=1 WHERE id='{id_lesson}'")
        self.conn.commit()

    def app_setting_init(self, name=''):
        if name == '':
            where_par = 'default_setting="1"'
        else:
            where_par = f'profile_name="{name}"'
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        cursor.execute(f'''
        SELECT mode_study.name, mode, comport, profile_name, lesson_per_day, time_beetween_study_1, time_beetween_study_2,
        time_beetween_study_3, time_beetween_study_4, time_beetween_study_5, time_beetween_study_6, sent_in_less,
        show_time_sent, punish_time_1, right_answer_1, right_answer_2, apostrophe         
        FROM app_settings 
        JOIN mode_study ON mode_study.id=app_settings.mode
        WHERE {where_par}
          ''')
        return cursor.fetchall()[0]
        # print(items['punish_time_3'])

    def get_mode_id(self, name):
        self.cursor.execute(f"SELECT id FROM mode_study WHERE name='{name}'")
        return self.cursor.fetchall()[0][0]

    def save_settings(self, settings):
        mode_id = self.get_mode_id(settings['name'].get())
        col_name = ''
        for key, var in settings.items():
            if key == 'name':
                col_name += f'mode="{mode_id}"'
            else:
                col_name += f', {key}="{var.get()}"'

        update_query = f'''
            UPDATE app_settings
            SET {col_name}
            WHERE default_setting="1"
        '''

        self.cursor.execute(update_query)
        self.conn.commit()

    def insert_settings(self, settings):
        mode_id = self.get_mode_id(settings['name'].get())
        col_name = ''
        val = ()
        val_q = ''
        for key, var in settings.items():
            if key == 'name':
                col_name += f'mode'
                val += (f'{mode_id}',)
                val_q += '?'
            else:
                col_name += f', {key}'
                val += (var.get(),)
                val_q += ', ?'
        print(col_name, val)
        self.cursor.execute(f'INSERT INTO app_settings ({col_name}) VALUES ({val_q})', val)
        self.conn.commit()
        last_id = self.cursor.lastrowid
        self.cursor.execute('UPDATE app_settings SET default_setting="0" WHERE default_setting="1"')
        self.conn.commit()
        self.cursor.execute(f'UPDATE app_settings SET default_setting="1" WHERE id="{last_id}"')
        self.conn.commit()

    def get_settings_profile(self):
        self.cursor.execute("SELECT profile_name FROM app_settings")
        items = self.cursor.fetchall()
        return [item[0] for item in items]

    def get_progress_sentance(self, cur_les, mode_id, right_answer, time_for_new_sent=None):
        if time_for_new_sent is None:
            self.cursor.execute('''
                SELECT sentance_id 
                FROM lesson_progress
                WHERE lesson_id=? AND mode_id=? AND right_count=? 
            ''', (cur_les, mode_id, right_answer))
        else:
            current_date = datetime.now()
            time_ago = current_date - timedelta(minutes=int(time_for_new_sent))
            # print(time_ago)
            self.cursor.execute('''
                SELECT sentance_id 
                FROM lesson_progress
                WHERE lesson_id=? AND mode_id=? AND right_count=? AND last_show_time<=?
            ''', (cur_les, mode_id, right_answer, time_ago))

        items = self.cursor.fetchall()
        return [item[0] for item in items]

    def get_new_sentance(self, cur_les, mode_id, add_sent_num):
        self.cursor.execute('''
                        SELECT id 
                        FROM lesson_body
                        WHERE (lession_id=?) AND (id NOT IN 
                            (SELECT sentance_id FROM lesson_progress WHERE lesson_id=? AND mode_id=? ))
                        LIMIT ?
                    ''', (cur_les, cur_les, mode_id, add_sent_num))
        # print(cur_les, mode_id, add_sent_num)
        items = self.cursor.fetchall()
        return [item[0] for item in items]

    def get_sent_data(self, study_id_sent_list):
        result = []
        for id_el in study_id_sent_list:
            self.cursor.execute('''
                SELECT what_to_learn, value_in_another_language, what_to_learn_audio, value_in_another_language_audio
                FROM lesson_body
                WHERE id=?
            ''', (id_el,))
            item = self.cursor.fetchall()
            result.append({
                'id': id_el,
                'study_phrase': item[0][0].strip(),
                'phrase_meaning': item[0][1].strip(),
                'phrase_audio': item[0][2],
                'meaning_audio': item[0][3]
            })

        return result

    def is_show_first_time(self, id_phrase, lesson_id, mode_id):
        self.cursor.execute('''
                        SELECT right_count
                        FROM lesson_progress
                        WHERE sentance_id=? AND lesson_id=? AND mode_id=? AND right_count>0
                    ''', (id_phrase, lesson_id, mode_id))
        item = self.cursor.fetchall()
        if len(item) > 0:
            return False
        else:
            return True

    def inc_dec_right_count(self, id_phrase, cur_les_id, mode_id, inc, remember=False):
        if remember:
            remember = 1
        else:
            remember = 0
        # проверяем есть ли это предложение в прогрессе обучения если нет то создаем запись
        self.cursor.execute('''
                               SELECT right_count
                               FROM lesson_progress
                               WHERE sentance_id=? AND lesson_id=? AND mode_id=? 
                           ''', (id_phrase, cur_les_id, mode_id))
        item = self.cursor.fetchall()
        current_date = datetime.now()
        if len(item) == 0:
            self.cursor.execute('''INSERT INTO lesson_progress (
                       lesson_id, show_count, right_count, last_show_time, sentance_id, mode_id, remember
                   )
                   VALUES (
                       ?, 0, 0, ?, ?, ?, ?
                   )''', (cur_les_id, current_date, id_phrase, mode_id, remember))
            self.conn.commit()
        self.cursor.execute('''
                        SELECT right_count, show_count
                        FROM lesson_progress
                        WHERE sentance_id=? AND lesson_id=? AND mode_id=?
                    ''', (id_phrase, cur_les_id, mode_id))
        items = self.cursor.fetchall()
        right_count = int(items[0][0])
        show_count = int(items[0][1])
        # print(items, right_count, show_count)
        show_count += 1
        current_date = datetime.now()
        if inc and (right_count < 6):
            right_count += 1
        elif right_count != 0:
            right_count -= 1
        self.cursor.execute('''
                UPDATE lesson_progress
                SET show_count=?, right_count=?, last_show_time=?, remember=?
                WHERE sentance_id=? AND lesson_id=? AND mode_id=?
            ''', (show_count, right_count, current_date, remember, id_phrase, cur_les_id, mode_id))
        self.conn.commit()

    def insert_new_statistic(self, cur_les_id, mode_id):
        self.cursor.execute('''INSERT INTO statistic (
                   study_date, total_show, right_answer, shock, new_phrase, mode_id, study_id
               )
               VALUES (
                   ?, 0, 0, 0, 0, ?, ?
               )''', (datetime.now(), mode_id, cur_les_id))
        self.conn.commit()
        return self.cursor.lastrowid

    def save_statistic(self, cur_les, total_shows_now, total_sent_now, total_word_now, right_answer,
                       new_sent_now, total_shock_now, total_time_now, total_sent, total_word):
        self.cursor.execute('''INSERT INTO statistic (
                    study_date, total_show, right_answer, shock, new_phrase, study_id, total_sent, total_word,
                     total_time, total_word_now, total_sent_now   
                     )
                     VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                        )
                   ''', (datetime.now(), total_shows_now, right_answer, total_shock_now, new_sent_now, cur_les,
                         total_sent, total_word, total_time_now, total_word_now, total_sent_now))
        self.conn.commit()

    def get_remember_sent(self, cur_les, mode_id, n=5, trigger_know=4):
        self.cursor.execute('''
                SELECT sentance_id 
                FROM lesson_progress
                WHERE lesson_id=? AND mode_id=? AND right_count>=? AND remember=0
            ''', (cur_les, mode_id, trigger_know))

        items = self.cursor.fetchall()
        shuffle(items)
        result = []
        if len(items) > n:
            for i in range(n):
                result.append(items[i])
        else:
            result = items

        return result

    def get_lang_list(self):
        self.cursor.execute('''
            SELECT name, code
            FROM languages
        ''')
        items = self.cursor.fetchall()

        return [item[1] for item in items]

    def get_lesson_mode(self, current_lesson_id):
        self.cursor.execute(f"SELECT mode FROM lesson_name WHERE id='{current_lesson_id}'")
        return self.cursor.fetchall()[0][0]

    def get_video_study_data(self, cur_les, limit=''):
        result = []
        self.cursor.execute(f'''
                SELECT id, video_id, start_time, stop_time, first_leng, sec_leng
                FROM video_study
                WHERE lesson_id=? AND NOT (first_leng IS NULL OR sec_leng IS NULL OR first_leng='music') AND studied=0
                {limit} 
            ''', (cur_les,))
        items = self.cursor.fetchall()
        if len(items) == 0:
            self.cursor.execute('''
                UPDATE video_study
                SET studied=0
                WHERE studied=1
            ''')
            self.cursor.execute(f'''
                           SELECT id, video_id, start_time, stop_time, first_leng, sec_leng
                           FROM video_study
                           WHERE lesson_id=? AND NOT (first_leng IS NULL OR sec_leng IS NULL OR first_leng='music') AND studied=0
                           {limit} 
                       ''', (cur_les,))
            items = self.cursor.fetchall()
        for item in items:
            result.append({
                'id': item[0],
                'video_id': item[1],
                'start_time': item[2],
                'stop_time': item[3],
                'first_leng': item[4],
                'sec_leng': item[5]
            })

        return result

    def del_null_row(self, lesson_id):
        self.cursor.execute('''
                       DELETE FROM video_study
                       WHERE lesson_id=? AND (first_leng IS NULL OR sec_leng IS NULL OR first_leng='music')
                   ''', (lesson_id,))
        self.conn.commit()

    def get_video_file_name(self, id_file):
        self.cursor.execute('''
            SELECT file_name
            FROM video_file
            WHERE id=?
        ''', (id_file,))
        items = self.cursor.fetchall()
        return items[0][0]

    def get_studied_sent_word(self, lessons: [], mode):
        all_studied_word = set()
        all_studied_sent = set()
        for lesson in lessons:
            self.cursor.execute('''
                                    SELECT sentance_id 
                                    FROM lesson_progress
                                    WHERE lesson_id=? AND mode_id=? 
                                ''', (lesson, mode))
            items = self.cursor.fetchall()
            all_studied_sent_id = [item[0] for item in items]
            for each in self.get_sent_data(all_studied_sent_id):
                all_studied_sent.add(each['study_phrase'])
                for word in re.findall('(\\w+)', each['study_phrase']):
                    all_studied_word.add(word)
        return all_studied_sent, all_studied_word

    def set_video_studied(self, study_data):
        pass
