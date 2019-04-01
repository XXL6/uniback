from uniback.tools.local_session import LocalSession
from uniback.models.general import SavedJobs


def delete_jobs(ids):
    with LocalSession() as session:
        for id in ids:
            session.query(SavedJobs).filter_by(id=id).delete()
        session.commit()


def add_job(info):
    with LocalSession() as session:
        jobs = SavedJobs(
            name=info['name'],
            engine_name=info['engine_name'],
            engine_class=info['engine_class']
        )
        session.add(jobs)
        session.commit()