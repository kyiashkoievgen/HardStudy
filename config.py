import os

base_dir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SECRET_KEY = 'SDKFGKJHSJKFlkdfjlksblkgf'
    BOOTSTRAP_SERVE_LOCAL = True
    LANGUAGES = ['ru', 'pt', 'es', 'en']

    @staticmethod
    def init_app():
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://ewgen:Zaqplm!234@localhost/hard_study'


config = {
    'development': DevelopmentConfig,

    'default': DevelopmentConfig
}
