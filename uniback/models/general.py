from datetime import datetime
from uniback import db
from sqlalchemy.types import JSON as JSONType


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
    
    last_attempted_run = db.Column(db.DateTime)
    last_successful_run = db.Column(db.DateTime)
    time_added = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow)
    
    db.relationship('JobHistory', backref='saved_job', lazy=True)
    db.relationship('JobParameter', backref='saved_job', lazy=True)


class JobParameter(db.Model):
    __bind_key__ = 'general'
    __tablename__ = 'job_parameter'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    param_name = db.Column(db.String(50), nullable=False)
    param_display_name = db.Column(db.String(50))
    param_value = db.Column(db.Text)

    job_id = db.Column(db.Integer, db.ForeignKey('saved_jobs.id'), nullable=False)


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

    saved_job_id = db.Column(db.Integer, db.ForeignKey('saved_jobs.id'), nullable=True)
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
    source = db.Column(db.String, nullable=True)
    last_good_backup = db.Column(db.DateTime)

    time_added = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    backup_objects = db.relationship(
        'BackupObject',
        backref='backup_set',
        lazy=True
    )


class BackupObject(db.Model):
    __bind_key__ = 'general'
    __tablename__ = 'backup_object'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    data = db.Column(db.Text)
    last_good_backup = db.Column(db.DateTime)
    time_added = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    backup_set_id = db.Column(db.Integer, db.ForeignKey('backup_set.id'))
    snapshots = db.relationship(
        'Snapshot',
        backref='backup_object',
        lazy=True)

class Snapshot(db.Model):
    __bind_key__ = 'general'
    __tablename__ = 'snapshot' 
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    data = db.Column(db.String)
    snapshot_time = db.Column(db.DateTime)
    snapshot_id = db.Column(db.String)

    backup_object_id = db.Column(db.Integer, db.ForeignKey('backup_object.id'))
