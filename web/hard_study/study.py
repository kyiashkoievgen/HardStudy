from datetime import datetime

from sqlalchemy import func, literal_column
from unidecode import unidecode
import os
import random

from .modls import StudyProgress, Sentence, RegSentWord, Word, Statistic
from .. import db


class Phrase:
    id_phrase = int()
    phrase_study = str()
    phrase_for_checking = str()
    phrase_study_audio = str()
    phrase_native = str()
    phrase_native_audio = str()
    was_help_flag = bool()
    was_help_sound_flag = bool()
    was_mistake_flag = bool()
    num_showings = int()
    study_type = int()
    img = str()


class StudyPhrases:
    def __init__(self, current_user):
        self.current_user = current_user
        self.phrases = []

    # (1059, 4762, 1059, 3, 527, 'La selva densa esconde',
    # '6eda7e38c40980ff01907c77db977d006cad8406aeb716638516e36c2c3c39da', True, False, 'Густой лес скрывает',
    # '415d735fc4fe4820f7d59e3df7ce40e344a9cfc680796790b1eefd364df21486', 4762, 'selva', 259, 1, 1, 1059, 1, 0, 0,
    # datetime.datetime(2023, 11, 10, 20, 4, 8), 3, Decimal('0'), datetime.datetime(2023, 11, 10, 20, 4, 8),
    # Decimal('0.0000'))
    def add_phrase(self, sent_list, study_type):
        for sent in sent_list:
            phrase = Phrase()
            phrase.id_phrase = sent[0]
            phrase.phrase_study = sent[5].lower()
            if self.current_user.use_dialect:
                phrase.phrase_for_checking = phrase.phrase_study
            else:
                phrase.phrase_for_checking = unidecode(phrase.phrase_study)
            phrase.phrase_study_audio = sent[6]
            phrase.phrase_native = sent[9].lower()
            phrase.phrase_native_audio = sent[10]
            phrase.study_type = study_type
            phrase.num_showings = 100
            images = os.listdir('web/static/img/hs/back_ground')
            phrase.img = random.choice(images)
            if study_type == 1 or study_type == 5:
                phrase.num_showings = self.current_user.num_showings1
            if study_type == 4:
                phrase.num_showings = 1
            if study_type == 2:
                phrase.num_showings = self.current_user.num_showings2
            elif study_type == 3:
                phrase.num_showings = self.current_user.num_showings3
            self.phrases.append(phrase)

    def take_lesson_content(self):
        subquery_StudyProgress = db.session.query(StudyProgress). \
            filter_by(user_id=self.current_user.id, lesson_name_id=self.current_user.cur_lesson_id).subquery()
        subquery_Sentence_translation = db.session.query(Sentence).filter_by(
            language_id=self.current_user.lang2).subquery()
        subquery_Sentence_native = db.session.query(Sentence.meaning_id, Sentence.text).filter_by(
            language_id=self.current_user.lang1).subquery()
        lesson_content_without_native = db.session.query(subquery_Sentence_translation, subquery_StudyProgress) \
            .select_from(subquery_Sentence_translation). \
            outerjoin(subquery_StudyProgress,
                      subquery_Sentence_translation.c.id == subquery_StudyProgress.c.sentence_id) \
            .subquery()
        lesson_content = db.session.query(lesson_content_without_native, subquery_Sentence_native). \
            outerjoin(subquery_Sentence_native,
                      subquery_Sentence_native.c.meaning_id == lesson_content_without_native.c.meaning_id). \
            order_by(lesson_content_without_native.c.right_count.desc()).all()
        return lesson_content

    def prepare_study_data(self):
        # получаем предложения которые в изучении у текущего пользователя
        subquery_StudyProgress = db.session.query(StudyProgress). \
            filter_by(user_id=self.current_user.id, lesson_name_id=self.current_user.cur_lesson_id).subquery()
        # получаем все предложения на изучаемом языке
        subquery_Sentence_translation = db.session.query(Sentence).filter_by(
            language_id=self.current_user.lang2).subquery()
        # получаем все предложения текущего пользователя на родном языке
        subquery_Sentence_native = db.session.query(Sentence.meaning_id, Sentence.text, Sentence.text_hash).filter_by(
            language_id=self.current_user.lang1).subquery()
        subquery_Sentence_translation = db.session.query(subquery_Sentence_translation, subquery_Sentence_native.c.text,
                                                         subquery_Sentence_native.c.text_hash) \
            .join(subquery_Sentence_native, subquery_Sentence_native.c.meaning_id == subquery_Sentence_translation.c.
                  meaning_id).subquery()
        # добавляем слова в предложения
        subquery_word_sent = db.session.query(RegSentWord, subquery_Sentence_translation) \
            .join(subquery_Sentence_translation,
                  RegSentWord.sentences_id == subquery_Sentence_translation.c.id).subquery()
        subquery_word_sent = db.session.query(subquery_word_sent, Word). \
            join(Word, subquery_word_sent.c.word_id == Word.id).subquery()
        # добавляем информацию о процессе обучения
        subquery_word_sent = db.session.query(subquery_word_sent, subquery_StudyProgress). \
            outerjoin(subquery_StudyProgress,
                      subquery_StudyProgress.c.sentence_id == subquery_word_sent.c.sentences_id).subquery()
        # подсчитываем количество слов в предложении и количество правильно отвеченных слов
        subquery_num_word_sent = db.session.query(subquery_word_sent, func.count(subquery_word_sent.c.word_id).
                                                  label('num_word')). \
            group_by(subquery_word_sent.c.sentences_id).subquery()
        subquery_right_word_sent = db.session.query(subquery_word_sent, func.sum(subquery_word_sent.c.right_count).
                                                    label('right_count_word'),
                                                    (func.max(subquery_word_sent.c.last_show_time))
                                                    .label('time_max')). \
            group_by(subquery_word_sent.c.word_id).subquery()
        subquery_word_sent = db.session.query(subquery_word_sent, subquery_num_word_sent.c.num_word). \
            join(subquery_num_word_sent, subquery_word_sent.c.sentences_id == subquery_num_word_sent.c.sentences_id). \
            subquery()
        subquery_word_sent = db.session.query(subquery_word_sent, subquery_right_word_sent.c.right_count_word,
                                              # text("(func.now() - subquery_right_word_sent.c.time_max) as date_diff"),
                                              subquery_right_word_sent.c.time_max). \
            join(subquery_right_word_sent, subquery_word_sent.c.word_id == subquery_right_word_sent.c.word_id). \
            subquery()
        subquery_word_sent = db.session.query(subquery_word_sent,
                                              literal_column("(right_count_word/TIMESTAMPDIFF(HOUR, time_max, NOW()))").
                                              label('forgetting')).subquery()
        # находим слова на которые было отвечено правильно
        word_right = set([word.word_id for word in
                          db.session.query(subquery_word_sent).filter(subquery_word_sent.c.right_count > 0)
                         .all()])
        # находим слова которые нужно учить
        all_word = set([word.id for word in db.session.query(Word).all()])
        word_to_study = all_word - word_right
        # предложения для разминки
        add_sent = db.session.query(subquery_word_sent).filter(subquery_word_sent.c.right_count != None) \
            .order_by(subquery_word_sent.c.right_count.desc()).group_by('id').limit(
            self.current_user.num_sent_warm_up).subquery()
        # если количество предложений меньше минимального количества предложений в разминке
        add_sent_num = self.current_user.num_sent_warm_up - db.session.query(add_sent).count()
        if add_sent_num > 0:
            add_sent2 = db.session.query(subquery_word_sent).order_by('num_word').group_by('id'). \
                limit(add_sent_num)
            add_sent = db.session.query(add_sent).union(add_sent2).subquery()
        self.add_phrase(db.session.query(add_sent).all(), 0)
        # находим предложения которые не были отвечены правильно и добавляем их в обучение
        add_sent = db.session.query(subquery_word_sent).filter_by(right_count=0).group_by('id'). \
            limit(self.current_user.num_new_sentences_lesson).all()
        # если количество предложений меньше минимального количества новые предложений в уроке добавляем новые приложения
        add_sent_num = self.current_user.num_new_sentences_lesson - len(add_sent)
        add_sent2 = []
        add_sent3 = []
        if add_sent_num > 0:
            # предложения которые не были в обучении
            subquery_Sentence_not_in_progress = db.session.query(subquery_word_sent). \
                filter_by(right_count=None).subquery()
            # предложения которые имеют слова на которые было отвечено правильно
            add_sent2 = db.session.query(subquery_Sentence_not_in_progress). \
                filter(subquery_Sentence_not_in_progress.c.right_count_word > 0).subquery()
            # предложения которые имеют слова которые нужно учить
            add_sent_nr = db.session.query(subquery_Sentence_not_in_progress). \
                filter(subquery_Sentence_not_in_progress.c.word_id.in_(word_to_study)).all()
            # предложения в которых содержат слова которые уже изучены и те что нужно учить
            add_sent2 = db.session.query(add_sent2).filter(
                add_sent2.c.id.in_(sent.id for sent in add_sent_nr)).group_by('id').order_by('num_word'). \
                limit(add_sent_num).all()

            add_sent_num = self.current_user.num_new_sentences_lesson - len(add_sent) - len(add_sent2)
            if add_sent_num > 0:
                add_sent3 = db.session.query(subquery_Sentence_not_in_progress). \
                    filter(subquery_Sentence_not_in_progress.c.word_id.in_(word_to_study)).group_by('id'). \
                    order_by('num_word').limit(add_sent_num).all()

        self.add_phrase(add_sent, 1)
        self.add_phrase(add_sent2, 5)
        self.add_phrase(add_sent3, 5)
        self.add_phrase(add_sent, 4)
        self.add_phrase(add_sent2, 4)
        self.add_phrase(add_sent3, 4)

        add_sent4 = db.session.query(subquery_word_sent). \
            filter(subquery_word_sent.c.right_count > 0, subquery_word_sent.c.right_count <= 3).order_by('forgetting'). \
            group_by('id').limit(self.current_user.num_new_sentences_lesson*2).all()
        # add_sent = db.session.query(add_sent).union(add_sent2).subquery()

        self.add_phrase(add_sent4, 2)

        add_sent4 = db.session.query(subquery_word_sent). \
            filter(subquery_word_sent.c.right_count > 3).order_by('forgetting'). \
            group_by('id').limit(self.current_user.num_new_sentences_lesson*2).all()
        # add_sent = db.session.query(add_sent).union(add_sent2).all()

        self.add_phrase(add_sent4, 3)
        self.add_phrase(add_sent, 4)
        self.add_phrase(add_sent2, 4)
        self.add_phrase(add_sent3, 4)

        self.current_user.adjust_motivator(len(self.phrases))


