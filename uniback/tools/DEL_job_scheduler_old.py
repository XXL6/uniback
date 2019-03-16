import time
from uniback.tools.ub_process import UBProcess
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from uniback.misc import credential_manager

# WORK IN PROGRESS
# Job scheduler will be a thread instead of a process
# this class left as a reference


class JobSchedulerOld(UBProcess):
    
    description = ("Periodically checks the job database and submits "
                   "jobs that are due for running.")
    ub_name = "Job Scheduler"
    ub_category = "system"

    def run(self):
        self.init_db_session()
        # group = self.session.query(JobQueue).filter_by(id=0)
        # self.logger.debug("process says" + group.description)
        self.queue.put(
            {'process_id': self.pid,
             'data_name': 'testvar',
             'data': "It totally worked :^)"})
        self.logger.debug("This pid == " + str(self.pid))
        try:
            test = credential_manager.get_all_credential_groups()
            for butt in test:
                self.logger.debug("butt" + butt['description'])
        except Exception as e:
            self.logger.debug(e)
        while True:
            credential_manager.get_crypt_key()
            time.sleep(10)

    def init_db_session(self):
        engine = create_engine('sqlite:///../ub_system.db')
        Session = sessionmaker(bind=engine)
        self.session = Session()
