import os
from dotenv import load_dotenv

base_dir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()


class Config:
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SECRET_KEY = os.getenv('SECRET_KEY')
    WTF_CSRF_TIME_LIMIT = 43200
    # BOOTSTRAP_SERVE_LOCAL = True
    LANGUAGES = ['ru', 'pt', 'es', 'en']
    MAIL_SUBJECT_PREFIX = 'Study Forge '
    MAIL_SENDER = os.getenv('MAIL_USERNAME')

    @staticmethod
    def init_app():
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')


config = {
    'development': DevelopmentConfig,

    'default': DevelopmentConfig
}
