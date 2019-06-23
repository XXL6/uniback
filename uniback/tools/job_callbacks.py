import uniback.db_interfaces.repository_list as repository_interface
import json


# adds the newly created repository information into the database
def repository_add_to_db(job):
    data_dict = {}
    for key, value in job.process.field_dict.items():
        if ((key != 'ub_name') and (key != 'ub_description')):
            data_dict[key] = value
    repository_interface.add_repository(
        dict(
            name=job.process.field_dict['ub_name'],
            description=job.process.field_dict['ub_description'],
            data=json.dumps(data_dict),
            engine=job.engine,
            physical_location_id=job.process.field_dict['location']
        )
    )
