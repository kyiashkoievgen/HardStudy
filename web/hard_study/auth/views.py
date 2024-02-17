from flask import render_template, redirect, request, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .forms import LoginForm, RegistrationForm
from ..email import send_email
from ..modls import User
from ... import db


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
                send_email(current_app, user.email, 'Confirm Your Account', 'hs/auth/confirm', user=user, token=token)
                flash('A confirmation email has been sent to you by email. Confirm account during 1 hour')
            return redirect(request.args.get('next') or url_for('hs.index'))
        flash('Invalid user name or password')
    return render_template('hs/auth/login.html', form=form, confirm_link=confirm_link)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.user_name.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(current_app, user.email, 'Confirm Your Account', 'hs/auth/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email. Confirm account during 1 hour')
        return redirect(url_for('auth.login'))
    return render_template('hs/auth/login.html', form=form, register=True)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('hs.index'))
    if not current_user.confirm(token):
        flash('The confirmation link is invalid or has expired.')
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
        flash('You have not confirmed your account yet.')
        flash('You should have received an email with a confirmation link.')
        return redirect(url_for('auth.login', confirm_link=1))

