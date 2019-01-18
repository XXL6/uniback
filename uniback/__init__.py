from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from uniback.config import Config
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    from uniback.main.routes import main
    app.register_blueprint(main)
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    return app
