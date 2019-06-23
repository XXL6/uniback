import subprocess
from uniback.dictionary.uniback_constants import BackupSetTypes
from uniback.dictionary.uniback_exceptions import BSNotSupportedException
from uniback.tools.ub_engine_processes import UBBackup, UBProcess, UBRestore
import os
from time import sleep
import traceback

OS_SUPPORT = ["Windows"]
RESUMABLE = False
ENGINE_NAME = 'testengine'
AVAILABLE_JOBS = ["Backup", "Restore", "Repository"]


class Backup(UBBackup):

    def __init__(
            self,
            param_list=None,
            progress_tracker=None):
        super().__init__()
        if param_list:
            self.repository = param_list.get('repository')
            self.backup_set = param_list.get('backup_set')
        self.repository = None
        self.backup_set = None
        self.param_list = param_list

        if self.logging is not None:
            self.logging_enabled = True
        else:
            self.logging_enabled = False
        self.assign_progress_tracker('(?<=\r ).*(?=%)')
        # self.assign_progress_tracker('.*(?=%)')
        #try:
        #    self.parse_backup_set()
        #except BSNotSupportedException as e:
        #    if self.logging is not None:
        #        self.logging.error(f"{e}")

    def run(self):
        super().run()
        self.status('running')
        command = self.generate_run_command()
        self.log(f'Generated run command: {command}')
        self.start_subprocess(command)
        self.log(f'Errors: {self.task.stderr}')
        sleep(10)
        self.status('success')

    def generate_run_command(self):
        run_command = []
        run_command.append('robocopy')
        # backup_from = self.parse_backup_set()
        # backup_to = ""
        # run_command.append('\"Y:\\Working Folder\\UBTests\\Sauce\"')
        # run_command.append('\"Y:\\Working Folder\\UBTests\\Destination\"')
        backup_source = self.backup_set['root']
        run_command.append(backup_source)
        run_command.append(self.repository)
        run_command.append(self.parse_backup_set())
        # run_command.append('\"C:\\Users\\Arnas\\Downloads\\UBTest\\Sauce\"')
        # run_command.append('\"C:\\Users\\Arnas\\Downloads\\UBTest\\Destination\"')

        run_command.append('/E')
        run_command = ' '.join(run_command)
        return run_command

    def parse_backup_set(self):
        if self.backup_set.type is BackupSetTypes.BS_TYPE_FOLDERS:
            return self.parse_folders_bs()
        elif self.backup_set.type is BackupSetTypes.BS_TYPE_FILESFOLDERS:
            return self.parse_file_folders_bs()
        else:
            pass  # pass during development
            # raise BSNotSupportedException("Backup set of type "
            #                              f"{self.backup_set.type} "
            #                              "is not supported.")

    def parse_folders_bs(self):
        parameter = ""
        num_folders = self.backup_set['num_folders']
        root = self.backup_set['root']
        for folder in self.backup_set['folders']:
            parameter += os.path.join(root, folder)
        return parameter

    def parse_file_folders_bs(self):
        parameter = ''
        num_items = self.backup_set.get('num_items')
        root = self.backup_set['root']
        for item in self.backup_set['items']:
            parameter += (item + ' ')
        

    @staticmethod
    def fields_request():
        field_list = []
        # field_list.append(dict(name="testfield", label="Test Lol", type="string", required=True))
        # field_list.append(dict(name="credentialTest", label="Credential Test", type="credential", required=True))
        return field_list



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
        field_list.append(dict(name="name", label="Repository name", type="string", required=True))
        return field_list

    # field_list[{'name': name, 'data': data}]
    def run(self):
        self.log("Repository creation began.")
        self.status('running')
        try:
            self.log(f"Attempting to create a directory {self.field_dict['name']}.")
            os.mkdir(os.path.join(self.address, self.field_dict['name']))
            self.status('success')
        except IOError as e:
            self.logger.error(f"Failed to create directory: {e}")
            self.log(f"Failed to create directory: {e}")
            self.status('error')
        self.log("Finished testengine Repository process.")
        sleep(30)
        
