from multiprocessing import Process


# just adds some extra functions for assigning the logger and
# some communication objects if necessary
class UBProcess(Process):

    description = "Process without a set description."
    ub_name = "Generic UB Process"
    ub_category = "undefined"
    data = {}

    def assign_queue(self, queue):
        self.queue = queue

    def assign_logger(self, logger):
        self.logger = logger

    def assign_data_manager(self, data_manager):
        self.data_manager = data_manager
