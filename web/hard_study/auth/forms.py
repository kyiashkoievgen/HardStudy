from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Email
from flask_babel import _, lazy_gettext as _l
from web.hard_study.modls import User


class LoginForm(FlaskForm):
    email = StringField(_l('Почта'), validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField(_l('Пароль'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Оставаться в системе'))
    confirm_link = HiddenField('confirm_link', default=False, validators=[DataRequired()])
    submit = SubmitField(_l('Войти'))


class RegistrationForm(FlaskForm):
    user_name = StringField(_l('Имя пользователя'), validators=[DataRequired(), Length(1, 64)])
    email = StringField(_l('Почта'), validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField(_l('Пароль'),
                             validators=[DataRequired(), EqualTo('password2', message=_l('Пароли должны совпадать.'))])
    password2 = PasswordField(_l('Подтвердить пароль'), validators=[DataRequired()])
    submit = SubmitField(_l('Регистрация'))

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(_l('Такая почта уже зарегистрированная'))
