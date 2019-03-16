from uniback.tools.local_session import LocalSession
# from uniback.models.ub_general import JobQueue
from uniback.dictionary.uniback_constants import JobStatus


class JobQueue:

    job_list = {}

    def insert_job(name, params):
        # we initialize jobs with the status of queued and it
        # will change once the job gets picked up by the job
        # runner
        job_queue = JobQueue(
            name=name,
            params=params,
            status=JobStatus.JOB_STATUS_QUEUED)