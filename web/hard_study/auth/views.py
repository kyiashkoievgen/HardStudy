from flask import render_template, redirect, request, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .forms import LoginForm, RegistrationForm
from ..email import send_email
from ..modls import User
from ... import db
from flask_babel import _


@auth.route('/login', methods=['GET', 'POST'])
def login():
    confirm_link = None
    if request.values.get('confirm_link') == '1':
        confirm_link = 1
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user, form.remember_me.data)
            if form.confirm_link.data == 'True' and not user.confirmed:
                token = user.generate_confirmation_token()
                send_email(current_app, user.email, _('Подтвердите свою учетную запись'), 'hs/auth/confirm', user=user, token=token)
                flash(_('Подтверждение было отправлено вам по электронной почте. Подтвердите учетную запись в течение 1 часа'))
            return redirect(request.args.get('next') or url_for('hs.index'))
        flash(_('Неверное имя пользователя или пароль'))
    return render_template('hs/auth/login.html', form=form, confirm_link=confirm_link)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.user_name.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(current_app, user.email, _('Подтвердите свою учетную запись'), 'hs/auth/confirm', user=user, token=token)
        flash(_('Подтверждение было отправлено вам по электронной почте. Подтвердите учетную запись в течение 1 часа'))
        return redirect(url_for('auth.login'))
    return render_template('hs/auth/login.html', form=form, register=True)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('hs.index'))
    if not current_user.confirm(token):
        flash(_('Ссылка для подтверждения недействительна или срок ее действия истек.'))
    else:
        flash(_('Вы подтвердили свою учетную запись. Спасибо!'))
    return redirect(url_for('hs.index'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    # flash('You have been logged out')
    return redirect(url_for('hs.index'))


@auth.before_app_request
def before_request():
    if current_user.is_authenticated and not current_user.confirmed and request.endpoint is not None and request.endpoint[:5] != 'auth.':
        logout_user()
        flash(_('Вы еще не подтвердили свою учетную запись.'))
        flash(_('Вы должны были получить электронное письмо со ссылкой для подтверждения.'))
        return redirect(url_for('auth.login', confirm_link=1))

