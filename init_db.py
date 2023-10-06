import sqlite3
import os


def initialize_database(database_name):
    # Удалите базу данных, если она существует
    if os.path.exists(database_name):
        os.remove(database_name)

    # Создайте подключение к базе данных
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    # Таблица с названиями и описаниями уроков
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lesson_name (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
	        default_lesson	INTEGER,
	        type_lesson	TEXT
        )
    ''')

    # Таблица с модами обучения
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mode_study (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT
        )
    ''')

    # Вставьте начальные данные
    initial_data = [
        ('Восприятие на слух', 'Обучение языка с восприятием только на слух')
        ('Чтение письмо ru>pt без \`', 'Обучение восприятия языка как текст португальского на русский без диалектических знаков')
        ('Чтение письмо ru>pt с \`', 'Обучение восприятия языка как текст португальского на русский с диалектическими знаками')
        # Добавьте больше данных, если необходимо
    ]

    for item in initial_data:
        cursor.execute('INSERT INTO mode_study (name, description) VALUES (?, ?)', item)

    # Таблица с содержанием уроков
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lesson_body (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lession_id INTEGER,
            what_to_learn TEXT,
            value_in_another_language TEXT,
            what_to_learn_audio TEXT UNIQUE,
            value_in_another_language_audio TEXT UNIQUE,
            FOREIGN KEY (lession_id) REFERENCES lesson_name(id)
        )
    ''')

    # Таблица с содержанием уроков
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lesson_progress (
            id	INTEGER,
            lesson_id	INTEGER,
            show_count	integer,
            right_count	integer,
            last_show_time	DATETIME,
            sentance_id	INTEGER,
            mode_id	INTEGER,
            FOREIGN KEY(lesson_id) REFERENCES lesson_body(id),
            FOREIGN KEY(sentance_id) REFERENCES lesson_body(id),
            FOREIGN KEY(mode_id) REFERENCES mode_study(id),
            PRIMARY KEY(id AUTOINCREMENT)
        )
    ''')

    # Таблица с настройками приложения
    cursor.execute('''
           CREATE TABLE IF NOT EXISTS app_settings (
            id	INTEGER,
            mode	TEXT,
            comport	TEXT,
            profile_name	TEXT,
            lesson_per_day	TEXT,
            time_beetween_study_1	TEXT,
            time_beetween_study_2	TEXT,
            time_beetween_study_3	TEXT,
            time_beetween_study_4	TEXT,
            time_beetween_study_5	TEXT,
            time_beetween_study_6	TEXT,
            sent_in_less	TEXT,
            show_time_sent	TEXT,
	        punish_time_1	TEXT,
	        punish_time_2	TEXT,
	        punish_time_3	TEXT,
	        default_setting	TEXT,
            FOREIGN KEY(mode) REFERENCES mode_study(id),
            PRIMARY KEY(id AUTOINCREMENT)
            );
           
       ''')

    # Вставьте начальные данные
    initial_data = [
        (2, '1', 5, 10, 20, 60, 480, 1440, 10080, 5, 10, 1, 2, 3, 1)
        # Добавьте больше данных, если необходимо
    ]
    for item in initial_data:
        cursor.execute('INSERT INTO app_settings (mode, profile_name, lesson_per_day, time_beetween_study_1, time_beetween_study_2, time_beetween_study_3, time_beetween_study_4, time_beetween_study_5, time_beetween_study_6, sent_in_less, show_time_sent, punish_time_1, punish_time_2, punish_time_3, default_setting) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', item)

    # Таблица со статистикой обучения
    cursor.execute('''
    CREATE TABLE "statistic"(
        "id"             INTEGER,
        "study_date"     DATETIME,
        "total_show"     INTEGER,
        "right_answer"   INTEGER,
        "shock"          INTEGER,
        "new_phrase"     INTEGER,
        "mode_id"        INTEGER,
        "study_id"       INTEGER,
        PRIMARY KEY("id" AUTOINCREMENT)
    );
    ''')

    # Сохраните изменения и закройте соединение с базой данных
    conn.commit()
    conn.close()


if __name__ == '__main__':
    database_name = 'hard_study.db'  # Укажите имя вашей базы данных
    initialize_database(database_name)
    print(f'База данных {database_name} инициализирована успешно.')
