#development config


class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///ub_system.db'
    SQLALCHEMY_BINDS = {
        'backup':   'sqlite:///ub_backup.db'
    }
    SECRET_KEY = 'devkey'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
