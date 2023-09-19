import hashlib
import sqlite3
import tkinter as tk
from gtts import gTTS
from langdetect import detect


class DB:
    def __init__(self):
        self.conn = sqlite3.connect('hard_study.db')
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.conn.close()

    def fetch_lesson_name(self):
        self.cursor.execute("SELECT name FROM lesson_name")
        items = self.cursor.fetchall()
        return [item[0] for item in items]

    def update_dropdown(self):
        items = self.fetch_lesson_name()
        self.dropdown_lesson_name['values'] = items

    def create_new_lesson(self, file_path, name_lesson, description_lesson, mode_id):
        self.cursor.execute('INSERT INTO lesson_name (name, description, mode_id) VALUES (?, ?, ?)', (name_lesson, description_lesson, mode_id))
        self.conn.commit()
        lesson_name_id = self.cursor.lastrowid
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                while True:
                    # Читаем две строки
                    what_to_learn = file.readline()
                    value_in_another_language = file.readline()
                    # Проверяем, что строки не пустые (конец файла)
                    if not what_to_learn or not value_in_another_language:
                        break
                    # detected_language1 = detect(what_to_learn)
                    # detected_language2 = detect(value_in_another_language)
                    # Создайте объект gTTS с автоматически определенным языком
                    tts1 = gTTS(what_to_learn, lang='pt')
                    tts2 = gTTS(value_in_another_language, lang='ru')
                    hash_object = hashlib.md5()
                    hash_object.update(what_to_learn.encode())
                    what_to_learn_mp3_name = hash_object.hexdigest()
                    hash_object.update(value_in_another_language.encode())
                    value_in_another_language_mp3_name = hash_object.hexdigest()
                    try:
                        # Выполняем изменения в базе данных
                        self.cursor.execute('''INSERT INTO lesson_body (lession_id, what_to_learn, 
                        value_in_another_language, what_to_learn_audio, value_in_another_language_audio
                         ) VALUES (?, ?, ?, ?, ?)''', (lesson_name_id, what_to_learn, value_in_another_language,
                                                       what_to_learn_mp3_name, value_in_another_language_mp3_name))

                        tts1.save(f"audio\\{what_to_learn_mp3_name}.mp3")
                        tts2.save(f"audio\\{value_in_another_language_mp3_name}.mp3")
                        self.conn.commit()
                    except Exception as e:
                        print(f"Ошибка: {e}")
                        self.conn.rollback()

                    # Обрабатываем две прочитанные строки
                    print(what_to_learn.strip())  # .strip() удаляет символы новой строки и пробелы
                    print(value_in_another_language.strip())
        except FileNotFoundError:
            print("Файл не найден.")
        except IOError:
            print("Ошибка ввода/вывода при чтении файла.")

    def get_current_lesson(self):
        self.cursor.execute("SELECT id, name FROM lesson_name WHERE default_lesson=1")
        items = self.cursor.fetchall()
        result = ('', 'Не выбрано')
        if len(items) != 0:
            result = (items[0][0], items[0][1])
        return result

    def set_default_lesson(self, name):
        self.cursor.execute("UPDATE lesson_name SET default_lesson=0 WHERE default_lesson=1")
        self.conn.commit()
        self.cursor.execute(f"UPDATE lesson_name SET default_lesson=1 WHERE name='{name}'")
        self.conn.commit()

    def app_setting_init(self, mode, comport, profile_name, lesson_per_day, time_between_study_1, time_beetween_study_2,
                         time_beetween_study_3, time_beetween_study_4, time_beetween_study_5, time_beetween_study_6,
                         sent_in_less, show_time_sent, punish_time_1, punish_time_2, punish_time_3):
        pass


