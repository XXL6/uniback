from uniback.dictionary.uniback_exceptions import JobQueueFullException
from uniback.dictionary.uniback_constants import JobStatus, JobStatusMap
from threading import Lock
from collections import deque
from uniback import process_manager


class JobQueue:

    _job_list = deque()
    # we implement thread locking so that multiple threads can use
    # the queue at the same time without conflicts
    lock = Lock()

    # unlike database records, the jobs do not get an id assigned
    # automatically, so we create an internal one that will get
    # automatically incremented every time a job is added.
    # By the time it overflows, the beginning jobs will most
    # likely be done anyways
    id_counter = 0

    # we can specify the maximum amount of jobs that can be added to
    # the queue. If the jobs exceed maximum size, an exception is
    # thrown
    def __init__(self, max_size=20):
        self.max_size = max_size

    # adds a job object to the back of the queue
    def add(self, job):
        self.lock.acquire()
        if len(self._job_list) < self.max_size:
            job.id = self.id_counter
            self.id_counter += 1
            self._job_list.append(job)
        else:
            self.lock.release()
            raise JobQueueFullException("Cannot add any more jobs to queue as it is full.")
        self.lock.release()

    # removes the foremost job from the queue and returns it
    def pop(self):
        self.lock.acquire()
        if len(self._job_list) > 0:
            temp = self._job_list.popleft()
            self.lock.release()
            return temp
        else:
            self.lock.release()
            return None

    # returns the foremost object in the queue without removing it
    def peek(self):
        return_object = None
        self.lock.acquire()
        try:
            return_object = self._job_list[0]
        except IndexError:
            pass
            # do nothing as there's often going to be peeks
            # on an empty queue
        self.lock.release()
        return return_object

    # takes the next job in-queue and moves it to the back
    # of the queue in case the job cannot be run at the moment
    def delay(self):
        self.lock.acquire()
        self._job_list.rotate(-1)
        self.lock.release()

    def get_job_queue_info(self):
        return_list = []
        self.lock.acquire()
        for item in self._job_list:
            return_list.append(dict(
                id=item.id,
                name=item.name,
                status=item.status,
                progress=item.process.data.get('progress'),
                description=item.process.description
                # progress=process_manager.get_info
            ))
        self.lock.release()
        return return_list

    def get_job_info(self, id, requested_data):
        info = ''
        self.lock.acquire()
        for item in self._job_list:
            if item.id == id:
                info = getattr(item, requested_data)
                break
        self.lock.release()
        return info


class JobObject:

    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.process = kwargs['process']
        self.engine = kwargs.get('engine')
        self.id = -1
        # all new jobs will begin life as queued and will
        # change as they are run
        self.status = JobStatus.JOB_STATUS_QUEUED

        self.success_callback = None
        self.warning_callback = None
        self.error_callback = None
