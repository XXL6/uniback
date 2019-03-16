from uniback.dictionary.uniback_exceptions import JobQueueFullException
from uniback.dictionary.uniback_constants import JobStatus
from threading import Lock


class JobQueue:

    # due to how lists work in python, we can pretend that it's
    # a queue with a couple of extra methods
    _job_list = []

    # we implement thread locking so that multiple threads can use
    # the queue at the same time without conflicts
    lock = Lock()

    # we can specify the maximum amount of jobs that can be added to
    # the queue. If the jobs exceed maximum size, an exception is
    # thrown
    def __init__(self, max_size=20):
        self.max_size = max_size

    # adds a job object to the back of the queue
    def add(self, job):
        self.lock.acquire()
        if len(self._job_list) < self.max_size:
            self._job_list.append(job)
        else:
            self.lock.release()
            raise JobQueueFullException("Cannot add any more jobs to queue as it is full.")
        self.lock.release()

    # removes the foremost job from the queue and returns it
    def pop(self):
        self.lock.acquire()
        if len(self._job_list) > 0:
            temp = self._job_list[0]
            del self._job_list[0]
            self.lock.release()
            return temp
        else:
            self.lock.release()
            return None

    # returns the foremost object in the queue without removing it
    def peek(self):
        self.lock.acquire()
        if len(self._job_list) > 0:
            return_object = self._job_list[0]
            self.lock.release()
            return return_object
        else:
            self.lock.release()
            return None

    # takes the next job in-queue and moves it to the back
    # of the queue in case the job cannot be run at the moment
    def delay(self):
        self.lock.acquire()
        self._job_list.append(self._job_list[0])
        del self._job_list[0]
        self.lock.release()

    def get_job_queue_info(self):
        return_list = []
        self.lock.acquire()
        for item in self._job_list:
            return_list.append(dict(
                name=item.name,
                description=item.description,
                category=item.category
            ))
        self.lock.release()
        return return_list


class JobObject:

    def __init__(self, name, process):
        self.name = name
        self.process = process
        # all new jobs will begin life as queued and will
        # change as they are run
        self.status = JobStatus.JOB_STATUS_QUEUED