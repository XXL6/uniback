from datetime import datetime
from uniback import db


class SavedJobs(db.Model):
    __bind_key__ = 'backup'
    __tablename__ = 'saved_jobs'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False, unique=True)
    notes = db.Column(db.Text)
    params = db.Column(db.String)
    time_added = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow)

    engine = db.Column(db.Integer, db.ForeignKey('engine.id'), nullable=False)


class JobQueue(db.Model):
    __bind_key__ = 'backup'
    __tablename__ = 'job_queue'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False, unique=True)
    status = db.Column(db.Integer, nullable=False)
    params = db.Column(db.String)
    time_started = db.Column(db.DateTime)
    time_finished = db.Column(db.DateTime)
    time_added = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow)

    engine = db.Column(db.Integer, db.ForeignKey('engine.id'), nullable=False)


class JobHistory(db.Model):
    __bind_key__ = 'backup'
    __tablename__ = 'job_history'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    engine = db.Column(db.Integer, db.ForeignKey('engine.id'), nullable=False)
    status = db.Column(db.Integer, nullable=False)
    time_started = db.Column(db.DateTime)
    time_finished = db.Column(db.DateTime)
    time_elapsed = db.Column(db.Time)
    time_added = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow)


class Repository(db.Model):
    __bind_key__ = 'backup'
    __tablename__ = 'repository'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(50), nullable=False, unique=True)
    time_added = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow)

    engine_id = db.Column(
        db.Integer, db.ForeignKey('engine.id'), nullable=False)
    physical_location_id = db.Column(
        db.Integer, db.ForeignKey('physical_location.id'), nullable=False)


class Engine(db.Model):
    __bind_key__ = 'backup'
    __tablename__ = 'engine'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(50), nullable=False, unique=True)
    time_added = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow)

    repositories = db.relationship(
        'Repository',
        backref='engine'
    )


class PhysicalLocation(db.Model):
    __bind_key__ = 'backup'
    __tablename__ = 'physical_location'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(50), nullable=False, unique=True)
    concurrent_jobs = db.Column(db.Integer, default=1)
    time_added = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow)

    repositories = db.relationship(
            'Repository',
            backref='physical_location',
            lazy=True)


class BackupSet(db.Model):
    __bind_key__ = 'backup'
    __tablename__ = 'backup_set'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(50), nullable=False, unique=True)
    type = db.Column(db.Integer, nullable=False)
    data = db.Column(db.Text, nullable=False)
    time_added = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow)
