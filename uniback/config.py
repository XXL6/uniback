#development config


class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///system.db'
    SECRET_KEY = 'devkey'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
