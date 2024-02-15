import json
import os
import sqlite3
import hashlib
from pathlib import Path

import requests
from gtts import gTTS
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Text, select, \
    not_, except_, update
from sqlalchemy.dialects.mysql import insert
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv

load_dotenv()


def mysql_connect():
    engine = create_engine("mysql+pymysql://ewgen:Zaqplm!234@localhost/hard_study")
    metadata = MetaData()
    meanings = Table('meanings', metadata, autoload_with=engine)
    sentences = Table('sentences', metadata, autoload_with=engine)
    statistics = Table('statistics', metadata, autoload_with=engine)
    roles = Table('roles', metadata, autoload_with=engine)
    users = Table('users', metadata, autoload_with=engine)
    lessons_names = Table('lessons_names', metadata, autoload_with=engine)
    languages = Table('languages', metadata, autoload_with=engine)
    study_progress = Table('study_progress', metadata, autoload_with=engine)
    words = Table('words', metadata, autoload_with=engine)
    word__progress = Table('word__progress', metadata, autoload_with=engine)
    reg_sent_word = Table('reg_sent_word', metadata, autoload_with=engine)
    reg_sent_les_name = Table('reg_sent_les_name', metadata, autoload_with=engine)
    return {
        'lessons_names': lessons_names,
        'languages': languages,
        'roles': roles,
        'users': users,
        'meanings': meanings,
        'sentences': sentences,
        'statistics': statistics,
        'study_progress': study_progress,
        'words': words,
        'word__progress': word__progress,
        'reg_sent_word': reg_sent_word,
        'reg_sent_les_name': reg_sent_les_name,
        'metadata': metadata,
        'connect': engine.connect()
    }


def sqlite_connect():
    db_name = 'hard_study_span.db'
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATABASE = os.path.join(BASE_DIR, db_name)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    return conn, cursor


def init_db():
    mysql = mysql_connect()
    new_item = insert(mysql['roles']).values(id=1, name='admin')
    mysql['connect'].execute(new_item)
    mysql['connect'].commit()
    new_item = insert(mysql['users']).values(id=1, username='jey', role_id=1)
    mysql['connect'].execute(new_item)
    new_item = insert(mysql['lessons_names']).values(id=1, name='Базовый', description='Базовые слова и выражения',
                                                     owner_id=1)
    mysql['connect'].execute(new_item)
    new_item = insert(mysql['languages']).values({'id': 1, 'name': 'Русский', 'code': 'ru'})
    mysql['connect'].execute(new_item)
    new_item = insert(mysql['languages']).values({'id': 2, 'name': 'Portugues', 'code': 'pt'})
    mysql['connect'].execute(new_item)
    new_item = insert(mysql['languages']).values({'id': 3, 'name': 'Spanish', 'code': 'es'})
    mysql['connect'].execute(new_item)
    mysql['connect'].commit()


def put_words_to_bd(language_id):
    mysql = mysql_connect()
    s = select(mysql['languages']).where(mysql['languages'].c.id == language_id)
    language = mysql['connect'].execute(s).fetchone()
    nlp = None
    if language[2] == 'ru':
        import ru_core_news_lg
        nlp = ru_core_news_lg.load()
    elif language[2] == 'pt':
        import pt_core_news_lg
        nlp = pt_core_news_lg.load()
    elif language[2] == 'es':
        import es_dep_news_trf
        nlp = es_dep_news_trf.load()
    elif language[2] == 'en':
        import en_core_web_trf
        nlp = en_core_web_trf.load()
    # doc = nlp("No text available yet")
    # print([(w.text, w.pos_) for w in doc])
    s = select(mysql['sentences']).where(mysql['sentences'].c.language_id == language_id)
    sentences = mysql['connect'].execute(s).fetchall()
    words_set = set()
    for sentence in sentences:
        text = sentence[3].lower()
        text = ' '.join(text.split())
        translator = str.maketrans('', '', string.punctuation)
        text = text.translate(translator)
        stop_words = set(stopwords.words(language[1]))
        words = word_tokenize(text)
        filtered_text = ' '.join([word for word in words if word.lower() not in stop_words])
        words = nlp(filtered_text)
        [words_set.add(w.lemma_) for w in words]

        for word in words_set:
            s = select(mysql['words']).where(mysql['words'].c.word == word)
            result = mysql['connect'].execute(s).fetchone()
            if not result:
                new_word = insert(mysql['words']).values(word=word)
                result = mysql['connect'].execute(new_word)
                word_id = result.inserted_primary_key[0]
            else:
                word_id = result[0]
            new_item = insert(mysql['reg_sent_word']).values(sentences_id=sentence[0], word_id=word_id)
            do_nothing_stmt = new_item.on_duplicate_key_update(sentences_id=new_item.inserted.sentences_id,
                                                               word_id=new_item.inserted.word_id)
            mysql['connect'].execute(do_nothing_stmt)
            print("ok:", sentence[0])
        print(len(words_set), '\n', words_set)
        words_set = set()
    mysql['connect'].commit()
    mysql['connect'].close()


# put_words_to_bd(4)


