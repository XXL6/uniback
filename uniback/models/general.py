from datetime import datetime
from uniback import db


class SysVars(db.Model):
    __bind_key__ = 'general'
    __tablename__ = 'sys_vars'
    id = db.Column(db.Integer, primary_key=True)
    # JSON might be better but SQLite doesn't seem to support it
    var_name = db.Column(db.String(100), nullable=False)
    var_data = db.Column(db.String(100), nullable=True)


class CredentialStore(db.Model):
    __bind_key__ = 'general'
    __tablename__ = 'credential_store'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(
        db.Integer, db.ForeignKey('credential_group.id'), nullable=False)
    credential_role = db.Column(db.String(100), nullable=False)
    credential_data = db.Column(db.String(100))


class CredentialGroup(db.Model):
    __bind_key__ = 'general'
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


class SavedJobs(db.Model):
    __bind_key__ = 'general'
    __tablename__ = 'saved_jobs'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False, unique=True)
    notes = db.Column(db.Text)
    engine_name = db.Column(db.String(50), nullable=False)
    engine_class = db.Column(db.String(50), nullable=False)
    params = db.Column(db.String)
    time_added = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow)


# the job queue will no longer be a database table and will instead
# just be a data structure in-memory so that classes can be stored
# more easily. Kept here for records
class JobQueue(db.Model):
    __bind_key__ = 'general'
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
    __bind_key__ = 'general'
    __tablename__ = 'job_history'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    status = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String, nullable=False)
    log = db.Column(db.Text)
    time_started = db.Column(db.DateTime)
    time_finished = db.Column(db.DateTime)
    time_elapsed = db.Column(db.Time)
    time_added = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow)

    engine = db.Column(db.Integer, db.ForeignKey('engine.id'), nullable=False)


class Repository(db.Model):
    __bind_key__ = 'general'
    __tablename__ = 'repository'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text)
    data = db.Column(db.Text)  # not sure if data is needed
    engine = db.Column(db.String, nullable=False)
    time_added = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow)

    physical_location_id = db.Column(
        db.Integer, db.ForeignKey('physical_location.id'), nullable=False)


class Engine(db.Model):
    __bind_key__ = 'general'
    __tablename__ = 'engine'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(50), nullable=False, unique=True)
    time_added = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow)


class PhysicalLocation(db.Model):
    __bind_key__ = 'general'
    __tablename__ = 'physical_location'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(50), nullable=False, unique=True)
    address = db.Column(db.Text)
    type = db.Column(db.Integer, db.ForeignKey('physical_location_type.id'), nullable=False)
    concurrent_jobs = db.Column(db.Integer, default=1)
    time_added = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow)

    repositories = db.relationship(
            'Repository',
            backref='physical_location',
            lazy=True)


class PhysicalLocationType(db.Model):
    __bind_key__ = 'general'
    __tablename__ = 'physical_location_type'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(50), nullable=False, unique=True)
    subtype = db.Column(db.String(15), nullable=False)  # cloud, local, offsite
    description = db.Column(db.Text)

    physical_locations = db.relationship(
        'PhysicalLocation',
        backref='physical_location_type',
        lazy=True
    )


class BackupSet(db.Model):
    __bind_key__ = 'general'
    __tablename__ = 'backup_set'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(50), nullable=False, unique=True)
    type = db.Column(db.Integer, nullable=False)
    data = db.Column(db.Text)
    time_added = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow)