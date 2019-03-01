from datetime import datetime
from uniback import db


class SysVars(db.Model):
    __bind_key__ = 'system'
    __tablename__ = 'sys_vars'
    id = db.Column(db.Integer, primary_key=True)
    # JSON might be better but SQLite doesn't seem to support it
    var_name = db.Column(db.String(100), nullable=False)
    var_data = db.Column(db.String(100), nullable=True)


# We have a separate system variable table that exists only in
# memory for certain variable sharing between processes
class SysVarsMemory(db.Model):
    __bind_key__ = 'memory'
    __tablename__ = 'sys_vars_memory'
    id = db.Column(db.Integer, primary_key=True)
    # JSON might be better but SQLite doesn't seem to support it
    var_name = db.Column(db.String(100), nullable=False)
    var_data = db.Column(db.String(100), nullable=True)


class CredentialStore(db.Model):
    __bind_key__ = 'system'
    __tablename__ = 'credential_store'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(
        db.Integer, db.ForeignKey('credential_group.id'), nullable=False)
    credential_role = db.Column(db.String(100), nullable=False)
    credential_data = db.Column(db.String(100))


class CredentialGroup(db.Model):
    __bind_key__ = 'system'
    __tablename__ = 'credential_group'
    id = db.Column(db.Integer, primary_key=True)
    credentials = db.relationship(
        'CredentialStore', backref='credential_group', lazy='subquery')
    description = db.Column(db.String(100))
    service_name = db.Column(db.String(50), nullable=False)
    time_added = db.Column(
                        db.DateTime,
                        nullable=False,
                        default=datetime.utcnow)
