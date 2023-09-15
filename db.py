import sqlite3
import tkinter as tk
from gtts import gTTS
from langdetect import detect


class DB:
    def __init__(self):
        self.conn = sqlite3.connect('hard_study.db')
        self.cursor = self.conn.cursor()
        self.dropdown_lesson_name = tk.StringVar()

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
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                while True:
                    # Читаем две строки
                    what_to_learn = file.readline()
                    value_in_another_language = file.readline()
                    # detected_language1 = detect(what_to_learn)
                    # detected_language2 = detect(value_in_another_language)
                    # Создайте объект gTTS с автоматически определенным языком
                    tts1 = gTTS(what_to_learn, lang='pt')
                    tts2 = gTTS(value_in_another_language, lang='ru')
                    tts1.save("output.mp3")
                    tts2.save("output2.mp3")
                    # Проверяем, что строки не пустые (конец файла)
                    if not what_to_learn or not value_in_another_language:
                        break

                    # Обрабатываем две прочитанные строки
                    print(what_to_learn.strip())  # .strip() удаляет символы новой строки и пробелы
                    print(value_in_another_language.strip())
        except FileNotFoundError:
            print("Файл не найден.")
        except IOError:
            print("Ошибка ввода/вывода при чтении файла.")
