# file will contain classes and other functionality
# in order to check and keep track of physical locations
# so that engine plugins can use them to initialize
# their repositories
import os
from uniback.dictionary.uniback_constants import PhysicalLocation as PL
from uniback.models.general import PhysicalLocation, PhysicalLocationType
from uniback.tools.local_session import LocalSession


def init_physical_location(name, address, type, concurrent_jobs=1):
    # the location where the ub folder will go
    ub_directory = os.path.join(address, PL.UB_FOLDER_NAME)
    # we check if a folder already exists for ub usage
    if os.path.exists(ub_directory):
        if not os.path.isdir(ub_directory):
            raise Exception(
                f"A file named {PL.UB_FOLDER_NAME} "
                "exists, but it's not a folder.")
    # create a new folder in case one does not already exist
    else:
        try:
            os.mkdir(ub_directory)
        except Exception:
            raise Exception("Failed to initialize UB directory")
    
    physical_location = PhysicalLocation(
        name=name,
        type=type,
        address=ub_directory,
        concurrent_jobs=concurrent_jobs)
    with LocalSession() as session:
        session.add(physical_location)
        session.commit()


def delete_location(id):
    with LocalSession() as session:
        session.query(PhysicalLocation).filter_by(id=id).delete()
        session.commit()


def get_location_info(id):
    with LocalSession() as session:
        location = session.query(PhysicalLocation).filter_by(id=id).first()
        if location:
            info_dict = dict(
                name=location.name,
                address=location.address,
                type=location.type,
                concurrent_jobs=location.concurrent_jobs
            )
        else:
            info_dict = dict(
                name="UNDEFINED",
                address="UNDEFINED",
                type="UNDEFINED",
                concurrent_jobs=0)
        return info_dict


def set_location_info(id, info):
    with LocalSession() as session:
        location = session.query(PhysicalLocation).filter_by(id=id).first()
        if location:
            location.name = info.get('name')
            location.address = info.get('address')
            location.type = info.get('type')
            location.concurrent_jobs = info.get('concurrent_jobs')
            session.commit()


def add_location(info):
    with LocalSession() as session:
        location = (
            PhysicalLocation(
                name=info.get('name'),
                address=info.get('address'),
                type=info.get('type'),
                concurrent_jobs=info.get('concurrent_jobs')
            )
        )
        session.add(location)
        session.commit()


def get_physical_locations(get_status=False):
    with LocalSession() as session:
        physical_locations = session.query(PhysicalLocation)
        return_list = []
        for location in physical_locations:
            return_list.append(
                dict(
                    id=location.id,
                    name=location.name,
                    address=location.address,
                    type=location.type,
                    concurent_jobs=location.concurrent_jobs,
                    status=get_location_status(location.id) if get_status else ''
                )
            )
        return return_list


def get_location_status(id):
    with LocalSession() as session:
        physical_location = session.query(PhysicalLocation).filter_by(id=id).first()
        if physical_location:
            # physical_location_type = session.query(PhysicalLocationType).filter_by(id=physical_location.type).first()
            address = physical_location.address
            type = physical_location.physical_location_type.name
        else:
            address = None
            type = None
    
    if type == 'localhost':
        return 'Online' if os.path.exists(address) and os.path.isdir(address) else 'Offline'
    else:
        return 'Unknown Type'


def get_location_types():
    return_list = []
    with LocalSession() as session:
        types = session.query(PhysicalLocationType).order_by(PhysicalLocationType.name.desc())
        for type in types:
            return_list.append(dict(
                id=type.id,
                name=type.name,
                subtype=type.subtype,
                description=type.description
            ))
    return return_list


def get_location_type(id):
    return_dict = None
    with LocalSession() as session:
        type = session.query(PhysicalLocationType).filter_by(id=id).first()
        if type:
            return_dict = dict(
                id=type.id,
                name=type.name,
                subtype=type.subtype,
                description=type.description
            )
    return return_dict


def add_location_type(info):
    with LocalSession() as session:
        type = (
            PhysicalLocationType(
                name=info['name'],
                subtype=info['subtype'],
                description=info.get('description')
            )
        )
        session.add(type)
        session.commit()


def set_location_type(id, info):
    with LocalSession() as session:
        type = session.query(PhysicalLocationType).filter_by(id=id).first()
        if type:
            type.name = info.get('name')
            type.type = info.get('subtype')
            type.description = info.get('description')
            session.commit()


def delete_location_type(id):
    with LocalSession() as session:
        session.query(PhysicalLocationType).filter_by(id=id).delete()
        session.commit()