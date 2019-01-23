from flask import Flask, url_for
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
    from uniback.users.routes import users
    from uniback.backup.routes import backup
    from uniback.restore.routes import restore
    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(backup)
    app.register_blueprint(restore)
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    with app.app_context():
        db.create_all()
    login_manager.login_view = "users.login"

    return app
