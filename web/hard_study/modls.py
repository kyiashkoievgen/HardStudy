from flask_sqlalchemy import SQLAlchemy
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
reg_sent_word = db.Table('reg_sent_word',
                         db.Column('sentences_id', db.Integer, db.ForeignKey('sentences.id')),
                         db.Column('word_id', db.Integer, db.ForeignKey('words.id'))
                         )

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
    text_hash = db.Column(db.String(40), unique=True)
    audio = db.Column(db.String(40))
    translate = db.relationship('Meaning',
                                backref=db.backref('sentences', lazy='joined'),
                                lazy='joined')
    words = db.relationship('Word',
                            secondary=reg_sent_word,
                            backref=db.backref('sentences', lazy='dynamic'),
                            lazy='dynamic')
    lesson_name = db.relationship('LessonName',
                                  secondary=reg_sent_les_name,
                                  backref=db.backref('lesson_name', lazy='dynamic'),
                                  lazy='dynamic')


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
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    lang1 = db.Column(db.Integer, db.ForeignKey('languages.id'))
    lang2 = db.Column(db.Integer, db.ForeignKey('languages.id'))
    cur_lesson_id = db.Column(db.Integer, db.ForeignKey('lessons_names.id'))

    @property
    def password(self):
        raise AttributeError('password is not readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


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
    study_date = db.Column(db.DateTime)
    total_show = db.Column(db.Integer)
    right_answer = db.Column(db.Integer)
    shock = db.Column(db.Integer)
    new_phrase = db.Column(db.Integer)
    full_understand = db.Column(db.Integer)
    total_time = db.Column(db.Integer)
    total_word_now = db.Column(db.Integer)
    total_sent_now = db.Column(db.Integer)
    time_start = db.Column(db.DateTime)
    time_stop = db.Column(db.DateTime)
    comment = db.Column(db.UnicodeText)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
