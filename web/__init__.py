from flask import Flask
from flask_babel import Babel
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from config import config

db = SQLAlchemy()
bootstrap = Bootstrap()
login_manager = LoginManager()
login_manager.session_protection = 'basic'
login_manager.login_view = 'auth.login'
babel = Babel()


def create_app(config_name):
    app = Flask(__name__)
    conf = config[config_name]
    app.config.from_object(conf)
    config[config_name].init_app()
    db.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    babel.init_app(app)
    from web.hard_study.auth import auth
    from web.hard_study import hs
    app.register_blueprint(hs)
    app.register_blueprint(auth, url_prefix='/auth')
    return app
