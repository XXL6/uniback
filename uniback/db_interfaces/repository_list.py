import os
# from uniback.dictionary.uniback_constants import Repository as Rep
from uniback.models.general import Repository
from uniback.tools.local_session import LocalSession


def init_repository(engine, name):
    with LocalSession() as session:
        pass        
        

def add_repository(info):
    with LocalSession() as session:
        repository = Repository(
            name=info['name'],
            description=info.get('description'),
            data=info['data'],
            engine=info['engine'],
            physical_location_id=info['physical_location_id']
        )
        session.add(repository)
        session.commit()


def delete_repositories(ids):
    with LocalSession() as session:
        for id in ids:
            session.query(Repository).filter_by(id=id).delete()
        session.commit()


def get_engine_repositories(engine_name):
    repository_list = []
    with LocalSession() as session:
        repositories = session.query(Repository).filter_by(engine=engine_name)
        for repository in repositories:
            repository_list.append((repository.id, repository.name))
    return repository_list


def get_info(id):
    info_dict = {}
    with LocalSession() as session:
        repository = session.query(Repository).filter_by(id=id).first()
        info_dict = dict(
            name=repository.name,
            description=repository.description,
            data=repository.data,
            engine=repository.engine,
            physical_location_id=repository.physical_location_id,
            physical_location_name=repository.physical_location.name
        )
    return info_dict