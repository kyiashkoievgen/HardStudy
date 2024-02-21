import datetime
from flask import render_template, request, current_app, session

from . import hs
from flask_login import login_required, current_user

from .forms import SelectLessonForm, SettingForm, StudyPhraseForm, StatisticForm, SettingFormMoney
from .modls import Language, LessonName
from .study import StudyPhrases, save_study_progress, save_statistic, get_lesson_result
from .. import db


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
    current_lesson = None
    if current_user.is_authenticated:
        current_lesson = LessonName.query.filter_by(name_id=current_user.cur_lesson_id, lang_id=current_user.lang1).first()
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
    money_motivator = request.values.get('money_motivator')
    if current_user.is_money_motivator_active:
        money_motivator = True
    elif money_motivator is None:
        money_motivator = current_user.money_motivator
    else:
        if money_motivator == 'y':
            money_motivator = True
        else:
            money_motivator = False
        current_user.money_motivator = money_motivator
        db.session.add(current_user)
        db.session.commit()
    if money_motivator:
        form = SettingFormMoney()
    else:
        form = SettingForm()
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
        current_user.money_motivator = money_motivator
        if money_motivator and (not current_user.is_money_motivator_active):
            current_user.my_bitcoin_wallet = form.my_bitcoin_wallet.data
            current_user.no_my_bitcoin_wallet = form.no_my_bitcoin_wallet.data
            current_user.time_period = form.time_period.data
            current_user.lesson_per_day = form.lesson_per_day.data
            if form.activate_motivator.data == 'True':
                current_user.is_money_motivator_active = True
                current_user.time_money_start = datetime.datetime.now()
                current_user.btc_per_day = current_user.btc_balance_in / current_user.time_period
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
        form.money_motivator.data = money_motivator
        if money_motivator:
            form.my_bitcoin_wallet.data = current_user.my_bitcoin_wallet
            form.no_my_bitcoin_wallet.data = current_user.no_my_bitcoin_wallet
            form.time_period.data = current_user.time_period
            form.lesson_per_day.data = current_user.lesson_per_day

    return render_template('hs/settings.html', form=form, current_user=current_user)


@login_required
@hs.route('/lesson_select/<lang_id>', methods=['GET', 'POST'])
def lesson_select(lang_id):
    lang_id_2 = current_user.lang2
    if not lang_id_2:
        lang_id_2 = lang_id
    cur_lesson_type = LessonName.query.filter_by(name_id=current_user.cur_lesson_id, lang_id=current_user.lang1).first().type
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
    study_data = StudyPhrases(current_user)
    study_data.prepare_study_data()
    phrase_form = StudyPhraseForm()
    statistic_form = StatisticForm()
    return render_template('hs/study.html', study_data=study_data, phrase_form=phrase_form,
                           statistic_form=statistic_form)


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
            mistake = False
            current_user.adjust_motivator(int(phrase_form.total_phrase.data))
            if phrase_form.was_mistake_flag.data == 'true' or phrase_form.was_help_flag.data == 'true':
                mistake = True
            current_user.calc_motivator_profit(int(phrase_form.total_phrase.data), not mistake)

        return {
            'money_motivator': True,
            'money_motivator_dec': current_user.money_motivator_dec,
            'money_motivator_inc': current_user.money_motivator_inc,
            'money_for_today': current_user.money_for_today - current_user.win_btc - current_user.lose_btc,
            'win_btc': current_user.win_btc,
            'lose_btc': current_user.lose_btc
        }

    elif statistic_form.validate_on_submit():
        time_start = datetime.datetime.strptime(statistic_form.time_start.data, '%Y-%m-%dT%H:%M:%S.%fZ')
        save_statistic(current_user, int(statistic_form.statistic_id_phrase.data), time_start,
                       int(statistic_form.new_phrase.data), int(statistic_form.right_answer.data),
                       int(statistic_form.full_understand.data), int(statistic_form.mistake_count.data),
                       int(statistic_form.shows.data), int(statistic_form.total_time.data))
        return 'ok stat'
    else:
        return 'not ok'


@login_required
@hs.route('/lesson_result')
def lesson_result():
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
