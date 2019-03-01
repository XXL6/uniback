from os import environ
from uniback.models.system import CredentialStore, SysVars,\
    CredentialGroup, SysVarsMemory
from uniback.dictionary.uniback_constants import Credential
from uniback.dictionary.uniback_exceptions import CredentialsLockedException
from sqlalchemy import exc, create_engine
from sqlalchemy.orm import sessionmaker
from Crypto.Cipher import AES
import logging
import bcrypt
from multiprocessing import current_process
from sqlalchemy.exc import OperationalError


class CredentialManager():

    def __init__(self):
        self.logger = logging.getLogger('mainLogger')
        engine = create_engine('sqlite:///../ub_system.db')
        Session = sessionmaker(bind=engine)
        self.session = Session()
        # if the database is encrypted we want to say that it's
        # locked as well on initialization, but if the database
        # is not encrypted, then the credentials would not be locked
        # if there's an attribute error or an operational error
        # that usually means that the database has not yet been initialized
        # and we can then deduce that the database would not de encrypted
        # either
        try:
            self._credentials_locked = self.credentials_encrypted()
        except OperationalError:
            self._credentials_locked = False
        except AttributeError:
            self._credentials_locked = False
        # crypt key kept in memory
        self.crypt_key = ""

    def assign_session(self, session):
        self.session = session

    def get_credential(self, group_id, credential_role):
        if self.credentials_encrypted() and self.credentials_locked():
            self.logger.error(f"Could not get credential data for "
                              f"role={credential_role} as "
                              "credential store is encrypted and locked")
            raise CredentialsLockedException
        credential = self.session.query(CredentialStore).filter_by(
                                            credential_role=credential_role,
                                            group_id=group_id).first()
        if self.credentials_encrypted():
            decryption_key = self.get_crypt_key()
            if decryption_key is None:
                self.logger.error(f"Credential database marked as "
                                  "unlocked but no key provided")
                raise Exception("No password specified for credential store")
            self.decrypt_string(credential.credential_data,
                                self.get_crypt_key())
        return credential.credential_data

    # returns a list of credential objects belonging to a certain group
    def get_group_credentials(self, group_id):
        if self.credentials_encrypted() and self.credentials_locked():
            self.logger.error(f"Could not get credentials for group="
                              "{group_id} as credential store is "
                              "encrypted and locked")
            raise CredentialsLockedException
        credentials = self.session.query(CredentialStore).filter_by(
            group_id=group_id)
        if self.credentials_encrypted():
            decryption_key = self.get_crypt_key()
            if decryption_key is None:
                self.logger.error(f"Credential database marked as "
                                  "unlocked but no key provided")
                raise Exception("No password specified for credential store")
            for credential in credentials:
                credential.credential_data = self.decrypt_string(
                    credential.credential_data, decryption_key)
        return credentials

    def get_all_credential_groups(self):
        if self.credentials_encrypted() and self.credentials_locked():
            self.logger.error("Could not retrieve credentials while "
                              "the credential database is locked.")
            raise CredentialsLockedException
        group_list = []
        credential_groups = self.session.query(CredentialGroup).order_by(
            CredentialGroup.id.asc())
        for group in credential_groups:
            temp_group = dict(
                description=group.description,
                service_name=group.service_name,
                group_id=group.id,
            )
            group_list.append(temp_group)
        return group_list

    def credentials_encrypted(self):
        encrypted = self.session.query(SysVars).filter_by(
            var_name=Credential.CREDENTIAL_DB_ENCRYPTED).first()
        return encrypted.var_data == '1'

    def credentials_locked(self):
