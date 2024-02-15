import datetime
import json
from flask import render_template
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Text, select
from sqlalchemy.sql import insert


def db_connect():
    engine = create_engine("mysql+pymysql://ewgen:Zaqplm!234@localhost/chatgpt")
    metadata = MetaData()
    chat = Table('chat', metadata, autoload_with=engine)
    messages = Table('messages', metadata, autoload_with=engine)
    open_ai_model = Table('model', metadata, autoload_with=engine)
    return metadata, engine, chat, messages, open_ai_model


def result_to_dict(result):
    column_names = result.keys()
    rows = [dict(zip(column_names, row)) for row in result.fetchall()]
    dict_result = []
    for row in rows:
        message = ''
        if 'date' in row and row['date']:
            row['date'] = row['date'].strftime('%Y-%m-%d %H:%M:%S')
        if 'model_id' in row and row['model_id']:
            row['model'] = get_model(row['model_id'])[0]['name']
        if 'in_out' in row and row['in_out'] == 1:
            row.update(json.loads(row['usage']))
        elif 'in_out' in row and row['in_out'] == 2:
            message = row['message']
            message = json.loads(message)
            message[0]['date'] = row['date']
            message[0]['model'] = row['model']
            message[0]['model_id'] = row['model_id']
            message[0]['temperature'] = row['temperature']
            message[0]['max_tokens'] = row['max_tokens']
        dict_result.append(render_template('send_message.html', messages=message))
    return result


def get_chats():
    metadata, engine, chat, messages, open_ai_model = db_connect()
    with engine.connect() as connection:
        s = select(chat)
        result = connection.execute(s)
    column_names = result.keys()
    rows = [dict(zip(column_names, row)) for row in result.fetchall()]
    return rows


def get_model(id_model=None):
    metadata, engine, chat, messages, open_ai_model = db_connect()
    with engine.connect() as connection:
        s = ''
        if id_model:
            s = select(open_ai_model).where(open_ai_model.c.id == id_model)
        else:
            s = select(open_ai_model)
        result = connection.execute(s)
    column_names = result.keys()
    rows = [dict(zip(column_names, row)) for row in result.fetchall()]
    return rows


def get_chats_messages(chat_id):
    metadata, engine, chat, messages, open_ai_model = db_connect()
    with engine.connect() as connection:
        s = select(messages).order_by('date').where(messages.c.chat_id == chat_id)
        result = connection.execute(s)
    column_names = result.keys()
    rows = [dict(zip(column_names, row)) for row in result.fetchall()]
    dict_result = []
    for row in rows:
        message = []
        if 'in_out' in row and row['in_out'] == 1:
            message.append({
                "id": row['id'],
                "role": "assistant",
                "content": row['message'],
                "in": 1
            })
            message[0].update(json.loads(row['usage']))
        elif 'in_out' in row and row['in_out'] == 2:
            message = row['message']
            message = json.loads(message)
            for i in range(0, len(message)):
                message[i]['id'] = f"{row['id']}{row['chat_id']}{i}"
            message[0]['temperature'] = row['temperature']
            message[0]['max_tokens'] = row['max_tokens']
        elif 'in_out' in row and row['in_out'] == 0:
            message.append({
                "id": row['id'],
                "role": "raw",
                "content": row['message']
            })
        if 'date' in row and row['date']:
            message[0]['date'] = row['date'].strftime('%Y-%m-%d %H:%M:%S')
        if 'model_id' in row and row['model_id']:
            message[0]['model'] = get_model(row['model_id'])[0]['name']
            message[0]['model_id'] = row['model_id']

        dict_result.append(render_template('send_message.html', messages=message))
    return dict_result


def get_id(table_name, name, connect):
    s = select(table_name).where(table_name.c.name == name)
    result = connect.execute(s).fetchone()
    if not result:
        new_item = insert(table_name).values(name=name)
        result = connect.execute(new_item)
        item_id = result.inserted_primary_key[0]  # Получение автоинкрементного id
    else:
        item_id = result[0]  # Получение id из ответа
    return item_id


def send_messages(gpt_data, chat_id, chat_name):
    metadata, engine, chat, messages, open_ai_model = db_connect()
    with engine.connect() as connection:
        # mess = []
        # for each in gpt_data['messages']:
        #     mess.append(json.loads(json.dumps(each, ensure_ascii=False)))
        mess = json.dumps(gpt_data['messages'], ensure_ascii=False)
        if chat_id == 'new':
            chat_id = get_id(chat, chat_name, connection)
        gpt_raw = f"messages = {mess}\n" \
                  "response = client.chat.completions.create(\n" \
                  f"    temperature={gpt_data['temperature']},\n" \
                  f"    max_tokens={gpt_data['max_tokens']},\n" \
                  f"    model='{gpt_data['model']}',\n" \
                  f"    messages=messages\n" \
                  ")\n" \
                  "result = response.model_dump_json()"
        connection.execute(messages.insert(), [
            {
                'chat_id': chat_id,
                'date': datetime.datetime.now(),
                'message': json.dumps(gpt_data),
                'in_out': 0,
                'model_id': None,
                'temperature': 0,
                'max_tokens': 0,
                'usage': 0,
                'gpt_raw': gpt_raw
            }])
        connection.commit()
