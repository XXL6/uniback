from uniback.models.general import BackupSet, BackupObject
from uniback.tools.local_session import LocalSession
from uniback.dictionary.uniback_constants import BackupSetList, BackupSetTypes
import json


def delete_backup_set(id):
    with LocalSession() as session:
        session.query(BackupSet).filter_by(id=id).delete()
        session.commit()


def delete_backup_sets(ids):
    with LocalSession() as session:
        for id in ids:
            session.query(BackupSet).filter_by(id=id).delete()
            session.query(BackupObject).filter_by(backup_set_id=id).delete()
        session.commit()


def get_backup_sets():
    with LocalSession() as session:
        backup_sets = session.query(BackupSet)
        return_list = []
        for backup_set in backup_sets:
            return_list.append(
                dict(
                    id=backup_set.id,
                    name=backup_set.name,
                    type=BackupSetList.BACKUP_SETS[backup_set.type]
                )
            )
        return return_list

# used for getting a tuple of values to be added to a select field
# on a form
def get_backup_sets_tuple():
    with LocalSession() as session:
        backup_sets = session.query(BackupSet)
        return_list = []
        for backup_set in backup_sets:
            return_list.append(
                (backup_set.id, backup_set.name)
            )
        return return_list


def add_backup_set(data):
    with LocalSession() as session:
        if data['type'] == BackupSetTypes.BS_TYPE_FILESFOLDERS:
            json_object = json.loads(data['backup_object_data']['file_list'])
            backup_object_list = json_object['file_list']
            display_state = json.dumps(json_object['state'])
        else: 
            raise Exception(f"Unsupported backup set {data['type']}")
        backup_set = (
            BackupSet(
                name=data['name'],
                type=data['type'],
                source=data['source'],
                data=display_state
            )
        )
        print(display_state)
        session.add(backup_set)
        session.commit()
        for backup_object in backup_object_list:
            new_backup_object = BackupObject(
                data=backup_object,
                backup_set_id=backup_set.id)
            session.add(new_backup_object)
        session.commit()


def get_backup_set_info(id):
    with LocalSession() as session:
        backup_set = session.query(BackupSet).filter_by(id=id).first()
        set_item_list = session.query(BackupObject).filter_by(backup_set_id=id)
        set_item_list_data = []
        for item in set_item_list:
            set_item_list_data.append(item.data)
        if backup_set:
            info_dict = dict(
                id=backup_set.id,
                name=backup_set.name,
                source=backup_set.source,
                type_name=BackupSetList.BACKUP_SETS[backup_set.type],
                data=backup_set.data,
                type=backup_set.type,
                time_added=backup_set.time_added
            )
        else:
            info_dict = dict(
                id="UNDEFINED",
                name="UNDEFINED",
                source="UNDEFINED",
                type_name="UNDEFINED",
                type="UNDEFINED",
                time_added="UNDEFINED"
            )
        return info_dict, set_item_list_data
