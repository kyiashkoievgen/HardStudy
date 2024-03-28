from flask import Flask, current_app, session
from flask_babel import Babel
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from config import config
from flask import request

db = SQLAlchemy()
bootstrap = Bootstrap()
login_manager = LoginManager()
login_manager.session_protection = 'basic'
login_manager.login_view = 'auth.login'
babel = Babel()
mail = Mail()


def create_app(config_name):
    app = Flask(__name__)
    conf = config[config_name]
    app.config.from_object(conf)
    config[config_name].init_app()
    db.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    from web.hard_study.auth import auth
    from web.hard_study import hs
    app.register_blueprint(hs)
    app.register_blueprint(auth, url_prefix='/auth')

    def get_locale():
        lang = session.get('language')
        if not lang:
            lang = request.accept_languages.best_match(current_app.config['LANGUAGES'])
        if current_user.is_authenticated:
            return current_user.lang1_code.code
        # otherwise try to guess the language from the user accept
        # header the browser transmits.  We support de/fr/en in this
        # example.  The best match wins.
        return lang

    babel.init_app(app, locale_selector=get_locale)
    return app
