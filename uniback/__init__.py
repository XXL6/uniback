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
    from uniback.users.routes import users
    from uniback.backup.routes import backup
    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(backup)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    bcrypt.init_app(app)
    login_manager.init_app(app)

    return app
