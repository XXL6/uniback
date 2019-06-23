import subprocess
from uniback.dictionary.uniback_constants import BackupSetTypes
from uniback.dictionary.uniback_exceptions import BSNotSupportedException
from uniback.tools.ub_engine_processes import UBBackup, UBProcess, UBRestore
import os
from time import sleep

OS_SUPPORT = ["Windows"]
RESUMABLE = False
AVAILABLE_JOBS = ["DummyJob1", "DummyJob2", "DummyJob3"]

class Backup(UBBackup):

    def __init__(
            self,
            param_list=None,
            progress_tracker=None):
        super().__init__()
        self.repository = param_list['repository']
        self.backup_set = param_list['backup_set']
        self.param_list = param_list

        if self.logging is not None:
            self.logging_enabled = True
        else:
            self.logging_enabled = False
        try:
            self.parse_backup_set()
        except BSNotSupportedException as e:
            if self.logging is not None:
                self.logging.error(f"{e}")

    def run(self):
        command = self.generate_run_command()
        self.task = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        stdout, stderr = self.task.communicate()

    def generate_run_command(self):
        run_command = []
        run_command.append('robocopy')
        
        backup_from = self.parse_backup_set()
        backup_to = ""

    def parse_backup_set(self):
        if self.backup_set.type is BackupSetTypes.BS_TYPE_FOLDERS:
            return self.parse_folders_bs()
        else:
            raise BSNotSupportedException("Backup set of type "
                                          f"{self.backup_set.type} "
                                          "is not supported.")

    def parse_folders_bs(self):
        parameter = ""
        num_folders = self.backup_set['num_folders']
        root = self.backup_set['root']
        for folder in self.backup_set['folders']:
            parameter += os.path.join(root, folder)
        return parameter


class Restore(UBRestore):

    def __init__(
            self,
            repository,
            restore_location,
            logging=None,
            progress_tracker=None):
        super().__init__()
        self.repository = repository
        self.restore_location = restore_location
        if logging is not None:
            self.logging_enabled = True
        else:
            self.logging_enabled = False

    @staticmethod
    def fields_request():
        pass


class Repository(UBProcess):

    def __init__(self, address, field_dict=None):
        super().__init__()
        self.address = address
        self.field_dict = field_dict

    @staticmethod
    def fields_request():
        field_list = []
        field_list.append(dict(name="name", label="Repository name", type="string"))
        return field_list

    # field_list[{'name': name, 'data': data}]
    def run(self):
        self.send_data('status', 'running')
        try:
            os.mkdir(os.path.join(self.address, self.field_dict['name']))
            self.send_data('status', 'success')
        except IOError as e:
            self.logger.error(f"Failed to create directory: {e}")
            self.send_data('status', 'error')
        
