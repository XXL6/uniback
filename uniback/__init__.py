from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from uniback.config import Config
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    from uniback.blueprints.main.routes import main
    from uniback.blueprints.users.routes import users
    from uniback.blueprints.backup.routes import backup
    from uniback.blueprints.restore.routes import restore
    from uniback.blueprints.settings.routes import settings
    from uniback.blueprints.repositories.routes import repositories
    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(backup)
    app.register_blueprint(restore)
    app.register_blueprint(settings)
    app.register_blueprint(repositories)
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    with app.app_context():
        db.create_all()

    return app
