from uniback.tools.job_scheduler import JobScheduler
from uniback.tools.process_manager import ProcessManager
import logging
from multiprocessing import Process

logger = logging.getLogger("debugLogger")


# def benis():
manager = ProcessManager()
for i in range(10):
    scheduler = JobScheduler()
    manager.add_process(scheduler)
