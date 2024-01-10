from flask import render_template, request, current_app

from . import hs
from flask_login import login_required

from .modls import Language, LessonType, LessonName, Sentence


@hs.cli.command('initdb')
def initdb_command():
    languages = Language.query.all()
    print(languages)
# главная страница сайта меню все фреймы
@hs.route('/')
def index():
    languages = Language.query.all()
    preferred_languages = request.accept_languages
    # Выбираем первый язык из списка, который поддерживается в вашем приложении
    selected_language = preferred_languages.best_match(current_app.config['LANGUAGES'])
    return render_template('hs/layout.html', languages=languages, selected_language=selected_language, lesson={'name': 'name', 'id': 12})


# домашняя страница сайта
@login_required
@hs.route('/home')
def home():
    return render_template('content_home.html')

@login_required
@hs.route('/settings')
def settings():
    return render_template('hs/settings.html')

@login_required
@hs.route('/lesson_select')
def lesson_select():
    languages = Language.query.all()
    lesson_type = LessonType.query.all()
    lesson_name = LessonName.query.all()
    lesson_content = Sentence.query()
    return render_template('hs/lesson_select.html', languages=languages, lesson_type=lesson_type,
                           lesson_name=lesson_name)

@login_required
@hs.route('/study/<lesson_id>')
def study(lesson_id):
    return render_template('hs/study.html', lesson_id=lesson_id)

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
    return render_template('content_about.html')

