from datetime import datetime
from uniback import db


class SavedJobs(db.Model):
    __bind_key__ = 'backup'
    __tablename__ = 'saved_jobs'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False, unique=True)
    engine = db.Column(db.Integer, db.ForeignKey('engine.id'), nullable=False)
    time_added = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow)


class BackupJobQueue(db.Model):
    __bind_key__ = 'backup'
    __tablename__ = 'backup_job_queue'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False, unique=True)
    engine = db.Column(db.Integer, db.ForeignKey('engine.id'), nullable=False)
    status = db.Column(db.Integer, nullable=False)
    time_started = db.Column(db.DateTime, nullable=False)
    time_added = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow)


class Repository(db.Model):
    __bind_key__ = 'backup'
    __tablename__ = 'repository'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(50), nullable=False, unique=True)
    engine = db.Column(db.Integer, db.ForeignKey('engine.id'), nullable=False)
    time_added = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow)


class Engine(db.Model):
    __bind_key__ = 'backup'
    __tablename__ = 'engine'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(50), nullable=False, unique=True)
    time_added = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow)


class PhysicalLocation(db.Model):
    __bind_key__ = 'backup'
    __tablename__ = 'physical_location'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(50), nullable=False, unique=True)
    repositories = db.relationship(
        'Repository',
        backref='PhysicalLocation',
        lazy=True)
    time_added = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow)
