from multiprocessing import Process
from uniback.tools.data_trackers import ProgressTracker, DataTracker
from time import sleep
from threading import Thread, Lock
import os


# process object with the ability to deal with subprocesses and parse
# their output as necessary
class UBProcess(Process):

    def __init__(self):
        super().__init__()
        self.name = "Generic UB Process"
        self.description = "Process without a set description."
        self.category = "undefined"
        self.can_update = True
        self.data = {}
        self.job_log = []
        self.progress_tracker = ProgressTracker()
        self.data_tracker = DataTracker()
        
        self.logging = None

    def testMethod(self):
        # self.update_thread = Thread(target=self.data_update, daemon=True)
        # self.update_thread_lock = Lock()
        pass

    def run(self):
        self.update_thread = Thread(target=self.data_update, daemon=True)
        self.update_thread_lock = Lock()
        try:
            self.update_thread.start()
        except Exception as e:
            self.log(f"update_thread exception: {e}")
        pass

    def parse_input(self, input):
        temp = os.read(input.fileno(), 128).decode('utf-8')
        # we want to only parse the multitude of regexes every once in a while
        # in case they take up a lot of cpu time, hence we have a thread
        # running in the background that lets the regex run every set amount of
        # time at the moment, but can be changed as necessary. We still want to
        # do the os.read so that the process does not halt execution
        self.update_thread_lock.acquire()
        if self.can_update:
            self.data_tracker.update(temp)
            self.progress_tracker.set_progress(temp)

            self.send_data('progress', self.progress_tracker.get_current_progress())
            temp_values = self.data_tracker.get_data_values()
            if temp_values is not None:
                for key, value in self.data_tracker.get_data_values().items:
                    self.send_data(key, value)
            self.can_update = False
        self.update_thread_lock.release()

    def assign_progress_tracker(self, regex):
        self.progress_tracker.reset_progress()
        self.progress_tracker.set_regex(regex)

    def assign_data_tracker(self, name, regex):
        self.data_tracker.insert_tracker(name, regex)

    def assign_queue(self, queue):
        self.queue = queue

    def assign_logger(self, logger):
        self.logger = logger

    def assign_data_manager(self, data_manager):
        self.data_manager = data_manager

    def send_data(self, data_name, data):
        self.queue.put(
            {'process_id': self.pid,
             'data_name': data_name,
             'data': data})

    def log(self, data):
        self.send_data('log', data)

    def status(self, data):
        self.send_data('status', data)

    def data_update(self):
        while True:
            self.update_thread_lock.acquire()
            self.can_update = True
            self.update_thread_lock.release()
            sleep(0.5)
