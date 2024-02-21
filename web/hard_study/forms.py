from flask_wtf import FlaskForm
from flask_babel import _, lazy_gettext as _l
from wtforms import SubmitField, SelectField, HiddenField, IntegerField, BooleanField, StringField
from wtforms.validators import DataRequired

from web.hard_study.modls import LessonType, Language, LessonName


class SelectLessonForm(FlaskForm):
    lesson_name = SelectField(_l('Название урока'), coerce=int, validators=[DataRequired()])
    lesson_type = SelectField(_l('Тип урока'), coerce=int, validators=[DataRequired()])
    lesson_lang = SelectField(_l('Язык урока'), coerce=int, validators=[DataRequired()])

    what_request = HiddenField('what_request', validators=[DataRequired()])

    def __init__(self, current_user, app_lang_id, *args, **kwargs):
        super(SelectLessonForm, self).__init__(*args, **kwargs)
        lang_id_2 = current_user.lang2
        if not lang_id_2:
            lang_id_2 = app_lang_id

        self.lesson_type.choices = [(row.type_id, row.type) for row in LessonType.query.filter_by(lang_id=current_user.lang1).all()]
        self.lesson_lang.choices = [(row.id, row.code) for row in Language.query.all()]
        self.lesson_lang.default = lang_id_2
        self.lesson_name.choices = [(row.name_id, row.name) for row in LessonName.query.filter_by(lang_id=current_user.lang1).all()]
        self.lesson_type.default = LessonName.query.filter_by(name_id=current_user.cur_lesson_id, lang_id=current_user.lang1).first().type
        self.lesson_name.default = current_user.cur_lesson_id


class SettingForm(FlaskForm):
    num_new_sentences = IntegerField(_l('Количество новых слов в уроке'), validators=[DataRequired()])
    total_sentences = IntegerField(_l('Всего предложений в уроке'), validators=[DataRequired()])
    num_sent_warm_up = IntegerField(_l('Количество предложений для разминки'), validators=[DataRequired()])
    voice = SelectField(_l('Голос'), choices=['google_fast', 'google_slow', 'nova'], validators=[DataRequired()])
    num_showings1 = IntegerField(_l('Количество повторений для новых предложений'), validators=[DataRequired()])
    num_showings2 = IntegerField(_l('Количество повторений для предложений которые в процессе обучения'),
                                 validators=[DataRequired()])
    num_showings3 = IntegerField(_l('Количество повторений для предложений которые в повторении'),
                                 validators=[DataRequired()])
    use_dialect = BooleanField(_l('Использовать диалектические знаки при вводе?'), validators=[])
    shock_motivator = BooleanField(_l('Использовать электро мотиватор'), validators=[])
    smoke_motivator = BooleanField(_l('Использовать мотивацию никотином'), validators=[])
    money_motivator = BooleanField(_l('Использовать денежную мотивацию'), validators=[])
    submit = SubmitField(_l('Сохранить настройки'))


class SettingFormMoney(SettingForm):
    my_bitcoin_wallet = StringField(_l('Кошелек для вывода своих денег'), validators=[DataRequired()])
    no_my_bitcoin_wallet = StringField(_l('Кошелек для вывода проигранных денег'), validators=[DataRequired()])
    time_period = IntegerField(_l('На сколько дней распределить мотиватор?'), validators=[DataRequired()])
    lesson_per_day = IntegerField(_l('Сколько уроков в день?'), validators=[DataRequired()])
    money_motivator = BooleanField(_l('Использовать денежную мотивацию'), validators=[DataRequired()])
    activate_motivator = HiddenField(validators=[DataRequired()], default=False)


class StudyPhraseForm(FlaskForm):
    id_phrase = HiddenField(validators=[DataRequired()])
    was_help_flag = HiddenField(validators=[DataRequired()], default=False)
    was_help_sound_flag = HiddenField(validators=[DataRequired()], default=False)
    was_mistake_flag = HiddenField(validators=[DataRequired()], default=False)
    total_phrase = HiddenField(validators=[DataRequired()], default=False)


class StatisticForm(FlaskForm):
    statistic_id_phrase = HiddenField(validators=[DataRequired()])
    shows = HiddenField(validators=[DataRequired()], default=0)
    right_answer = HiddenField(validators=[DataRequired()], default=0)
    mistake_count = HiddenField(validators=[DataRequired()], default=0)
    new_phrase = HiddenField(validators=[DataRequired()], default=0)
    full_understand = HiddenField(validators=[DataRequired()], default=0)
    total_time = HiddenField(validators=[DataRequired()], default=0)
    time_start = HiddenField(validators=[DataRequired()], default=0)