#        locked = self.session2.query(SysVarsMemory).filter_by(
#            var_name="CREDENTIAL_DATABASE_ENCRYPTED").first()
#        return locked.var_data == '1'
        return False

    def set_credentials_encrypted(self, set_encrypted):
        encrypted = self.session.query(SysVars).filter_by(
            var_name=Credential.CREDENTIAL_DB_ENCRYPTED).first()
        encrypted.var_data = '1' if set_encrypted else '0'
        self.session.commit()

    def set_credentials_locked(self, set_locked):
 #       locked = self.session2.query(SysVarsMemory).filter_by(
 #           var_name="CREDENTIAL_DATABASE_ENCRYPTED").first()
 #       locked.var_data = '1' if set_locked else '0'
 #       self.session.commit()
        pass

    def encrypt_credentials(self, encryption_key):
        if self.credentials_encrypted() or self.credentials_locked():
            self.logger.error("Credential database encryption was attempted, "
                              "however, the database is already encrypted "
                              "or locked")
            raise CredentialsLockedException
        
            try:
                # we do not encrypt group_id of 0 as that's the built-in group
                # to check the validity of encryption password
                credential_list = self.session.query(CredentialStore).filter(
                    CredentialStore.group_id > 0)
            except exc.SQLAlchemyError as e:
                self.logger.error(f"Failure to query credential database. {e}")
                raise
            for instance in credential_list:
                encrypted_credential = self.encrypt_string(
                    instance.credential_data, encryption_key)
                instance.credential_data = encrypted_credential
            try:
                self.session.commit()
            except Exception as e:
                self.logger.error(
                    f"Failure to commit encrypted credential changes. {e}")
                raise
        self.set_crypt_key(encryption_key)
        # once all the checks complete we can conclude that the database
        # is now encrypted
        self.set_credentials_encrypted(True)

    # using the saved crypto key we decrypt all the credential_data
    # objects permanently and clear the old key from memory and
    # the database
    def decrypt_credentials(self):
        if self.credentials_locked():
            self.logger.error("Cannot decrypt credentials as the database "
                              "is locked.")
            raise CredentialsLockedException
        else:
            decryption_key = self.get_crypt_key()
            try:
                # we do not decrypt group_id of 0 as that's the 
                # built-in group to check the validity 
                # of encryption password
                credential_list = (self.session.query(CredentialStore).
                                   filter(CredentialStore.group_id > 0))
            except exc.InvalidRequestError as e:
                self.logger.error(f"Failure to query credential database.")
                raise e
            except exc.SQLAlchemyError as e:
                self.logger.error(f"General DB error.")
                raise e
            for instance in credential_list:
                decrypted_credential = self.decrypt_string(
                    instance.credential_data, decryption_key)
                instance.credential_data = decrypted_credential
            try:
                self.session.commit()
            except exc.InvalidRequestError as e:
                self.logger.error(
                    f"Failure to commit decrypted credential changes.")
                raise e
            except exc.SQLAlchemyError as e:
                self.logger.error(f"General DB error.")
                raise e
            self.set_crypt_key("")
            self.store_crypt_key("")
            # once all the checks complete we can conclude that the database
            # is now decrypted
            self.set_credentials_encrypted(False)

    # Basically if the encryption/decryption key is not currently set
    # the database is considered to be locked as the credential data
    # can no longer be decrypted on the fly
    def lock_credentials(self):
        try:
            environ.unsetenv(Credential.CREDENTIAL_ENVIRONMENT_VAR_NAME)
        except Exception as e:
            self.logger.error(f'Failed to lock credentials.')
            raise e
        self.set_credentials_locked(True)

    def unlock_credentials(self, key):
        try:
            hashed_key = self.session.query(CredentialStore).filter_by(
                group_id=0).first().credential_data
        except Exception as e:
            self.logger.error(f"Failure to query credential database "
                              "while unlocking credentials.")
            raise e
        if not bcrypt.check_password_hash(hashed_key, key):
            self.logger.error(f"Wrong password provided for "
                              "credential unlocking")
            raise
        self.set_crypt_key(key)
        self.set_credentials_locked(False)

    def get_crypt_key(self):
        # return environ.get(Credential.CREDENTIAL_ENVIRONMENT_VAR_NAME)
        # crypt_key = self.session2.query(SysVarsMemory).filter_by(
        # var_name=Credential.CREDENTIAL_ENVIRONMENT_VAR_NAME).first()
        # return crypt_key
        return self.crypt_key

    # method used to store the user's cryptographic key for later use
    # can be changed if environmental variables are not wanted
    def set_crypt_key(self, key):
        # environ[Credential.CREDENTIAL_ENVIRONMENT_VAR_NAME] = key
        # crypt_key = self.session2.query(SysVarsMemory).filter_by(
        #    var_name=Credential.CREDENTIAL_ENVIRONMENT_VAR_NAME).first()
        # crypt_key.var_data = key
        # self.session.commit()
        self.crypt_key = key

    # stores and encrypts they key in the database using bcrypt
    # this way we can see whether the user input the right key
    # to unlock the database without having to store the key itself
    def store_crypt_key(self, key):
        try:
            credential = self.session.query(CredentialStore).filter_by(
                    credential_role=Credential.CREDENTIAL_KEY_ROLE_NAME,
                    group_id=0).first()
        except exc.InvalidRequestError as e:
            self.logger.error(f"Failure to query credential database "
                              "while storing cryptographic key.")
            raise e
        except exc.SQLAlchemyError as e:
            self.logger.error("General DB error.")
            raise e
        try:
            credential_group = (self.session.query(CredentialGroup).
                                filter_by(id=0).first())
        except exc.InvalidRequestError as e:
            self.logger.error(f"Failure to query credential database "
                              "while storing cryptographic key.")
            raise e
        except exc.SQLAlchemyError as e:
            self.logger.error("General DB error.")
            raise e
        if credential_group and credential_group.description != \
                Credential.CREDENTIAL_KEY_GROUP_NAME:
            self.logger.error(f"Wrong item in id=0 location of the "
                              "credential group table.")
            raise
        elif not credential_group:
            new_credential_group = CredentialGroup(
                id=0,
                description=Credential.CREDENTIAL_KEY_GROUP_NAME,
                service_name=Credential.CREDENTIAL_KEY_GROUP_NAME)
            try:
                self.session.add(new_credential_group)
            except exc.InvalidRequestError as e:
                self.logger.error(f"Failure to add new credential group "
                                  "to the database.")
                raise e
            except exc.SQLAlchemyError as e:
                self.logger.error("General DB error.")
                raise e
        if not credential:
            new_credential = CredentialStore(
                group_id=0,
                credential_role=Credential.CREDENTIAL_KEY_ROLE_NAME,
                credential_data=bcrypt.generate_password_hash(key))
            try:
                self.session.add(new_credential)
            except exc.InvalidRequestError as e:
                self.logger.error(f"Failure to add the credential "
                                  "password hash to the credential "
                                  "database.")
                raise e
            except exc.SQLAlchemyError as e:
                self.logger.error("General DB error.")
                raise e
        self.session.commit()

    def encrypt_string(self, input_string, key):
        enc = AES.new(key, AES.MODE_CFB)
        return enc.encrypt(input_string)

    def decrypt_string(self, input_string, key):
        enc = AES.new(key, AES.MODE_CFB)
        return enc.decrypt(input_string)

    # removes all credential keys and groups
    # essentially has to be done if user encrypts
    # their database and forgets their password
    def reset_database(self):
        try:
            credentials_deleted = self.session.query(CredentialStore).filter(
                CredentialStore.group_id > 0).\
                delete(synchronize_session=False)
            self.session.commit()
        except exc.InvalidRequestError as e:
            self.logger.error(f"Failed to delete CredentialStore entries.")
            raise e
        except exc.SQLAlchemyError as e:
            self.logger.error("General DB error.")
            raise e
        try:
            credential_groups_deleted = (self.session.query(CredentialGroup).
                                         filter(CredentialGroup.id > 0).
                                         delete(synchronize_session=False))
            self.session.commit()
        except exc.InvalidRequestError as e:
            self.logger.error(f"Failed to reset CredentialGroup database.")
            raise e
        except exc.SQLAlchemyError as e:
            self.logger.error("General DB error.")
            raise e
        self.logger.info(f"[{credentials_deleted}] credentials deleted "
                         f" and [{credential_groups_deleted}] credential "
                         "groups deleted")
        self.set_credentials_encrypted(False)
        self.set_credentials_locked(False)
        self.set_crypt_key("")
        self.store_crypt_key("")

    # add a singular credential into the database
    # looks for a credential group with the specified
    # service name and assigns that group to the newly
    # added credential.
    # if it can't find the group with the specified
    # service name, it adds the group and then uses the newly
    # created group's id to create the credential
    def add_credential(self, service_name, credential_role, credential_data):
        if self.credentials_locked():
            self.logger.error(f"Unable to add [{credential_role}] "
                              f"for [{service_name}] as the credential "
                              "database is locked")
            raise CredentialsLockedException
        
            try:
                credential_group = (self.session.query(CredentialGroup).
                                    filter_by(service_name=service_name))
            except exc.InvalidRequestError as e:
                self.logger.error("Failed to query credential group database "
                                  "while adding new credential.")
                raise e
            except exc.SQLAlchemyError as e:
                self.logger.error("General DB error.")
                raise e
            if credential_group:
                group_id = credential_group.id
            else:
                credential_group = CredentialGroup(service_name=service_name)
                self.session.add(credential_group)
                self.session.commit()
                group_id = credential_group.id
            new_credential = CredentialStore(
                credential_role=credential_role,
                credential_data=credential_data,
                group_id=group_id)
            if self.credentials_encrypted():
                new_credential.credential_data = self.encrypt_string(
                    new_credential.credential_data,
                    self.get_crypt_key()
                )
            self.session.add(new_credential)
            self.session.commit()
        return group_id

    # Removes all credentials belonging to a certain group including
    # the group itself
    def remove_credentials(self, group_id):
        credentials_deleted = self.session.query(CredentialStore).filter_by(
            group_id=group_id).delete(synchronize_session=False)
        credential_group = self.session.query(CredentialGroup).filter_by(
            id=group_id).delete(synchronize_session=False)
        self.session.commit()
        if credentials_deleted > 0:
            self.logger.info(f"{credentials_deleted} credentials "
                             f"with group id of {group_id} have been deleted.")
        else:
            self.logger.warning(f"No credentials have been deleted for "
                                f"group id of {group_id}")
        if credential_group > 0:
            self.logger.info(f"Credential group with id {group_id} "
                             "has been deleted.")
        else:
            self.logger.warning(f"No credential groups with id {group_id} "
                                "have been deleted.")

    # sets a description to a credential group
    def set_group_description(self, group_id, description):
        credential_group = self.session.query(CredentialGroup).filter_by(
            id=group_id
        )
        if not credential_group:
            self.logger.error(f"Unable to set description to "
                              "group {group_id}")
            raise Exception
        credential_group.description = description
        self.session.commit()
