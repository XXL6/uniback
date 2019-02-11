import subprocess
from uniback.dictionary.uniback_constants import BackupSetTypes
from uniback.dictionary.uniback_exceptions import BSNotSupportedException
import os

OS_SUPPORT = ["Windows"]
RESUMABLE = False


class RobocopyBackup:

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
        else:
            self.logging_enabled = False
        try:
            self.parse_backup_set()
        except BSNotSupportedException as e:
            if logging is not None:
                logging.error(f"BackupSet of {}")

    def run(self):
        self.task = subprocess.Popen(
            ['robocopy', 'C:\\Users\\Arnas\\Downloads\\test',
                'C:\\Users\\Arnas\\Downloads\\test2'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)

    def parse_backup_set(self):
        if backup_set.type is BackupSetTypes.BS_TYPE_FILESFOLDERS:
            pass
        else:
            raise BSNotSupportedException

    def get_process_id():
        return os.getpid()


class RobocopyRestore:

    def __init__(
            self,
            repository,
            restore_location,
            logging=None,
            progress_tracker=None):

        self.repository = repository
        self.restore_location = restore_location
        if logging is not None:
            self.logging_enabled = True
        else:
            self.logging_enabled = False
