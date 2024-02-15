from flask_wtf import FlaskForm

from wtforms import SubmitField, SelectField, HiddenField, IntegerField, BooleanField, StringField
from wtforms.validators import DataRequired

from web.hard_study.modls import LessonType, Language, LessonName


class SelectLessonForm(FlaskForm):
    lesson_name = SelectField('Lesson name', coerce=int, validators=[DataRequired()])
    lesson_type = SelectField('Lesson type', coerce=int, validators=[DataRequired()])
    lesson_lang = SelectField('Lesson Language', coerce=int, validators=[DataRequired()])

    what_request = HiddenField('what_request', validators=[DataRequired()])

    def __init__(self, current_user, app_lang_id, *args, **kwargs):
        super(SelectLessonForm, self).__init__(*args, **kwargs)
        lang_id_2 = current_user.lang2
        if not lang_id_2:
            lang_id_2 = app_lang_id

        self.lesson_type.choices = [(row.id, row.type) for row in LessonType.query.all()]
        self.lesson_lang.choices = [(row.id, row.code) for row in Language.query.all()]
        self.lesson_lang.default = lang_id_2
        self.lesson_name.choices = [(row.id, row.name) for row in LessonName.query.all()]
        self.lesson_type.default = LessonName.query.filter_by(id=current_user.cur_lesson_id)
        self.lesson_name.default = current_user.cur_lesson_id


class SettingForm(FlaskForm):
    num_new_sentences = IntegerField('Количество новых слов в уроке', validators=[DataRequired()])
    total_sentences = IntegerField('Всего предложений в уроке', validators=[DataRequired()])
    num_sent_warm_up = IntegerField('Количество предложений для разминки', validators=[DataRequired()])
    voice = SelectField('Голос', choices=['google_fast', 'google_slow', 'nova'], validators=[DataRequired()])
    num_showings1 = IntegerField('Количество повторений для новых предложений', validators=[DataRequired()])
    num_showings2 = IntegerField('Количество повторений для предложений которые в процессе обучения',
                                 validators=[DataRequired()])
    num_showings3 = IntegerField('Количество повторений для предложений которые в повторении',
                                 validators=[DataRequired()])
    use_dialect = BooleanField('Использовать диалектические знаки при вводе?', validators=[])
    shock_motivator = BooleanField('Использовать электро мотиватор', validators=[])
    smoke_motivator = BooleanField('Использовать мотивацию никотином', validators=[])
    money_motivator = BooleanField('Использовать денежную мотивацию', validators=[])
    submit = SubmitField('Save settings')


class SettingFormMoney(SettingForm):
    my_bitcoin_wallet = StringField('Кошелек для вывода своих денег', validators=[DataRequired()])
    no_my_bitcoin_wallet = StringField('Кошелек для вывода проигранных денег', validators=[DataRequired()])
    time_period = IntegerField('На сколько дней распределить мотиватор?', validators=[DataRequired()])
    lesson_per_day = IntegerField('Сколько уроков в день?', validators=[DataRequired()])
    money_motivator = BooleanField('Использовать денежную мотивацию', validators=[DataRequired()])
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
