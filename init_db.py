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
            mode_id INTEGER,
            FOREIGN KEY (mode_id) REFERENCES mode_study(id)
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
        ('Учить язык произношение', 'Обучение языка с произношением')
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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lession_body_id INTEGER,            
            show_count integer,
            right_count integer,
            last_show_time DATETIME,
            FOREIGN KEY (lession_body_id) REFERENCES lesson_body(id)
        )
    ''')

    # Таблица с настройками приложения
    cursor.execute('''
           CREATE TABLE IF NOT EXISTS app_settings (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               mode TEXT,
               mode_description TEXT,
               comport INTEGER
           )
       ''')

    # Вставьте начальные данные
    initial_data = [
        ('Audio', 'Режим обучения восприятия на слух', 1)
        # Добавьте больше данных, если необходимо
    ]

    for item in initial_data:
        cursor.execute('INSERT INTO app_settings (mode, mode_description, comport) VALUES (?, ?, ?)', item)

    # Сохраните изменения и закройте соединение с базой данных
    conn.commit()
    conn.close()


if __name__ == '__main__':
    database_name = 'hard_study.db'  # Укажите имя вашей базы данных
    initialize_database(database_name)
    print(f'База данных {database_name} инициализирована успешно.')
