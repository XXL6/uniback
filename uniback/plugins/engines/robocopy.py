import subprocess


class Robocopy:

    OS_SUPPORT = ["Windows"]

    def __init__(
            self,
            repository,
            backup_set,
            logging=None,
            progress_tracker=None):
        self.repository = repository
        self.backup_set = backup_set
        if logging is not None:
            self.logging_enabled = True

    def run(self):
        self.task = subprocess.Popen(
            ['robocopy', 'C:\\Users\\Arnas\\Downloads\\test',
                'C:\\Users\\Arnas\\Downloads\\test2'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        
