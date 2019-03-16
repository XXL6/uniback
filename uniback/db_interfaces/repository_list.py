import os
from uniback.dictionary.uniback_constants import Repository as Rep
from uniback.models.general import Repository
from uniback.tools.local_session import LocalSession


def init_repository(engine, name):
    with LocalSession() as session:
        pass        
        