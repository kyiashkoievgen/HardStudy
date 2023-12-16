import re
import sqlite3
from datetime import datetime, timedelta
from random import shuffle
import os


def array_to_str(cur_les_list):
    cur_les = '('
    for les in cur_les_list:
        cur_les += f'{int(les)}, '
    cur_les = cur_les[:-2]
    return cur_les + ')'


class DB:
    def __init__(self, db_name='hard_study.db'):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        DATABASE = os.path.join(BASE_DIR, db_name)
        self.conn = sqlite3.connect(DATABASE)
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

    def set_default_lesson(self, id_lessons):
        self.cursor.execute("UPDATE lesson_name SET default_lesson=0 WHERE default_lesson=1")
        self.conn.commit()
        for id_lesson in id_lessons:
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
        SELECT id, comport, profile_name, lesson_per_day, time_beetween_study_1, time_beetween_study_2,
        time_beetween_study_3, time_beetween_study_4, time_beetween_study_5, time_beetween_study_6, sent_in_less,
        show_time_sent, punish_time_1, right_answer_1, right_answer_2, apostrophe         
        FROM app_settings 
        WHERE {where_par}
          ''')
        return dict(cursor.fetchall()[0])

    def set_setting_def(self, id_prof):
        update_query = f'''
            UPDATE app_settings
            SET default_setting="0"
            WHERE default_setting="1"
        '''
        self.cursor.execute(update_query)
        self.conn.commit()

        update_query = f'''
                    UPDATE app_settings
                    SET default_setting="1"
                    WHERE id=?
                '''
        self.cursor.execute(update_query, (id_prof,))
        self.conn.commit()

    def get_mode_id(self, name):
        self.cursor.execute(f"SELECT id FROM mode_study WHERE name='{name}'")
        return self.cursor.fetchall()[0][0]

    def save_settings(self, settings):
        col_name = ''
        for key, var in settings.items():
            if key == 'comport':
                col_name += f'comport="{var}"'
            else:
                col_name += f', {key}="{var}"'

        update_query = f'''
            UPDATE app_settings
            SET {col_name}
            WHERE default_setting="1"
        '''

        self.cursor.execute(update_query)
        self.conn.commit()

    def insert_settings(self, settings):
        col_name = ''
        val = ()
        val_q = ''
        for key, var in settings.items():
            if key == 'comport':
                col_name += f'comport'
                val += (f'{var}',)
                val_q += '?'
            else:
                col_name += f', {str(key)}'
                val += (str(var),)
                val_q += ', ?'
        # print(col_name, val)
        self.cursor.execute(f'INSERT INTO app_settings ({col_name}) VALUES ({val_q})', val)
        self.conn.commit()
        last_id = self.cursor.lastrowid
        self.cursor.execute('UPDATE app_settings SET default_setting="0" WHERE default_setting="1"')
        self.conn.commit()
        self.cursor.execute(f'UPDATE app_settings SET default_setting="1" WHERE id="{last_id}"')
        self.conn.commit()

    def get_settings_profile(self):
        self.cursor.execute("SELECT id, profile_name FROM app_settings")
        items = self.cursor.fetchall()
        return [{'id': item[0], 'name': item[1]} for item in items]

    def get_progress_sentance(self, cur_les_list, right_answer, limit, time_for_new_sent=None):
        cur_les = array_to_str(cur_les_list)
        if time_for_new_sent is None:
            self.cursor.execute(f'''
                SELECT sentance_id 
                FROM lesson_progress
                WHERE lesson_id in {cur_les} AND right_count=? 
                LIMIT ?
            ''', (right_answer, limit))
        else:
            current_date = datetime.now()
            time_ago = current_date - timedelta(minutes=int(time_for_new_sent))
            # print(time_ago)
            self.cursor.execute(f'''
                SELECT sentance_id 
                FROM lesson_progress
                WHERE lesson_id in {cur_les} AND right_count=? AND last_show_time<=?
                ORDER BY last_show_time
                LIMIT ?
            ''', (right_answer, time_ago, limit))

        items = self.cursor.fetchall()
        return [item[0] for item in items]

    def get_new_sentance(self, cur_les_list, add_sent_num):
        cur_les = array_to_str(cur_les_list)
        self.cursor.execute(f'''
                        SELECT id 
                        FROM lesson_sentence
                        WHERE (lession_id in {cur_les}) AND (id NOT IN 
                            (SELECT sentance_id FROM lesson_progress WHERE lesson_id in {cur_les}))
                        LIMIT ?
                    ''', (add_sent_num, ))
        # print(cur_les, mode_id, add_sent_num)
        items = self.cursor.fetchall()
        return [item[0] for item in items]

    def get_sent_data(self, study_id_sent_list):
        result = []
        for id_el in study_id_sent_list:
            if type(id_el) == tuple:
                id_el = id_el[0]
            self.cursor.execute('''
                SELECT what_to_learn, value_in_another_language, what_to_learn_audio, value_in_another_language_audio
                FROM lesson_sentence
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

    def is_show_first_time(self, id_phrase, lesson_id):
        self.cursor.execute('''
                        SELECT right_count
                        FROM lesson_progress
                        WHERE sentance_id=? AND lesson_id=? AND right_count>0
                    ''', (id_phrase, lesson_id))
        item = self.cursor.fetchall()
        if len(item) > 0:
            return False
        else:
            return True

    def inc_dec_right_count(self, id_phrase, cur_les_id, inc, remember=False):
        if remember:
            remember = 1
        else:
            remember = 0
        # проверяем есть ли это предложение в прогрессе обучения если нет то создаем запись
        self.cursor.execute('''
                               SELECT right_count
                               FROM lesson_progress
                               WHERE sentance_id=? AND lesson_id=?
                           ''', (id_phrase, cur_les_id))
        item = self.cursor.fetchall()
        current_date = datetime.now()
        if len(item) == 0:
            self.cursor.execute('''INSERT INTO lesson_progress (
                       lesson_id, show_count, right_count, last_show_time, sentance_id, remember
                   )
                   VALUES (
                       ?, 0, 0, ?, ?, ?
                   )''', (cur_les_id, current_date, id_phrase, remember))
            self.conn.commit()
        self.cursor.execute('''
                        SELECT right_count, show_count
                        FROM lesson_progress
                        WHERE sentance_id=? AND lesson_id=?
                    ''', (id_phrase, cur_les_id))
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
                WHERE sentance_id=? AND lesson_id=?
            ''', (show_count, right_count, current_date, remember, id_phrase, cur_les_id))
        self.conn.commit()

    def insert_new_statistic(self, cur_les_id):
        self.cursor.execute('''INSERT INTO statistic (
                   study_date, total_show, right_answer, shock, new_phrase, study_id
               )
               VALUES (
                   ?, 0, 0, 0, 0, ?
               )''', (datetime.now(), cur_les_id))
        self.conn.commit()
        return self.cursor.lastrowid

    def save_statistic(self, cur_les_list, total_shows_now, total_sent_now, total_word_now, right_answer,
                       new_sent_now, total_shock_now, total_time_now, total_sent, total_word, time_start, time_stop,
                       full_understand):
        cur_les = array_to_str(cur_les_list)[1:-1]
        self.cursor.execute('''INSERT INTO statistic (
                    study_date, total_show, right_answer, shock, new_phrase, study_id, total_sent, total_word,
                     total_time, total_word_now, total_sent_now, time_start, time_stop, full_understand  
                     )
                     VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                        )
                   ''', (datetime.now(), total_shows_now, right_answer, total_shock_now, new_sent_now, cur_les,
                         total_sent, total_word, total_time_now, total_word_now, total_sent_now, time_start, time_stop,
                         full_understand))
        self.conn.commit()

    def get_remember_sent(self, cur_les_list, n=5, trigger_know=4):
        cur_les = array_to_str(cur_les_list)
        self.cursor.execute(f'''
                SELECT sentance_id 
                FROM lesson_progress
                WHERE lesson_id in {cur_les} AND right_count>=? AND remember=0
            ''', (trigger_know, ))

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

    def get_studied_sent_word(self, lessons: []):
        all_studied_word = set()
        all_studied_sent = set()
        full_understand = 0
        result = []
        for lesson in lessons:
            self.cursor.execute('''
                                    SELECT sentance_id 
                                    FROM lesson_progress
                                    WHERE lesson_id=? 
                                ''', (lesson,))
            items = self.cursor.fetchall()
            all_studied_sent_id = [item[0] for item in items]
            for each in self.get_sent_data(all_studied_sent_id):
                all_studied_sent.add(each['study_phrase'])
                for word in re.findall('(\\w+)', each['study_phrase']):
                    all_studied_word.add(word)

            self.cursor.execute('''
                                    SELECT sentance_id 
                                    FROM lesson_progress
                                    WHERE lesson_id=? AND remember=1
                                ''', (lesson,))

            full_understand = len(self.cursor.fetchall())
            result.append({
                'studied_word': all_studied_word,
                'studied_sent': all_studied_sent,
                'full_understand': full_understand
            })
            all_studied_word = set()
            all_studied_sent = set()
        return result

    def set_video_studied(self, study_data):
        pass

    def get_all_lesson(self, lesson_filter, my_lesson=False):
        where = ''
        param = ()
        if (not lesson_filter['mode'] is None) and (not lesson_filter['mode'] == 'all'):
            where = f' AND lesson_name.mode=?'
            param += (lesson_filter["mode"],)
        if (not lesson_filter['lang1'] is None) and (not lesson_filter['lang1'] == 'all'):
            where += f' AND lesson_name.first_lang=?'
            param += (lesson_filter["lang1"],)
        if (not lesson_filter['lang2'] is None) and (not lesson_filter['lang2'] == 'all'):
            where += f' AND lesson_name.second_lang=?'
            param += (lesson_filter["lang2"],)
        if my_lesson:
            where += ' AND lesson_name.id IN (SELECT lesson_id FROM lesson_progress)'
        else:
            where += ' AND lesson_name.id NOT IN (SELECT lesson_id FROM lesson_progress)'
        query = f'''SELECT lesson_name.id, lesson_name.name, lesson_name.description, lesson_name.mode, 
                            mode_study.name AS mode_name, lesson_name.first_lang, lesson_name.second_lang, 
                            lesson_name.sentence_numer, lesson_name.word_numer, default_lesson
                         FROM lesson_name, mode_study
                         WHERE lesson_name.mode=mode_study.id{where}
                         '''
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        cursor.execute(query, param)
        items = cursor.fetchall()
        result = []
        for each in items:
            result.append(dict(each))
        return result

    def get_all_mode(self):
        self.cursor.execute('''
            SELECT id, name, description
            FROM mode_study            
        ''')
        return self.cursor.fetchall()

    def fill_lesson_sent_word(self):
        query = ''
        for mode in self.get_all_mode():
            self.cursor.execute('''
                SELECT id 
                FROM lesson_name
                WHERE mode=?
            ''', (mode[0],))
            all_lesson_id = self.cursor.fetchall()
            if mode[0] == 2:
                query = '''
                        SELECT what_to_learn
                        FROM lesson_sentence
                        WHERE lession_id=?
                    '''
            elif mode[0] == 1:
                query = '''
                        SELECT first_leng
                        FROM video_study
                        WHERE lesson_id=?
                    '''
            for lesson_id in all_lesson_id:
                self.cursor.execute(query, lesson_id)
                lesson_sent = self.cursor.fetchall()
                num_sent = len(lesson_sent)
                list_of_word = set()
                for sent in lesson_sent:
                    for word in re.findall('(\\w+)', sent[0]):
                        list_of_word.add(word)
                num_word = len(list_of_word)
                self.cursor.execute('''
                    UPDATE lesson_name
                    SET sentence_numer=?, word_numer=?
                    WHERE id=?
                ''', (num_sent, num_word, lesson_id[0]))
                print(lesson_id[0], num_sent, num_word)
        self.conn.commit()

    def get_all_mode_lang_name(self, mode=True):
        query = ''
        if mode:
            query = '''
                        SELECT id, name, description
                        FROM mode_study
                    '''
        else:
            query = '''
                        SELECT name, code
                        FROM languages
                    '''
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        cursor.execute(query)
        items = cursor.fetchall()
        result = []

        for each in items:
            new_dict = dict()
            old_dict = dict(each)
            for key in old_dict.keys():
                new_dict[key] = str(old_dict[key])
            result.append(new_dict)
        return result

    def get_statistic(self):
        pass

# db = DB()
# print(db.fill_lesson_sent_word())
