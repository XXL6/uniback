import logging
from threading import Thread


class JobScheduler(Thread):

    def __init__(self, queue):
        super().__init__()
        self.queue = queue
        self.logger = logging.getLogger("mainLogger")

    def run(self):
        pass
