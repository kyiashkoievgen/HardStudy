import datetime
import json
import os
import sqlite3
import hashlib
from pathlib import Path

import requests
# import codecs
from gtts import gTTS
import string
# import spacy
import ru_core_news_lg
# from nltk import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
# from nltk.stem import PorterStemmer
# from flask import render_template
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Text, select, \
    not_, except_, update
from sqlalchemy.dialects.mysql import insert
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv

load_dotenv()

from sqlalchemy import func, and_, except_all


def gpt_db_connect():
    engine = create_engine("mysql+pymysql://ewgen:Zaqplm!234@localhost/chatgpt")
    metadata = MetaData()
    chat = Table('chat', metadata, autoload_with=engine)
    messages = Table('messages', metadata, autoload_with=engine)
    model = Table('model', metadata, autoload_with=engine)
    return {
        'chat': chat,
        'messages': messages,
        'model': model,
        'connect': engine.connect()
    }


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


def words_create_request(lang_id):
    mysql = mysql_connect()
    gpt_db = gpt_db_connect()

    s = select(mysql['reg_sent_word'])
    result = mysql['connect'].execute(s).fetchall()
    sent_id = [el[0] for el in result]

    s = select(mysql['sentences']).where(mysql['sentences'].c.language_id == lang_id).filter(
        mysql['sentences'].c.id.not_in(sent_id)
    )

    result = mysql['connect'].execute(s).fetchall()
    messages = []
    i = 0
    text = ''
    for j, row in enumerate(result):
        row = row[3]
        if i < 30 and j != len(result) - 1:
            text += f'{row}.\n'
            i += 1
        else:
            if text == '':
                text += f'{row}.\n'
            message = {
                "type_data": "chat",
                "temperature": 0,
                "max_tokens": 4096,
                "model": "gpt-4-1106-preview",
                "messages": [
                    {
                        "role": "system",
                        "content": "You doing very important job. You are very attentive. You exactly following next "
                                   "instructions:"
                                   "1. Use all sentences from request.\n2. Pick out only: numeral, substantive, "
                                   "adjective, verb and adverb.\n3. Words convert to its base form.\n4. Provide "
                                   "response to the JSON following format where applicable: ['sent':'sentence from "
                                   "user request', 'words': ['words from sentence']]"
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ]
            }
            new_item = insert(gpt_db['messages']).values(chat_id=26, date=datetime.datetime.now(),
                                                         message=json.dumps(message, ensure_ascii=False), in_out=-1)
            gpt_db['connect'].execute(new_item)
            gpt_db['connect'].commit()
            messages.append(json.dumps(message))
            i = 0
            text = ''

    print(messages)


def put_words_to_bd(language_id=4):
    # nlp = ru_core_news_lg.load()
    # doc = nlp("No text available yet")
    # print([(w.text, w.pos_) for w in doc])
    import en_core_web_trf
    nlp = en_core_web_trf.load()
    # nlp = spacy.load("pt_core_news_lg")
    # import pt_core_news_lg
    # import es_dep_news_trf
    # nlp = es_dep_news_trf.load()
    mysql = mysql_connect()
    s = select(mysql['sentences']).where(mysql['sentences'].c.language_id == language_id)
    sentences = mysql['connect'].execute(s).fetchall()
    words_set = set()
    for sentence in sentences:
        text = sentence[3].lower()
        text = ' '.join(text.split())
        translator = str.maketrans('', '', string.punctuation)
        text = text.translate(translator)
        stop_words = set(stopwords.words('english'))
        words = word_tokenize(text)
        filtered_text = ' '.join([word for word in words if word.lower() not in stop_words])
        words = nlp(filtered_text)

        [words_set.add(w.lemma_) for w in words]
    with open("words.txt", "w") as file:
        # Преобразуем set в список и записываем его в файл
        file.write("\n".join(words_set))
    print(len(words_set))


put_words_to_bd()


def put_word_from_gpt(chat_id=26):
    try:
        mysql = mysql_connect()
        gpt_db = gpt_db_connect()
        s = select(gpt_db['messages']).where(gpt_db['messages'].c.chat_id == chat_id, gpt_db['messages'].c.in_out == 1)
        mess_result = gpt_db['connect'].execute(s).fetchall()
        for message in mess_result:
            mess = json.loads(message[3].replace('```json', '').replace('```', ''))
            for sent in mess:
                # normal_string = codecs.decode(sent['sent'].replace('.', ''), 'unicode_escape')
                normal_string = sent['sent'].replace('.', '')
                s = select(mysql['sentences']).where(mysql['sentences'].c.text == normal_string)
                sent_id = mysql['connect'].execute(s).fetchone()
                if sent_id:
                    sent_id = sent_id[0]
                    for word in sent['words']:
                        # word = codecs.decode(word.lower(), 'unicode_escape')
                        word = word.lower()
                        s = select(mysql['words']).where(mysql['words'].c.word == word)
                        result = mysql['connect'].execute(s).fetchone()
                        if not result:
                            new_word = insert(mysql['words']).values(word=word)
                            result = mysql['connect'].execute(new_word)
                            word_id = result.inserted_primary_key[0]
                        else:
                            word_id = result[0]
                        new_item = insert(mysql['reg_sent_word']).values(sentences_id=sent_id, word_id=word_id)
                        do_nothing_stmt = new_item.on_duplicate_key_update(sentences_id=new_item.inserted.sentences_id,
                                                                           word_id=new_item.inserted.word_id)
                        mysql['connect'].execute(do_nothing_stmt)
                        print("ok:", sent_id)
                else:
                    print('not ok:')
    except:
        pass
    mysql['connect'].commit()
    mysql['connect'].close()
    gpt_db['connect'].close()


def copy_data_from_sqlite(lesson_from_id, lang1, lang2, user_id=1, lesson_to_id=1):
    mysql = mysql_connect()
    conn, cursor = sqlite_connect()
    cursor.execute(f'SELECT * FROM lesson_sentence WHERE lession_id={lesson_from_id}')
    rows = cursor.fetchall()
    for row in rows:
        sent_id = row[0]
        sent_lang1 = row[2].strip()
        sent_hash1 = hashlib.sha1(sent_lang1.lower().encode()).hexdigest()
        audio1 = row[4]
        sent_lang2 = row[3].strip()
        sent_hash2 = hashlib.sha1(sent_lang2.lower().encode()).hexdigest()
        audio2 = row[5]

        s = select(mysql['sentences']).where(mysql['sentences'].c.text_hash == sent_hash1)
        result1 = mysql['connect'].execute(s).fetchone()
        s = select(mysql['sentences']).where(mysql['sentences'].c.text_hash == sent_hash2)
        result2 = mysql['connect'].execute(s).fetchone()
        meaning_id = -1
        if not (result1 and result2):
            if (not result1) and (not result2):
                new_item = insert(mysql['meanings']).values()
                result = mysql['connect'].execute(new_item)
                meaning_id = result.inserted_primary_key[0]
            if result1:
                meaning_id = result1[2]
            if result2:
                meaning_id = result2[2]
            if not result1:
                new_item = insert(mysql['sentences']).values(language_id=lang1, meaning_id=meaning_id,
                                                             text=sent_lang1, text_hash=sent_hash1, audio=audio1)
                result = mysql['connect'].execute(new_item)
                sent_lang1_id = result.inserted_primary_key[0]
                new_item = insert(mysql['reg_sent_les_name']).values(sentences_id=sent_lang1_id,
                                                                     lessons_names_id=lesson_to_id)
                mysql['connect'].execute(new_item)
            if not result2:
                new_item = insert(mysql['sentences']).values(language_id=lang2, meaning_id=meaning_id,
                                                             text=sent_lang2, text_hash=sent_hash2, audio=audio2)
                result = mysql['connect'].execute(new_item)
                sent_lang2_id = result.inserted_primary_key[0]
                new_item = insert(mysql['reg_sent_les_name']).values(sentences_id=sent_lang2_id,
                                                                     lessons_names_id=lesson_to_id)
                mysql['connect'].execute(new_item)

            cursor.execute(f'SELECT * FROM lesson_progress WHERE sentance_id={sent_id} AND lesson_id={lesson_from_id}')
            progress_row = cursor.fetchone()
            if progress_row:
                show_count = progress_row[2]
                right_count = progress_row[3]
                last_show_time = progress_row[4]
                remember = progress_row[6]
                new_item = insert(mysql['study_progress']).values(user_id=user_id, lesson_name_id=lesson_to_id,
                                                                  sentence_id=sent_lang1_id,
                                                                  show_count=show_count, right_count=right_count,
                                                                  remember=remember,
                                                                  last_show_time=last_show_time)
                mysql['connect'].execute(new_item)
                print(show_count, right_count, last_show_time, remember)
            print(sent_id, sent_lang1, audio1, sent_lang2, audio2)
    mysql['connect'].commit()
    mysql['connect'].close()


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


def create_audio(creating_type='img', speed='slow', voice="nova"):
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

create_audio()
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

# translate_sent(4, 3, 1)
# copy_data_from_sqlite(29, 3, 1)
# init_db()
# words_create_request(3)
# put_word_from_gpt()
