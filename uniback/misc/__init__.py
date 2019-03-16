# from uniback.tools.credential_manager import CredentialManager
from uniback import db
from uniback.tools.credential_manager import CredentialManager
from multiprocessing import current_process
from uniback.tools.job_tools import JobQueue
from uniback.tools.job_runner import JobRunner
from uniback import process_manager

# this is a separate package for initializing objects that
# might not be initializable in the main __init__ file due to
# them trying to import things from the said __init__ file and
# thus causing a circular import

credential_manager = CredentialManager()
# if it's the main application process, that means its' db.session is
# going to have the necessary app context and we don't need to
# manually create sessions. Manually creating the sessions will
# cause issues in the main application process as some route
# handling might be multithreaded

job_queue = JobQueue()
job_runner = JobRunner(queue=job_queue, process_manager=process_manager)
job_runner.start()
