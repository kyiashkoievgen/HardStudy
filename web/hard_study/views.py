import datetime
import json

from flask import render_template, request, current_app, session, jsonify, redirect, url_for

from crypto import get_new_address, qrcode_gen, get_user_balance, get_currency_list, btc_price_converter, \
    create_webhook_if_not_exists
from . import hs
from flask_login import login_required, current_user

from .forms import SelectLessonForm, SettingForm, StudyPhraseForm, StatisticForm, SettingFormMoney
from .modls import Language, LessonName
from .study import StudyPhrases, save_study_progress, save_statistic, get_lesson_result
from .. import db


# @hs.route('/favicon.ico')
# def favicon():
#     return hs.send_static_file('favicon.ico')


# главная страница сайта меню все фреймы
@hs.route('/', methods=['GET'])
def index():
    selected_language = request.values.get('lang')
    if selected_language:
        selected_language = Language.query.filter_by(id=selected_language).first()
        session['language'] = selected_language.code
        if current_user.is_authenticated:
            current_user.lang1 = selected_language.id
            db.session.add(current_user)
            db.session.commit()
    else:
        selected_language = session.get('language')
        if not selected_language:
            selected_language = request.accept_languages.best_match(current_app.config['LANGUAGES'])

        selected_language = Language.query.filter_by(code=selected_language).first()
        if current_user.is_authenticated:
            user_language = current_user.lang1_code
            if user_language:
                selected_language = user_language
            else:
                current_user.lang1 = selected_language.id
                db.session.add(current_user)
                db.session.commit()
    current_lesson = None
    if current_user.is_authenticated:
        current_lesson = LessonName.query.filter_by(name_id=current_user.cur_lesson_id,
                                                    lang_id=current_user.lang1).first()
    languages = Language.query.all()
    return render_template('hs/layout.html', languages=languages, selected_language=selected_language,
                           lesson=current_lesson)


# домашняя страница сайта
@login_required
@hs.route('/home')
def home():
    return render_template('hs/content_home.html')


@login_required
@hs.route('/settings', methods=['GET', 'POST'])
def settings():
    current_user.calc_motivator_money()
    if current_user.btc_address is None:
        current_user.get_new_address()
    # create_webhook_if_not_exists(current_user.btc_address, url_for('hs.top_up_balance', _external=True),
    #                              current_user.api_key)
    form = SettingForm()
    form.currency_show.choices = get_currency_list()
    form2 = SettingFormMoney()
    if form.validate_on_submit():
        current_user.num_sent_warm_up = form.num_sent_warm_up.data
        current_user.num_new_sentences_lesson = form.num_new_sentences.data
        current_user.num_sentences_lesson = form.total_sentences.data
        current_user.voice = form.voice.data
        current_user.num_showings1 = form.num_showings1.data
        current_user.num_showings2 = form.num_showings2.data
        current_user.num_showings3 = form.num_showings3.data
        current_user.use_dialect = form.use_dialect.data
        current_user.shock_motivator = form.shock_motivator.data
        current_user.smoke_motivator = form.smoke_motivator.data
        current_user.currency_show = form.currency_show.data
        if not current_user.is_money_motivator_active:
            current_user.money_motivator = form.money_motivator.data
        db.session.add(current_user)
        db.session.commit()
    else:
        form.num_sent_warm_up.data = current_user.num_sent_warm_up
        form.num_new_sentences.data = current_user.num_new_sentences_lesson
        form.total_sentences.data = current_user.num_sentences_lesson
        form.voice.default = current_user.voice
        form.num_showings1.data = current_user.num_showings1
        form.num_showings2.data = current_user.num_showings2
        form.num_showings3.data = current_user.num_showings3
        form.voice.data = current_user.voice
        form.use_dialect.data = current_user.use_dialect
        form.shock_motivator.data = current_user.shock_motivator
        form.smoke_motivator.data = current_user.smoke_motivator
        form.money_motivator.data = current_user.money_motivator
        form.currency_show.data = current_user.currency_show

    if form2.validate_on_submit() and not current_user.is_money_motivator_active:
        current_user.time_period = form2.time_period.data
        current_user.lesson_per_day = form2.lesson_per_day.data
        current_user.money_per_day_start = int(current_user.motivator_btc_balance / current_user.time_period)
        current_user.is_money_motivator_active = True
        db.session.add(current_user)
        db.session.commit()
    else:
        form2.time_period.data = current_user.time_period
        form2.lesson_per_day.data = current_user.lesson_per_day
    balance = current_user.get_user_balance()

    return render_template('hs/settings.html', form=form, form2=form2, current_user=current_user, balance=balance)


@login_required
@hs.route('/top_up_money_motivator')
def top_up_money_motivator():
    val = request.args.get('val', type=int)  # Получаем параметр val как целое число
    if val is not None:
        val = btc_price_converter(current_user, val, to_btc=True)
        user_balance = get_user_balance(current_user)
        if user_balance['btc_balance'] >= val:
            current_user.motivator_btc_balance += val
            db.session.add(current_user)
            db.session.commit()
    return redirect(url_for('hs.settings'))


@login_required
@hs.route('/clean_motivator')
def clean_motivator():
    if not current_user.is_money_motivator_active:
        current_user.motivator_btc_balance = 0
        db.session.add(current_user)
        db.session.commit()
    return redirect(url_for('hs.settings'))


