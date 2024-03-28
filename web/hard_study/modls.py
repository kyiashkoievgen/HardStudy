from datetime import datetime
from flask import current_app
from itsdangerous import URLSafeTimedSerializer as Serializer, SignatureExpired, BadSignature
from sqlalchemy import Column, Integer, ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from crypto import btc_price_converter, get_user_balance, get_new_address, get_btc_rate
from mysql.models import BaseMeaning, BaseLanguage, BaseLessonName, BaseLessonType, BaseRegSentWord, BaseSentence, \
    BaseWord, BaseUser, BaseRole, BaseStudyProgress, BaseWordProgress, BaseStatistic, BaseTransactionHistory
from .. import login_manager, db


class Meaning(BaseMeaning, db.Model):
    __tablename__ = 'meanings'


class Language(BaseLanguage, db.Model):
    __tablename__ = 'languages'
    sentences = db.relationship('Sentence', backref='lang')


class LessonName(BaseLessonName, db.Model):
    __tablename__ = 'lessons_names'


class LessonType(BaseLessonType, db.Model):
    __tablename__ = 'lesson_types'


# описывает взаимоотношение многие ко многим. какие слова находятся в предложении
class RegSentWord(BaseRegSentWord, db.Model):
    __tablename__ = 'reg_sent_word'


# описывает взаимоотношение многие ко многим. предложении слова находятся в разных лекциях
reg_sent_les_name = db.Table('reg_sent_les_name',
                             db.Column('sentences_id', db.Integer, db.ForeignKey('sentences.id')),
                             db.Column('lessons_names_id', db.Integer, db.ForeignKey('lessons_names.id'))
                             )


# описывает предложения
class Sentence(BaseSentence, db.Model):
    __tablename__ = 'sentences'
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
class Word(BaseWord, db.Model):
    __tablename__ = 'words'


class User(BaseUser, UserMixin, db.Model):
    __tablename__ = 'users'
    lang1 = Column(Integer, ForeignKey('languages.id'))
    lang1_code = db.relationship('Language', foreign_keys=[lang1], backref='lang_code')
    money_motivator_day = None
    money_motivator_hours = None
    money_motivator_dec = None
    money_motivator_inc = None
    money_for_today = None
    btc_per_lesson = None
    motivator_btc_per_day = None

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

    def get_new_address(self):
        self.btc_address = get_new_address()
        db.session.add(self)
        db.session.commit()
        return self.btc_address

    def currency_rate_update(self):
        rate = get_btc_rate(self)
        if rate is not None:
            self.currency_rate = rate
            db.session.add(self)
            db.session.commit()

    def calc_motivator_money(self):
        if self.is_money_motivator_active:
            # Время сколько работает мотиватор
            t = datetime.now() - self.time_money_start
            self.money_motivator_day = t.days + 1
            self.money_motivator_hours = int(24 - t.seconds / 3600)
            self.motivator_btc_per_day = int(self.motivator_btc_balance/(self.time_period-t.days))
            # сколько денег должно быть если заниматься каждый день, если нет то списываем разницу
            money_diff = self.motivator_btc_balance - (self.time_period - t.days) * self.money_per_day_start
            self.money_for_today = self.motivator_btc_per_day - self.motivator_win_btc_today - self.motivator_lose_btc_today
            if money_diff > 0:
                money_diff = money_diff - self.motivator_lose_btc_today - self.motivator_win_btc_today
                if money_diff < 0:
                    money_diff = 0
                self.motivator_btc_balance = self.motivator_btc_balance - self.\
                    motivator_win_btc_today - self.motivator_lose_btc_today - money_diff
                # распределяем деньги и обнуляем ежедневный счетчик выплат
                self.user_btc_balance += int(self.motivator_win_btc_today)
                self.motivator_win_btc_today = 0
                self.my_btc_balance += (int(self.motivator_lose_btc_today) + money_diff)
                self.motivator_lose_btc_today = 0
                self.count_day_lesson = 0
                db.session.add(self)
                db.session.commit()
                # проверяем не закончились ли деньги на мотиваторе
                if self.motivator_btc_balance < self.motivator_btc_per_day / self.lesson_per_day:
                    self.is_money_motivator_active = False
                    db.session.add(self)
                    db.session.commit()

    # устанавливаем на сколько увеличивать или уменьшать мотиватор на уроке
    def adjust_motivator(self, num_sent):
        self.calc_motivator_money()
        if self.is_money_motivator_active:
            lesson = self.lesson_per_day - self.count_day_lesson
            if lesson == 0:
                self.btc_per_lesson = 0
                self.money_motivator_inc = 0
                self.money_motivator_dec = 0
            else:
                self.btc_per_lesson = int(self.motivator_btc_per_day / lesson - self.motivator_win_btc_today - self.motivator_lose_btc_today)
                self.money_motivator_inc = self.btc_per_lesson / num_sent
                self.money_motivator_dec = self.money_motivator_inc * self.difficult_money

    def calc_motivator_profit(self, num_sent, inc=True):
        if self.is_money_motivator_active:
            if inc:
                self.motivator_win_btc_today += self.money_motivator_inc
            else:
                self.motivator_lose_btc_today += self.money_motivator_dec

            db.session.add(self)
            db.session.commit()
            self.calc_motivator_money()
            self.adjust_motivator(num_sent)

    def day_money_to_user(self):
        self.user_btc_balance += self.money_for_today
        self.money_for_today = 0
        db.session.add(self)
        db.session.commit()

# баланс пользователя в его валюте
    def get_user_balance(self):
        if self.btc_address is None:
            return None
        currency_rate = btc_price_converter(self, 1)
        balance = get_user_balance(self)
        balance['btc_transaction_in_progress'] = balance['btc_transaction_in_progress'] * currency_rate
        balance['btc_balance'] = balance['btc_balance'] * currency_rate
        balance['unconfirmed_balance'] = balance['unconfirmed_balance'] * currency_rate
        return balance

# баланс мотиватора в его валюте
    def get_motivator_balance(self):
        if self.btc_address is None:
            return None
        return btc_price_converter(self, self.motivator_btc_balance)

    def get_motivator_btc_per_day(self):
        return btc_price_converter(self, self.motivator_btc_per_day)

    def get_motivator_win_btc_today(self):
        return btc_price_converter(self, self.motivator_win_btc_today)

    def get_motivator_lose_btc_today(self):
        return btc_price_converter(self, self.motivator_lose_btc_today)

    def get_money_for_today(self):
        return btc_price_converter(self, self.money_for_today)

    def get_money_motivator_dec(self):
        return btc_price_converter(self, self.money_motivator_dec)

    def get_money_motivator_inc(self):
        return btc_price_converter(self, self.money_motivator_inc)


class Role(BaseRole, db.Model):
    __tablename__ = 'roles'
    users = db.relationship('User', backref='role')


class StudyProgress(BaseStudyProgress, db.Model):
    __tablename__ = 'study_progress'


class WordProgress(BaseWordProgress, db.Model):
    __tablename__ = 'word__progress'


class Statistic(BaseStatistic, db.Model):
    __tablename__ = 'statistics'


class TransactionHistory(BaseTransactionHistory, db.Model):
    __tablename__ = 'transaction_history'


@login_manager.user_loader
def load_user(user_id):
    current_user = User.query.get(int(user_id))
    return current_user
