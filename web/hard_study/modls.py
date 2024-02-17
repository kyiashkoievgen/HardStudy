import time
from datetime import datetime, timedelta

from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeTimedSerializer as Serializer, SignatureExpired, BadSignature
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from .. import login_manager, db


class Meaning(db.Model):
    __tablename__ = 'meanings'
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.String(40), unique=True)


class Language(db.Model):
    __tablename__ = 'languages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), unique=True)
    code = db.Column(db.String(5), unique=True)
    sentences = db.relationship('Sentence', backref='lang')


class LessonName(db.Model):
    __tablename__ = 'lessons_names'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15))
    type = db.Column(db.Integer, db.ForeignKey('lesson_types.id'))
    description = db.Column(db.UnicodeText)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class LessonType(db.Model):
    __tablename__ = 'lesson_types'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(15), unique=True)


# описывает взаимоотношение многие ко многим. какие слова находятся в предложении
class RegSentWord(db.Model):
    __tablename__ = 'reg_sent_word'
    sentences_id = db.Column(db.Integer, db.ForeignKey('sentences.id'), primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), primary_key=True)


# описывает взаимоотношение многие ко многим. предложении слова находятся в разных лекциях
reg_sent_les_name = db.Table('reg_sent_les_name',
                             db.Column('sentences_id', db.Integer, db.ForeignKey('sentences.id')),
                             db.Column('lessons_names_id', db.Integer, db.ForeignKey('lessons_names.id'))
                             )


# описывает предложения
class Sentence(db.Model):
    __tablename__ = 'sentences'
    id = db.Column(db.Integer, primary_key=True)
    language_id = db.Column(db.Integer, db.ForeignKey('languages.id'))
    meaning_id = db.Column(db.Integer, db.ForeignKey('meanings.id'))
    text = db.Column(db.UnicodeText)
    text_hash = db.Column(db.String(64), unique=True)
    audio = db.Column(db.Boolean)
    img = db.Column(db.Boolean)
    translate = db.relationship('Meaning',
                                backref=db.backref('sentences', lazy='joined'),
                                lazy='joined')
    # words = db.relationship('Word',
    #                         secondary=reg_sent_word,
    #                         backref=db.backref('words', lazy='dynamic'),
    #                         lazy='dynamic')
    lesson_name = db.relationship('LessonName',
                                  secondary=reg_sent_les_name,
                                  backref=db.backref('lesson_name', lazy='dynamic'),
                                  lazy='dynamic')
    study_progress = db.relationship('StudyProgress',
                                     backref=db.backref('study_progress', lazy='joined'),
                                     lazy='joined'
                                     )


