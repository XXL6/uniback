from uniback.tools.local_session import LocalSession
from uniback.models.general import SavedJobs
from uniback.tools import job_tools
from uniback.misc import job_queue, credential_manager
from uniback.tools import plugin_tools

def delete_jobs(ids):
    with LocalSession() as session:
        for id in ids:
            session.query(SavedJobs).filter_by(id=id).delete()
        session.commit()


def add_job(info):
    with LocalSession() as session:
        jobs = SavedJobs(
            name=info['name'],
            notes=info.get('notes'),
            engine_name=info['engine-name'],
            engine_class=info['engine-class'],
            params=info.get('params')
        )
        session.add(jobs)
        session.commit()


def get_job_info(id):
    with LocalSession() as session:
        job = session.query(SavedJobs).filter_by(id=id).first()
        if job:
            info_dict = dict(
                name=job.name,
                notes=job.notes,
                engine_name=job.engine_name,
                engine_class=job.engine_class,
                params=job.params,
                last_attempted_run=job.last_attempted_run,
                last_successful_run=job.last_successful_run,
                time_added=job.time_added
            )
            return info_dict


def update_job_times(id, info):
    with LocalSession() as session:
        job = session.query(SavedJobs).filter_by(id=id).first()
        if info.get('last_attempted_run'):
            job.last_attempted_run = info['last_attempted_run']
        if info.get('last_successful_run'):
            job.last_successful_run = info['last_successful_run']
        session.commit()


def add_job_to_queue(id):
    with LocalSession() as session:
        job = session.query(SavedJobs).filter_by(id=id).first()
        job_class = plugin_tools.get_engine_class(job.engine_name, job.engine_class)
        process_object = job_class()
        job_object = job_tools.JobObject(name=job.name, process=process_object, engine=job.engine_name)
        job_queue.add(job=job_object)