def translate_sent(from_len_id, to_len_id, lessons_names_id):
    try:
        client = OpenAI()
        mysql = mysql_connect()
        # gpt_db = gpt_db_connect()
        s = select(mysql['languages']).where(mysql['languages'].c.id == from_len_id)
        len_code1 = mysql['connect'].execute(s).fetchone()[2]
        s = select(mysql['languages']).where(mysql['languages'].c.id == to_len_id)
        len_code2 = mysql['connect'].execute(s).fetchone()[2]

        s = select(mysql['sentences']).where(mysql['sentences'].c.language_id == from_len_id)
        from_sent_list = mysql['connect'].execute(s).fetchall()
        meaning_values = set([row[2] for row in from_sent_list])
        # Извлечь строки из таблицы mysql['sentences'] с заданными условиями
        has_meaning = select(mysql['sentences']).where(
            (mysql['sentences'].c.meaning_id.in_(meaning_values))
        ).filter((mysql['sentences'].c.language_id == to_len_id))
        has_meaning_val = mysql['connect'].execute(has_meaning).fetchall()
        meaning_values = set([row[2] for row in has_meaning_val])
        no_meaning = select(mysql['sentences']).where(
            ~(mysql['sentences'].c.meaning_id.in_(meaning_values))
        ).filter((mysql['sentences'].c.language_id == from_len_id))
        from_sent_list = mysql['connect'].execute(no_meaning).fetchall()
        i = 0
        text = ''
        for j, from_sent in enumerate(from_sent_list):
            meaning_id = from_sent[2]
            from_sent_txt = from_sent[3]
            if i < 10 and j != len(from_sent_list) - 1:
                text += f'id={meaning_id}, {from_sent_txt}.\n'
                i += 1
            else:
                if text == '':
                    text += f'id={meaning_id}, {from_sent_txt}.\n'
                try:
                    response = client.chat.completions.create(
                        temperature=0,
                        max_tokens=4096,
                        model="gpt-3.5-turbo-1106",
                        response_format={"type": "json_object"},
                        messages=[
                            {
                                "role": "system",
                                "content": f"Translate from '{len_code1}' to '{len_code2}' "
                                           "all sentences from request. Response privilege JSON following format:"
                                           "{'id':'translation'} For example {'523':'O fogo ardente consome'}"
                            },
                            {
                                "role": "user",
                                "content": text
                            }
                        ]
                    )
                    content = json.loads(response.choices[0].message.content)
                    for key, text in content.items():
                        text = ' '.join(text.split())
                        translator = str.maketrans('', '', string.punctuation)
                        text = text.translate(translator)
                        sent_hash = hashlib.sha256((str(to_len_id) + text).lower().encode()).hexdigest()
                        new_item = insert(mysql['sentences']).values(language_id=to_len_id, meaning_id=key,
                                                                     text=text, text_hash=sent_hash)
                        result = mysql['connect'].execute(new_item)
                        sent_lang_id = result.inserted_primary_key[0]
                        new_item = insert(mysql['reg_sent_les_name']).values(sentences_id=sent_lang_id,
                                                                             lessons_names_id=lessons_names_id)
                        mysql['connect'].execute(new_item)
                        print(key, text)

                    mysql['connect'].commit()
                except OpenAIError as e:
                    print(str(e))
                # new_item = insert(gpt_db['messages']).values(chat_id=26, date=datetime.datetime.now(),
                #                                          message=json.dumps(message, ensure_ascii=False), in_out=-1)
                # gpt_db['connect'].execute(new_item)
                i = 0
                text = ''

    except Exception as e:
        print('error', e)
    # gpt_db['connect'].commit()


def create_audio_img(creating_type='img', speed='slow', voice="nova"):
    mysql = mysql_connect()
    client = OpenAI()
    s = select(mysql['sentences']).where(mysql['sentences'].c.img == 0, mysql['sentences'].c.language_id == 4)
    from_sent_list = mysql['connect'].execute(s).fetchall()
    for row in from_sent_list:
        try:
            text = row[3]
            file_name = row[4]
            s = select(mysql['languages']).where(mysql['languages'].c.id == row[1])
            len_code = mysql['connect'].execute(s).fetchone()[2]
            if creating_type == 'voice_google':
                tts1 = gTTS(text, lang=len_code, slow=(speed == 'slow'))

                speech_file_path = Path(__file__).parent / \
                                   f"web/static/audio/hs/google_{speed}/{file_name}.mp3"
                tts1.save(speech_file_path)
            elif creating_type == 'voice_openai':
                response = client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=text
                )
                speech_file_path = Path(__file__).parent / \
                                   f"web/static/audio/hs/{voice}/{file_name}.mp3"
                response.stream_to_file(speech_file_path)
            elif creating_type == 'img':
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=f"create image in surrealism style. Img topic is: {text}",
                    n=1,
                    quality="standard",
                    size="1024x1024"
                )

                # Получаем байты изображения
                image_url = response.data[0].url
                response = requests.get(image_url)
                if response.status_code == 200:
                    # Сохраняем изображение на диск
                    speech_file_path = Path(__file__).parent / \
                                       f"web/static/img/hs/back_ground/{file_name}.png"
                    with open(speech_file_path, "wb") as f:
                        f.write(response.content)

            s = update(mysql['sentences']).where(mysql['sentences'].c.id == row[0]).values(audio=1)
            mysql['connect'].execute(s)
            mysql['connect'].commit()
        except OpenAIError as e:
            print(str(e))
        except Exception as e:
            print('error', e)

# mysql = mysql_connect()
# s = select(mysql['sentences']).where(mysql['sentences'].c.language_id == 4)
# from_sent_list = mysql['connect'].execute(s).fetchall()
# for row in from_sent_list:
#     try:
#         sent_hash = hashlib.sha256((str(row[1]) + row[3]).lower().encode()).hexdigest()
#         s = update(mysql['sentences']).where(mysql['sentences'].c.id==row[0]).values(text_hash=sent_hash)
#         mysql['connect'].execute(s)
#         print(row[3])
#     except Exception as e:
#         print('error', e)
# mysql['connect'].commit()