@login_required
@hs.route('/lesson_select/<lang_id>', methods=['GET', 'POST'])
def lesson_select(lang_id):
    lang_id_2 = current_user.lang2
    if not lang_id_2:
        lang_id_2 = lang_id
    cur_lesson_type = LessonName.query.filter_by(name_id=current_user.cur_lesson_id,
                                                 lang_id=current_user.lang1).first().type
    form = SelectLessonForm(current_user, lang_id)
    if form.validate_on_submit():
        current_user.cur_lesson_id = form.lesson_name.data
        lang_id_2 = form.lesson_lang.data
        if form.what_request.data == 'lesson_type':
            cur_lesson_type = form.lesson_type.data
            current_user.cur_lesson_id = LessonName.query.filter(
                LessonName.type == cur_lesson_type,
                LessonName.owner_id.in_([1, current_user.id])
            ).first().id
        current_user.lang1 = lang_id
        current_user.lang2 = lang_id_2
        db.session.add(current_user)
        db.session.commit()
    else:
        form.lesson_lang.data = lang_id_2
        form.lesson_name.data = current_user.cur_lesson_id
        form.lesson_type.data = cur_lesson_type

    lesson_name = LessonName.query.filter(
        LessonName.type == cur_lesson_type,
        LessonName.owner_id.in_([1, current_user.id])
    ).all()
    allowed_lessons_id = [lesson.id for lesson in lesson_name]
    if current_user.cur_lesson_id not in allowed_lessons_id:
        current_user.cur_lesson_id = allowed_lessons_id[0]
    lesson_content = StudyPhrases(current_user).take_lesson_content()
    # lesson_content = StudyProgress.take_lesson_content(current_user.id, current_user.cur_lesson_id, lang_id, lang_id_2)
    return render_template('hs/lesson_select.html', form=form, lesson_content=lesson_content, lang_id_2=lang_id_2)


@login_required
@hs.route('/study')
def study():
    current_user.calc_motivator_money()
    phrase_form = StudyPhraseForm()
    statistic_form = StatisticForm()
    return render_template('hs/study.html', current_user=current_user, phrase_form=phrase_form,
                           statistic_form=statistic_form)


@login_required
@hs.route('/get_lessons_data')
def lessons_data():
    study_data = StudyPhrases(current_user)
    study_data.prepare_study_data()
    return json.dumps(study_data.phrases)


@login_required
@hs.route('/save_lesson_data', methods=['GET', 'POST'])
def save_lesson_data():
    phrase_form = StudyPhraseForm()
    statistic_form = StatisticForm()
    if phrase_form.validate_on_submit():
        if phrase_form.id_phrase.data != 'false':
            save_study_progress(current_user, phrase_form.id_phrase.data, phrase_form.was_mistake_flag.data,
                                phrase_form.was_help_sound_flag.data, phrase_form.was_help_flag.data)

        if current_user.is_money_motivator_active:
            current_user.adjust_motivator(int(phrase_form.total_phrase.data))
            if phrase_form.id_phrase.data != 'false' and phrase_form.was_help_flag.data != 'true':
                current_user.calc_motivator_profit(int(phrase_form.total_phrase.data),
                                                   phrase_form.was_mistake_flag.data != 'true')
            elif phrase_form.id_phrase.data == 'false' and phrase_form.was_mistake_flag.data == 'true':
                current_user.calc_motivator_profit(int(phrase_form.total_phrase.data), False)
            return {
                'money_motivator': True,
                'money_motivator_dec': round(current_user.get_money_motivator_dec(), 2),
                'money_motivator_inc': round(current_user.get_money_motivator_inc(), 2),
                'money_for_today': f"{current_user.get_money_for_today():.2f}{current_user.currency_show}",
                'win_btc': f"{current_user.get_motivator_win_btc_today():.2f}{current_user.currency_show}",
                'lose_btc': f"{current_user.get_motivator_lose_btc_today():.2f}{current_user.currency_show}"
            }
        else:
            return 'ok'

    elif statistic_form.validate_on_submit():
        time_start = datetime.datetime.strptime(statistic_form.time_start.data, '%Y-%m-%dT%H:%M:%S.%fZ')
        save_statistic(current_user, int(statistic_form.statistic_id_phrase.data),
                       int(statistic_form.new_phrase.data), int(statistic_form.right_answer.data),
                       int(statistic_form.full_understand.data), int(statistic_form.mistake_count.data),
                       int(statistic_form.shows.data), int(statistic_form.total_time.data), time_start)
        return 'ok stat'
    else:
        return 'not ok'


@login_required
@hs.route('/lesson_result')
def lesson_result():
    current_user.count_day_lesson += 1
    db.session.add(current_user)
    db.session.commit()
    return get_lesson_result(current_user)


@login_required
@hs.route('/chat/<lesson_id>')
def chat(lesson_id):
    return render_template('hs/chat.html', lesson_id=lesson_id)


@login_required
@hs.route('/stat')
def stat():
    return render_template('hs/stat.html')


# о разработчиках
@hs.route('/about')
def about():
    return render_template('hs/content_about.html')


@login_required
@hs.route('/top_up_balance')
def top_up_balance():
    if current_user.btc_address is None:
        current_user.btc_address = get_new_address()
        db.session.add(current_user)
        db.session.commit()
        # Генерация QR-кода
    img_base64 = qrcode_gen(current_user.btc_address)

    # Отображение QR-кода и адреса на веб-странице
    return render_template('hs/btc_qr_code.html', img_data=img_base64, address=current_user.btc_address)


# @hs.route('/webhook', methods=['POST'])
# def handle_webhook():
#     data = request.json
#     address = data.get('address')
#     user_id = user_wallets.get(address)
#
#     if user_id:
#         # Обработайте уведомление, зная, что оно относится к user_id
#         print(f"Уведомление для пользователя {user_id}: {json.dumps(data, indent=2)}")
#         # Здесь можно добавить логику для отправки уведомления пользователю, например, через WebSocket
#     else:
#         print("Адрес кошелька не найден среди пользователей.")
#     return '', 200
