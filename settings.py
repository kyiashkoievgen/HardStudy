from db import DB


class Settings:
    def __init__(self):
        self.apostrophe = None
        self.right_answer_2 = None
        self.right_answer_1 = None
        self.punish_time_1 = None
        self.show_time_sent = None
        self.sent_in_less = None
        self.time_beetween_study_6 = None
        self.time_beetween_study_5 = None
        self.time_beetween_study_4 = None
        self.time_beetween_study_3 = None
        self.time_beetween_study_2 = None
        self.time_beetween_study_1 = None
        self.lesson_per_day = None
        self.profile_name = None
        self.comport = None
        self.name = None
        self.db = DB()
        self.get_settings()

    def get_settings(self):
        raw_setting = self.db.app_setting_init()
        self.name = raw_setting['name']
        self.comport = raw_setting['comport']
        self.profile_name = raw_setting['profile_name']
        self.lesson_per_day = raw_setting['lesson_per_day']
        self.time_beetween_study_1 = raw_setting['time_beetween_study_1']
        self.time_beetween_study_2 = raw_setting['time_beetween_study_2']
        self.time_beetween_study_3 = raw_setting['time_beetween_study_3']
        self.time_beetween_study_4 = raw_setting['time_beetween_study_4']
        self.time_beetween_study_5 = raw_setting['time_beetween_study_5']
        self.time_beetween_study_6 = raw_setting['time_beetween_study_6']
        self.sent_in_less = raw_setting['sent_in_less']
        self.show_time_sent = raw_setting['show_time_sent']
        self.punish_time_1 = raw_setting['punish_time_1']
        self.right_answer_1 = raw_setting['right_answer_1']
        self.right_answer_2 = raw_setting['right_answer_2']
        self.apostrophe = raw_setting['apostrophe']
