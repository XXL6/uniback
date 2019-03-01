import logging
from threading import Thread


class JobScheduler(Thread):

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("mainLogger")

    def run(self):
        pass
