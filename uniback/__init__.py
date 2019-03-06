from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import logging
from uniback import ub_logging
from uniback.tools.process_manager import ProcessManager
# from uniback.tools.credential_manager import CredentialManager

# import uniback.tools.credential_manager as cm
from multiprocessing import current_process
# from test2.process_manager import ProcessManager

ub_logging.initialize_logging()
db = SQLAlchemy()
process_manager = ProcessManager()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
logger = logging.getLogger('mainLogger')
bcrypt = Bcrypt()
print(current_process().name)
print(__name__)