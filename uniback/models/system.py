from datetime import datetime
from uniback import db


class SysVars(db.Model):
    __bind_key__ = 'system'
    id = db.Column(db.Integer, primary_key=True)
    # JSON might be better but SQLite doesn't seem to support it
    var_name = db.Column(db.String(100), nullable=False)
    var_data = db.Column(db.String(100), nullable=True)


class UserFacingLog(db.Model):
    __bind_key__ = 'system'
    id = db.Column(db.Integer, primary_key=True)
    log_level = db.Column(db.Integer, nullable=False)
    message = db.Column(db.String, nullable=True)


class CredentialStore(db.Model):
    __bind_key__ = 'system'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(
        db.Integer, db.ForeignKey('CredentialGroup.id'), nullable=False)
    service_name = db.Column(db.String, nullable=False)
    credential_role = db.Column(db.String(100), nullable=False)
    credential_data = db.Column(db.String(100))
    time_added = db.Column(
                        db.DateTime,
                        nullable=False,
                        default=datetime.utcnow)


class CredentialGroup(db.Model):
    __bind_key__ = 'system'
    id = db.Column(db.Integer, primary_key=True)
    credentials = db.Relationship(
        'CredentialStore', backref='credential_group', lazy=True)
    description = db.Column(db.String(100))
