from flask import Flask
from uniback.config import Config
from uniback import db, login_manager, bcrypt, logger
from uniback.process_init import init_sys_processes
from uniback.misc import credential_manager
from uniback.init_db import init_db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    with app.app_context():
        db.create_all()
        init_db()
    credential_manager.assign_session(db.session)
    from uniback.blueprints.main.routes import main
    from uniback.blueprints.jobs.routes import jobs
    from uniback.blueprints.users.routes import users
    from uniback.blueprints.backup.routes import backup
    from uniback.blueprints.restore.routes import restore
    from uniback.blueprints.settings.routes import settings
    from uniback.blueprints.repositories.routes import repositories
    app.register_blueprint(main)
    app.register_blueprint(jobs)
    app.register_blueprint(users)
    app.register_blueprint(backup)
    app.register_blueprint(restore)
    app.register_blueprint(settings)
    app.register_blueprint(repositories)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    init_sys_processes()
    logger.info('App created')
    return app
