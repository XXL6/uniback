# development config


class Config:
    SQLALCHEMY_BINDS = {
        'system':   'sqlite:///ub_system.db',
        'backup':   'sqlite:///ub_backup.db'
    }
    SECRET_KEY = 'devkey'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
