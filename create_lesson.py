from db import DB
from gtts import gTTS
import hashlib


def create_new_lesson_from_txt(file_path, name_lesson, description_lesson, file_type):
    db = DB()
    db.cursor.execute('INSERT INTO lesson_name (name, description, type_lesson) VALUES (?, ?, ?)',
                      (name_lesson, description_lesson, file_type))
    db.conn.commit()
    lesson_name_id = db.cursor.lastrowid
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
                    db.cursor.execute('''INSERT INTO lesson_body (lession_id, what_to_learn, 
                       value_in_another_language, what_to_learn_audio, value_in_another_language_audio
                        ) VALUES (?, ?, ?, ?, ?)''', (lesson_name_id, what_to_learn, value_in_another_language,
                                                      what_to_learn_mp3_name, value_in_another_language_mp3_name))

                    tts1.save(f"audio\\{what_to_learn_mp3_name}.mp3")
                    tts2.save(f"audio\\{value_in_another_language_mp3_name}.mp3")
                    db.conn.commit()
                except Exception as e:
                    print(f"Ошибка: {e}")
                    db.conn.rollback()

                # Обрабатываем две прочитанные строки
                print(what_to_learn.strip())  # .strip() удаляет символы новой строки и пробелы
                print(value_in_another_language.strip())
    except FileNotFoundError:
        print("Файл не найден.")
    except IOError:
        print("Ошибка ввода/вывода при чтении файла.")


def create_new_lesson_from_mp4(file_path, name_lesson, description_lesson, file_type):
    db = DB()
    db.cursor.execute('INSERT INTO lesson_name (name, description, type_lesson) VALUES (?, ?, ?)',
                      (name_lesson, description_lesson, file_type))
    db.conn.commit()
    lesson_name_id = db.cursor.lastrowid
