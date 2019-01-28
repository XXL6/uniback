from datetime import datetime
from uniback import db


class BackupJobQueue(db.Model):
    __bind_key__ = 'backup'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    status = db.Column(db.Integer, nullable=False)
    time_started = db.Column(db.DateTime, nullable=False)
    time_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
