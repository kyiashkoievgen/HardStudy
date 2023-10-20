from db import DB
from gtts import gTTS
import hashlib
from voice_unit import mp4_to_wav, audio_file_recognizer
from voice_frame_generator import chunk_wav
from googletrans import Translator


def create_new_lesson_from_txt(file_path, first_lang,  second_lang, name_lesson, description_lesson):
    db = DB()
    db.cursor.execute('''INSERT INTO lesson_name
                        (name, description, mode, first_lang, second_lang) 
                        VALUES (?, ?, ?, ?, ?)''',
                      (name_lesson, description_lesson, 2, first_lang,  second_lang))
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
                tts1 = gTTS(what_to_learn, lang=first_lang)
                tts2 = gTTS(value_in_another_language, lang=second_lang)
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


def create_new_lesson_from_mp4(video_file_path, first_lang,  second_lang, name_lesson, description_lesson):
    file_path = 'audio\\tmp_file'
    db = DB()
    db.cursor.execute('INSERT INTO lesson_name (name, description, mode, first_lang, second_lang) VALUES (?, ?, ?, ?)',
                      (name_lesson, description_lesson, 1, first_lang,  second_lang))
    db.conn.commit()
    lesson_id = db.cursor.lastrowid
    db.cursor.execute('INSERT INTO video_file (file_name, language) VALUES (?, ?)',
                      (video_file_path, first_lang))
    db.conn.commit()
    video_file_id = db.cursor.lastrowid

    mp4_to_wav(video_file_path, f'{file_path}\\tmp_wav_file.wav')

    chunk_wav(file_path, db, video_file_id, lesson_id)

    db.cursor.execute('''SELECT audio_file
                         FROM video_study
                         WHERE lesson_id=? AND video_id=? ''', (lesson_id, video_file_id))
    rows = db.cursor.fetchall()
    translator = Translator()
    for row in rows:
        file_name = row[0]
        text_orig = audio_file_recognizer(file_name, first_lang)
        print(f'файл {file_name} --- {text_orig}\n')
        if not text_orig == '':
            translated_text = translator.translate(text_orig, src=first_lang, dest=second_lang)
            print(f'перевод {translated_text.text}\n')
            db.cursor.execute('''
                            UPDATE video_study
                            SET first_leng=?, sec_leng=?
                            WHERE audio_file=? AND lesson_id=? AND video_id=?
                        ''', (text_orig, translated_text.text, file_name, lesson_id, video_file_id))
            db.conn.commit()

    db.conn.close()


def recognize_file(lesson_id, video_file_id, first_lang,  second_lang):
    db = DB()
    db.cursor.execute('''SELECT audio_file
                         FROM video_study
                         WHERE lesson_id=? AND video_id=? AND first_leng IS NULL''', (lesson_id, video_file_id))
    rows = db.cursor.fetchall()
    translator = Translator()
    for row in rows:
        file_name = row[0]
        text_orig = audio_file_recognizer(file_name, first_lang)
        print(f'файл {file_name} --- {text_orig}\n')
        if not text_orig == '':
            translated_text = translator.translate(text_orig, src=first_lang, dest=second_lang)
            print(f'перевод {translated_text.text}\n')
            db.cursor.execute('''
                            UPDATE video_study
                            SET first_leng=?, sec_leng=?
                            WHERE audio_file=? AND lesson_id=? AND video_id=?
                        ''', (text_orig, translated_text.text, file_name, lesson_id, video_file_id))
            db.conn.commit()

    db.conn.close()



#recognize_file(20, 17, 'en-US', 'ru')