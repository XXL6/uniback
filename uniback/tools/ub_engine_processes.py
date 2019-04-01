from uniback.tools.data_trackers import ProgressTracker, DataTracker
from uniback.tools.ub_process import UBProcess


class UBBackup(UBProcess):

    def __init__(self):
        super().__init__()
        # self.progress_tracker = ProgressTracker()
        # self.data_tracker = DataTracker()
    
    def parse_backup_set(self):
        pass

    def generate_run_command(self):
        pass


class UBRestore(UBProcess):

    def __init__(self):
        super().__init__()
        self.progress_tracker = ProgressTracker()
        self.data_tracker = DataTracker()

    def generate_run_command(self):
        pass
