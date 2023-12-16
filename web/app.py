import datetime

from flask import Flask, render_template, request, redirect, url_for, flash, make_response, json
from gpt_db import get_chats, get_chats_messages, get_model, send_messages
from study import WebStudy, Phrase
from db import DB

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# главная страница сайта меню все фреймы
@app.route('/')
def index():
    return render_template('layout.html')

# домашняя страница сайта
@app.route('/home')
def home():
    return render_template('content_home.html')

# о разработчиках
@app.route('/about')
def about():
    return render_template('content_about.html')

# настройки
@app.route('/settings')
def settings():
    db = DB()
    name_settings = db.get_settings_profile()
    return render_template('setting.html', Settings=db.app_setting_init(), name_settings=name_settings)

# изменения профайла настроек и установки их по умолчанию
@app.route('/change_setting_profile', methods=['GET'])
def change_setting_profile():
    db = DB()
    try:
        sett = request.values.get('profile_id')
        db.set_setting_def(int(sett))
    except:
        flash('Пожалуйста, правильно заполните все поля!')

    return redirect(url_for('settings'))

# чтение и проверка данных с формы настроек
def get_form_data():
    sett = {}
    try:
        sett['comport'] = request.form.get('comport')
        sett['profile_name'] = request.form.get('profile_name')
        sett['lesson_per_day'] = int(request.form.get('lesson_per_day'))
        sett['time_beetween_study_1'] = int(request.form.get('time_beetween_study_1'))
        sett['time_beetween_study_2'] = int(request.form.get('time_beetween_study_2'))
        sett['time_beetween_study_3'] = int(request.form.get('time_beetween_study_3'))
        sett['time_beetween_study_4'] = int(request.form.get('time_beetween_study_4'))
        sett['time_beetween_study_5'] = int(request.form.get('time_beetween_study_5'))
        sett['time_beetween_study_6'] = int(request.form.get('time_beetween_study_6'))
        sett['show_time_sent'] = int(request.form.get('show_time_sent'))
        sett['sent_in_less'] = int(request.form.get('sent_in_less'))
        sett['punish_time_1'] = int(request.form.get('punish_time_1'))
        sett['right_answer_1'] = int(request.form.get('right_answer_1'))
        sett['right_answer_2'] = int(request.form.get('right_answer_2'))
        sett['apostrophe'] = bool(request.form.get('apostrophe'))
        # flash('Изменения сохранены!')
    except:
        flash('Пожалуйста, правильно заполните все поля!')

    return sett


# сохранение настроек
@app.route('/save_settings', methods=['POST'])
def save_settings_form():
    try:
        db = DB()
        db.save_settings(get_form_data())
    except:
        flash('Пожалуйста, правильно заполните все поля!')
    return redirect(url_for('settings'))

# создание нового профайла с настройками
@app.route('/create_new_profile', methods=['POST'])
def create_new_profile():
    try:
        db = DB()
        sett = get_form_data()
        db.insert_settings(sett)
    except:
        flash('Пожалуйста, правильно заполните все поля!')
    return redirect(url_for('settings'))

# загрузка страницу с фреймами для списков всех уроков и уроков пользователя в куках храним фильтры что выбрал
# пользователь
@app.route('/lessons')
def lessons():
    lesson_filter = {'mode': request.cookies.get('mode'),
                     'lang1': request.cookies.get('lang1'),
                     'lang2': request.cookies.get('lang2')
                     }
    db = DB()
    list_mode = db.get_all_mode_lang_name()
    list_lang = db.get_all_mode_lang_name(mode=False)
    return render_template('lessons.html', list_mode=list_mode, list_lang=list_lang,
                           lesson_filter=lesson_filter)

# вывод всех уроков и уроков пользователя
@app.route('/all_lesson', methods=['GET'])
def all_lesson():
    # если есть куки с фильтрами то достаем их если нет то устанавливаем
    lesson_filter = {'mode': request.cookies.get('mode'),
                     'lang1': request.cookies.get('lang1'),
                     'lang2': request.cookies.get('lang2'),
                     request.values.get('select_name'): request.values.get('value')}

    db = DB()
    my_lesson = request.values.get('my_lesson')
    list_all_lesson = db.get_all_lesson(lesson_filter, my_lesson=my_lesson)
    if my_lesson:
        all_studied = db.get_studied_sent_word([lesson['id'] for lesson in list_all_lesson])
        for lesson, stat in zip(list_all_lesson, all_studied):
            lesson['studied_sent'] = len(stat['studied_sent'])
            lesson['studied_word'] = len(stat['studied_word'])
            lesson['full_understand'] = stat['full_understand']
    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    response = make_response(render_template('all_lesson.html', list_all_lesson=list_all_lesson))
    if not lesson_filter['mode'] is None:
        response.set_cookie('mode', lesson_filter['mode'], expires=expires)
    if not lesson_filter['lang1'] is None:
        response.set_cookie('lang1', lesson_filter['lang1'], expires=expires)
    if not lesson_filter['lang2'] is None:
        response.set_cookie('lang2', lesson_filter['lang2'], expires=expires)
    return response

@app.route('/start_study', methods=['POST'])
def start_study():
    lesson_id_name = []
    req = request.form.to_dict()
    for lesson_id in req.keys():
        lesson_id_name.append({
            'id': lesson_id,
            'name': req[lesson_id]
        })
    study = WebStudy(req.keys())
    study_data, add_sent_num = study.get_study_data_as_list()
    return render_template('study.html', lesson_id_name=lesson_id_name, study_data=study_data,
                           add_sent_num=add_sent_num)

@app.route('/save_result', methods=['POST'])
def save_result():
    req = request.form.to_dict()
    study = WebStudy(json.loads(req['lessons']))
    statistic = study.save_progress_from_web(json.loads(req['response']), req['add_sent_num'], req['shock_count'],
                                             req['timeStart'], req['timeStop'], req['duration'])
    return render_template('stat.html', stat=statistic)

@app.route('/stat')
def stat():
    return render_template('stat.html')

@app.route('/create_lesson_form')
def create_lesson_form():
    db = DB()
    list_lang = db.get_all_mode_lang_name(mode=False)
    return render_template('create_lesson.html', list_lang=list_lang)

@app.route('/create_lesson', methods=['POST'])
def create_lesson():
    req = request.form.to_dict()
    if req['name_lesson']=='':
        flash('Пожалуйста, правильно заполните все поля!')
    return redirect(url_for('create_lesson_form'))

@app.route('/chatgpt')
def chatgpt():
    chats_names = get_chats()
    return render_template('chatgpt.html', chats=chats_names)

@app.route('/chat_messages/<chat_id>')
def chat_messages(chat_id):
    chats_messages = get_chats_messages(chat_id)
    models = get_model()
    return render_template('chat_messages.html', messages=chats_messages, models=models, chat_id=chat_id)

@app.route('/chat_messages/new/<chat_id>', methods=['POST'])
def chat_messages_new(chat_id):
    gpt_data = request.form.to_dict()['gpt_request']
    chat_name = request.form.get('chat_name')
    send_messages(gpt_data, chat_id, chat_name)
    return redirect(url_for('chat_messages', chat_id=chat_id))

if __name__ == '__main__':
    app.run(debug=True)
