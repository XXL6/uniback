class JobStatus:
    JOB_STATUS_RUNNING = 10
    JOB_STATUS_QUEUED = 20
    JOB_STATUS_PAUSED = 30
    JOB_STATUS_FINISHED = 40


class JobStatusMap:
    JOB_STATUS = {
        JobStatus.JOB_STATUS_RUNNING: 'Running',
        JobStatus.JOB_STATUS_QUEUED: 'Queued',
        JobStatus.JOB_STATUS_PAUSED: 'Paused',
        JobStatus.JOB_STATUS_FINISHED: 'Finished'
    }


class JobStatusFinished:
    JOB_STATUS_SUCCESS = 10
    JOB_STATUS_WARNING = 20
    JOB_STATUS_ERROR = 30


class JobStatusFinishedMap:
    JOB_STATUS_FINISHED = {
        JobStatusFinished.JOB_STATUS_SUCCESS: 'Success',
        JobStatusFinished.JOB_STATUS_WARNING: 'Warning',
        JobStatusFinished.JOB_STATUS_ERROR: 'Error'
    }


class BackupSetTypes:
    BS_TYPE_FOLDERS = 0
    BS_TYPE_FOLDERS_DESC = "Folders"
    BS_TYPE_FILESFOLDERS = 1
    BS_TYPE_FILESFOLDERS_DESC = "Files and Folders"


# might put these in the database later
class BackupSetList:
    BACKUP_SETS = {
        BackupSetTypes.BS_TYPE_FOLDERS: BackupSetTypes.BS_TYPE_FOLDERS_DESC,
        BackupSetTypes.BS_TYPE_FILESFOLDERS: BackupSetTypes.BS_TYPE_FILESFOLDERS_DESC
    }


class Credential:
    CREDENTIAL_ENVIRONMENT_VAR_NAME = "UB_CREDENTIAL_STORE_PASSWORD"
    CREDENTIAL_KEY_GROUP_NAME = "CREDENTIAL_PASSWORD"
    CREDENTIAL_KEY_ROLE_NAME = "KEY"
    CREDENTIAL_DB_ENCRYPTED = "CREDENTIAL_DB_ENCRYPTED"


class System:
    DB_INITIALIZED_VAR_NAME = "DB_INITIALIZED"


class PhysicalLocation:
    UB_FOLDER_NAME = "UB_Location"


class PhysicalLocationTypes:
    LOCATION_TYPE_LOCAL = 1
    LOCATION_TYPE_LOCAL_DESC = "Local"

