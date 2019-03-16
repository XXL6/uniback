import logging
from threading import Thread
from time import sleep
from uniback.dictionary.uniback_constants import JobStatus, JobStatusFinished
from uniback.models.general import JobHistory
from datetime import datetime
from uniback.tools.local_session import LocalSession


# purpose of this class is to grab job objects from the job queue
# and submit them for execution in the process manager.
# It also stores the job in the job history after completion;
class JobRunner(Thread):

    def __init__(self, queue, process_manager):
        super().__init__(daemon=True)
        self.queue = queue
        self.process_manager = process_manager
        self.logger = logging.getLogger("mainLogger")

    # at the moment only one job gets run at a time with no concurrency
    # once it finishes, the next job is run
    # does not check whether or not a job can be run at this time
    # and will attempt to do it regardless
    def run(self):
        while True:
            job = self.queue.peek()
            if job:
                if job.status == JobStatus.JOB_STATUS_QUEUED:
                    self.process_manager.add_process(job.process)
                    job.time_started = datetime.now()
                    job.status = JobStatus.JOB_STATUS_RUNNING
                elif job.status == JobStatus.JOB_STATUS_RUNNING:
                    if job.process.data.get('status') == 'success':
                        self.add_to_history(
                            name=job.name,
                            engine=1,
                            status=JobStatusFinished.JOB_STATUS_SUCCESS,
                            time_started=job.time_started,
                            time_finished=datetime.now()
                        )
                        job.status = JobStatus.JOB_STATUS_FINISHED
                    elif job.process.data.get('status') == 'error':
                        self.add_to_history(
                            name=job.name,
                            engine=1,
                            status=JobStatusFinished.JOB_STATUS_ERROR,
                            time_started=job.time_started,
                            time_finished=datetime.now()
                        )
                        job.status = JobStatus.JOB_STATUS_FINISHED
                elif job.status == JobStatus.JOB_STATUS_FINISHED:
                    self.queue.pop()
            sleep(10)

    def add_to_history(self, **kwargs):
        elapsed = kwargs.get('time_finished') - kwargs.get('time_started')
        elapsed = (datetime.min + elapsed).time()
        history = JobHistory(
            name=kwargs.get('name'),
            engine=kwargs.get('engine'),
            status=kwargs.get('status'),
            time_started=kwargs.get('time_started'),
            time_finished=kwargs.get('time_finished'),
            time_elapsed=elapsed
        )
        with LocalSession() as session:
            session.add(history)
            session.commit()
