from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, UnicodeText, Boolean, Float, DateTime, func

Base = declarative_base()


class BaseMeaning(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    img = Column(String(40), unique=True)


class BaseLanguage(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    name = Column(String(15), unique=True)
    code = Column(String(5), unique=True)


class BaseLessonName(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    name = Column(String(15))
    type = Column(Integer, ForeignKey('lesson_types.type_id'))
    description = Column(UnicodeText)
    owner_id = Column(Integer, ForeignKey('users.id'))
    name_id = Column(Integer)
    lang_id = Column(Integer, ForeignKey('languages.id'))


class BaseLessonType(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    type = Column(String(15), unique=True)
    type_id = Column(Integer)
    lang_id = Column(Integer, ForeignKey('languages.id'))


# описывает взаимоотношение многие ко многим. какие слова находятся в предложении
class BaseRegSentWord(Base):
    __abstract__ = True
    sentences_id = Column(Integer, ForeignKey('sentences.id'), primary_key=True)
    word_id = Column(Integer, ForeignKey('words.id'), primary_key=True)


# описывает предложения
class BaseSentence(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    language_id = Column(Integer, ForeignKey('languages.id'))
    meaning_id = Column(Integer, ForeignKey('meanings.id'))
    text = Column(UnicodeText)
    text_hash = Column(String(64), unique=True)
    audio = Column(Boolean)
    img = Column(Boolean)


# описывает слова из которых состоит предложения
class BaseWord(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    word = Column(String(30), unique=True)


class BaseUser(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    username = Column(String(64))
    email = Column(String(64), unique=True, index=True)
    confirmed = Column(Boolean, default=False)
    role_id = Column(Integer, ForeignKey('roles.id'))
    password_hash = Column(String(128))
    lang1 = Column(Integer, ForeignKey('languages.id'))
    lang2 = Column(Integer, ForeignKey('languages.id'), nullable=False, default=4)
    cur_lesson_id = Column(Integer, ForeignKey('lessons_names.id'), nullable=False, default=1)
    num_new_sentences_lesson = Column(Integer, nullable=False, default=5)
    num_sentences_lesson = Column(Integer, nullable=False, default=20)
    num_sent_warm_up = Column(Integer, nullable=False, default=3)
    num_showings1 = Column(Integer, nullable=False, default=10)
    num_showings2 = Column(Integer, nullable=False, default=5)
    num_showings3 = Column(Integer, nullable=False, default=5)
    voice = Column(String(10), nullable=False, default='google_slow')
    use_dialect = Column(Boolean, nullable=False, default=False)
    shock_motivator = Column(Boolean, nullable=False, default=False)
    smoke_motivator = Column(Boolean, nullable=False, default=False)
    money_motivator = Column(Boolean, nullable=False, default=False)
    time_period = Column(Integer, nullable=False, default=30)
    lesson_per_day = Column(Integer, nullable=False, default=2)
    count_day_lesson = Column(Integer, nullable=False, default=0)
    difficult_money = Column(Float, nullable=False, default=0.1)
    is_money_motivator_active = Column(Boolean, nullable=False, default=False)
    time_money_start = Column(DateTime)
    money_per_day_start = Column(Integer, nullable=False, default=0)
    # биткоин data
    btc_address = Column(String(100))
    my_btc_balance = Column(Integer, nullable=False, default=0)
    user_btc_balance = Column(Integer, nullable=False, default=0)
    motivator_btc_balance = Column(Integer, nullable=False, default=0)
    motivator_win_btc_today = Column(Float, nullable=False, default=0)
    motivator_lose_btc_today = Column(Float, nullable=False, default=0)
    currency_show = Column(String(10), nullable=False, default='BTC')
    currency_rate = Column(Float, nullable=False, default=1)


class BaseRole(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True)


class BaseStudyProgress(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    lesson_name_id = Column(Integer, ForeignKey('lessons_names.id'))
    sentence_id = Column(Integer, ForeignKey('sentences.id'))
    show_count = Column(Integer)
    right_count = Column(Integer)
    remember = Column(Integer)
    last_show_time = Column(DateTime)


class BaseWordProgress(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    lesson_name_id = Column(Integer, ForeignKey('lessons_names.id'))
    word_id = Column(Integer, ForeignKey('words.id'))
    show_count = Column(Integer)
    right_count = Column(Integer)
    remember = Column(Integer)
    last_show_time = Column(DateTime)


class BaseStatistic(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    lesson_name_id = Column(Integer, ForeignKey('lessons_names.id'))
    sentence_id = Column(Integer, ForeignKey('sentences.id'))
    shows = Column(Integer)
    right_answer = Column(Integer)
    mistake_count = Column(Integer)
    new_phrase = Column(Integer)
    full_understand = Column(Integer)
    total_time = Column(Integer)
    time_start = Column(DateTime, default=func.now())
    comment = Column(UnicodeText)


class BaseTransactionHistory(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    value = Column(Integer)
    description = Column(UnicodeText)