def save_study_progress(current_user, id_phrase, was_mistake_flag, was_help_sound_flag, was_help_flag):
    study_progress = db.session.query(StudyProgress). \
        filter_by(user_id=current_user.id, lesson_name_id=current_user.cur_lesson_id,
                  sentence_id=id_phrase).first()
    show_count = 1
    right_count = 0
    remember = 0
    if (was_help_flag == 'false') and (was_help_sound_flag == 'false'):
        remember = 1
    if (was_mistake_flag == 'false') and (was_help_flag == 'false'):
        right_count = 1
    if (was_mistake_flag == 'true') and ((was_help_sound_flag == 'true') or (was_help_flag == 'true')):
        right_count = -1
    if not (study_progress is None):
        show_count += study_progress.show_count
        right_count += study_progress.right_count
        if right_count < 0:
            right_count = 0
        remember += study_progress.remember
        db.session.query(StudyProgress).filter_by(user_id=current_user.id,
                                                  lesson_name_id=current_user.cur_lesson_id,
                                                  sentence_id=id_phrase).update(
            {StudyProgress.show_count: show_count, StudyProgress.right_count: right_count,
             StudyProgress.remember: remember, StudyProgress.last_show_time: datetime.now()})
    else:
        study_progress = StudyProgress(user_id=current_user.id, lesson_name_id=current_user.cur_lesson_id,
                                       sentence_id=id_phrase, show_count=show_count, right_count=right_count,
                                       remember=remember, last_show_time=datetime.now())
        db.session.add(study_progress)
    db.session.commit()


def save_statistic(current_user, id_phrase, time_start, new_phrase, right_answer, full_understand, mistake_count, shows,
                   total_time):
    statistic = Statistic(user_id=current_user.id, lesson_name_id=current_user.cur_lesson_id, sentence_id=id_phrase,
                          time_start=time_start, new_phrase=new_phrase, right_answer=right_answer,
                          total_time=total_time,
                          full_understand=full_understand, mistake_count=mistake_count, shows=shows)
    db.session.add(statistic)
    db.session.commit()


def get_lesson_result(current_user):
    stat = db.session.query(Statistic, func.sum(Statistic.shows), func.sum(Statistic.right_answer),
                            func.sum(Statistic.full_understand), func.sum(Statistic.new_phrase),
                            func.sum(Statistic.mistake_count), func.sum(Statistic.total_time)) \
        .filter_by(user_id=current_user.id, lesson_name_id=current_user.cur_lesson_id).group_by('time_start'). \
        order_by(Statistic.time_start.desc()).first()
    result = {
        'shows': stat[1],
        'right_answer': stat[2],
        'full_understand': stat[3],
        'new_phrase': stat[4],
        'mistake': stat[5],
        'total_time': stat[6]
    }
    return result
