from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField
from wtforms.validators import DataRequired


class SelectLessonForm(FlaskForm):
    lesson_name = SelectField('Lesson name', validators=[DataRequired])
    lesson_lang = SelectField('Lesson Language', validators=[DataRequired])
    submit = SubmitField('Select Lesson')