# описывает слова из которых состоит предложения
class Word(db.Model):
    __tablename__ = 'words'
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(30), unique=True)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    email = db.Column(db.String(64), unique=True, index=True)
    confirmed = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    lang1 = db.Column(db.Integer, db.ForeignKey('languages.id'))
    lang2 = db.Column(db.Integer, db.ForeignKey('languages.id'))
    cur_lesson_id = db.Column(db.Integer, db.ForeignKey('lessons_names.id'), nullable=False, default=1)
    num_new_sentences_lesson = db.Column(db.Integer, nullable=False, default=5)
    num_sentences_lesson = db.Column(db.Integer, nullable=False, default=20)
    num_sent_warm_up = db.Column(db.Integer, nullable=False, default=3)
    num_showings1 = db.Column(db.Integer, nullable=False, default=10)
    num_showings2 = db.Column(db.Integer, nullable=False, default=5)
    num_showings3 = db.Column(db.Integer, nullable=False, default=5)
    voice = db.Column(db.String(10), nullable=False, default='google_slow')
    use_dialect = db.Column(db.Boolean, nullable=False, default=False)
    shock_motivator = db.Column(db.Boolean, nullable=False, default=False)
    smoke_motivator = db.Column(db.Boolean, nullable=False, default=False)
    money_motivator = db.Column(db.Boolean, nullable=False, default=False)
    bitcoin_wallet_in = db.Column(db.String(128))
    my_bitcoin_wallet = db.Column(db.String(128))
    no_my_bitcoin_wallet = db.Column(db.String(128))
    btc_balance_in = db.Column(db.Float, nullable=False, default=0)
    btc_balance_my_out = db.Column(db.Float, nullable=False, default=0)
    btc_balance_no_my_out = db.Column(db.Float, nullable=False, default=0)
    time_period = db.Column(db.Integer, nullable=False, default=30)
    lesson_per_day = db.Column(db.Integer, nullable=False, default=2)
    difficult_money = db.Column(db.Float, nullable=False, default=1.5)
    is_money_motivator_active = db.Column(db.Boolean, nullable=False, default=False)
    time_money_start = db.Column(db.DateTime)
    btc_per_day = db.Column(db.Float)
    win_btc = db.Column(db.Float)
    lose_btc = db.Column(db.Float)
    money_motivator_day = None
    money_motivator_hours = None
    money_motivator_dec = None
    money_motivator_inc = None
    money_for_today = None
    btc_per_lesson = None

    @property
    def password(self):
        raise AttributeError('password is not readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        token = s.dumps({'user_id': self.id})
        return token

    def confirm(self, token, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=expiration)
        except SignatureExpired:
            return False
        except BadSignature:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def calc_motivator_money(self):
        if self.is_money_motivator_active:
            t = datetime.now() - self.time_money_start
            self.money_motivator_day = t.days + 1
            self.money_motivator_hours = int(24 - t.seconds / 3600)
            money_diff = self.btc_balance_in - (self.time_period - t.days) * self.btc_per_day
            self.money_for_today = self.btc_balance_in - (
                    self.time_period - t.days - 1) * self.btc_per_day
            if money_diff > 0:
                money_diff = money_diff - self.lose_btc - self.win_btc
                if money_diff < 0:
                    money_diff = 0
                self.btc_balance_in = self.btc_balance_in - self.win_btc - self.lose_btc - money_diff
                self.btc_balance_my_out += self.win_btc
                self.win_btc = 0
                self.btc_balance_no_my_out += (self.lose_btc + money_diff)
                self.lose_btc = 0

                db.session.add(self)
                db.session.commit()
            if self.btc_balance_in < self.btc_per_day / self.lesson_per_day:
                self.is_money_motivator_active = False
                db.session.add(self)
                db.session.commit()

    def adjust_motivator(self, num_sent):
        if self.is_money_motivator_active:
            self.btc_per_lesson = self.btc_per_day / self.lesson_per_day
            self.money_motivator_inc = (self.btc_per_day - self.lose_btc - self.win_btc) / num_sent
            self.money_motivator_dec = self.money_motivator_inc * self.difficult_money

    def calc_motivator_profit(self, num_sent, inc=True):
        if self.is_money_motivator_active:
            if inc:
                self.win_btc += self.money_motivator_inc
            else:
                self.lose_btc += self.money_motivator_dec

            db.session.add(self)
            db.session.commit()
            self.calc_motivator_money()
            self.adjust_motivator(num_sent)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')


class StudyProgress(db.Model):
    __tablename__ = 'study_progress'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    lesson_name_id = db.Column(db.Integer, db.ForeignKey('lessons_names.id'))
    sentence_id = db.Column(db.Integer, db.ForeignKey('sentences.id'))
    show_count = db.Column(db.Integer)
    right_count = db.Column(db.Integer)
    remember = db.Column(db.Integer)
    last_show_time = db.Column(db.DateTime)


class WordProgress(db.Model):
    __tablename__ = 'word__progress'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    lesson_name_id = db.Column(db.Integer, db.ForeignKey('lessons_names.id'))
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'))
    show_count = db.Column(db.Integer)
    right_count = db.Column(db.Integer)
    remember = db.Column(db.Integer)
    last_show_time = db.Column(db.DateTime)


class Statistic(db.Model):
    __tablename__ = 'statistics'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    lesson_name_id = db.Column(db.Integer, db.ForeignKey('lessons_names.id'))
    sentence_id = db.Column(db.Integer, db.ForeignKey('sentences.id'))
    shows = db.Column(db.Integer)
    right_answer = db.Column(db.Integer)
    mistake_count = db.Column(db.Integer)
    new_phrase = db.Column(db.Integer)
    full_understand = db.Column(db.Integer)
    total_time = db.Column(db.Integer)
    time_start = db.Column(db.DateTime)
    comment = db.Column(db.UnicodeText)


@login_manager.user_loader
def load_user(user_id):
    current_user = User.query.get(int(user_id))
    current_user.calc_motivator_money()
    return current_user
