# file will contain classes and other functionality
# in order to check and keep track of physical locations
# so that engine plugins can use them to initialize
# their repositories
import os
from uniback.dictionary.uniback_constants import PhysicalLocation as PL
from uniback.models.general import PhysicalLocation
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
                concurrent_jobs=location.concurrent_jobs,
                status=get_location_status(id))
        else:
            info_dict = dict(
                name="UNDEFINED",
                address="UNDEFINED",
                type="UNDEFINED",
                concurrent_jobs=0,
                status="Undefined")
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


def get_physical_locations():
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
                    status=get_location_status(location.id)
                )
            )
        return return_list


def get_location_status(id):
    with LocalSession() as session:
        physical_location = session.query(PhysicalLocation).filter_by(id=id).first()
        if physical_location:
            address = physical_location.address
            type = physical_location.type
        else:
            address = None
            type = None
    
    if type == 'local':
        return 'Online' if os.path.exists(address) and os.path.isdir(address) else 'Offline'
    else:
        return 'Unknown Type'
