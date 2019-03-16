from multiprocessing import Process


# just adds some extra functions for assigning the logger and
# some communication objects if necessary
class UBProcess(Process):

    name = "Generic UB Process"
    description = "Process without a set description."
    category = "undefined"
    data = {}

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
