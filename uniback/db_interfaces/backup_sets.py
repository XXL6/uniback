from uniback.models.general import BackupSet
from uniback.tools.local_session import LocalSession
from uniback.dictionary.uniback_constants import BackupSetList


def delete_backup_set(id):
    with LocalSession() as session:
        session.query(BackupSet).filter_by(id=id).delete()
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


def add_backup_set(info):
    with LocalSession() as session:
        backup_set = (
            BackupSet(
                name=info['name'],
                data=info['data'],
                type=info['type']
            )
        )
        session.add(backup_set)
        session.commit()


def get_backup_set_info(id):
    with LocalSession() as session:
        backup_set = session.query(BackupSet).filter_by(id=id).first()
        if backup_set:
            info_dict = dict(
                id=backup_set.id,
                name=backup_set.name,
                type=BackupSetList.BACKUP_SETS[backup_set.type],
                data=backup_set.data,
                time_added=backup_set.time_added
            )
        else:
            info_dict = dict(
                id="UNDEFINED",
                name="UNDEFINED",
                data="UNDEFINED",
                type="UNDEFINED",
                time_added="UNDEFINED"
            )
        return info_dict
