from os import environ
from uniback.models.system import CredentialStore, SysVars, CredentialGroup
from uniback.dictionary.uniback_variables import Credential
from uniback.dictionary.uniback_exceptions import DbGeneralException
from sqlalchemy import exc
from uniback import db, bcrypt
from Crypto.Cipher import AES
from flask import current_app as app
import logging

logging.getLogger('mainLogger')


def get_credential(group_id, credential_role):
    if credentials_encrypted() and credentials_locked():
        logging.error(f'Could not get credential data for role={credential_role} \
                        credential store is encrypted and locked')
        raise DbGeneralException("Database locked.")
    with app.app_context():
        credential = CredentialStore.query.filter_by(
                                            credential_role=credential_role,
                                            group_id=group_id).first()
    if credentials_encrypted():
        decryption_key = get_crypt_key()
        if decryption_key is None:
            logging.error(f'Credential database marked as \
                            unlocked but no key provided')
            raise Exception("No password specified for credential store")
        decrypt_string(credential.credential_data, get_crypt_key())
    return credential.credential_data


def credentials_encrypted():
    with app.app_context():
        encrypted = SysVars.query.filter_by(
            var_name="CREDENTIAL_DATABASE_ENCRYPTED").first()
    return encrypted.var_data == '1'


def credentials_locked():
    with app.app_context():
        locked = SysVars.query.filter_by(
            var_name="CREDENTIAL_DATABASE_LOCKED").first()
    return locked.var_data == '1'


def set_credentials_encrypted(set_encrypted):
    with app.app_context():
        encrypted = SysVars.query.filter_by(
            var_name="CREDENTIAL_DATABASE_ENCRYPTED").first()
        encrypted.var_data = '1' if set_encrypted else '0'
        db.session.commit()


def set_credentials_locked(set_locked):
    with app.app_context():
        locked = SysVars.query.filter_by(
            var_name="CREDENTIAL_DATABASE_LOCKED").first()
        locked.var_data = '1' if set_locked else '0'
        db.session.commit()


def encrypt_credentials(encryption_key):
    if credentials_encrypted() or credentials_locked():
        logging.error("Credential database encryption was attempted, \
                        however, the database is already encrypted or locked")
        raise Exception("Can't encrypt an encrypted database")
    with app.app_context():
        try:
            # we do not encrypt group_id of 0 as that's the built-in group
            # to check the validity of encryption password
            credential_list = CredentialStore.query.filter(
                CredentialStore.group_id > 0)
        except exc.SQLAlchemyError as e:
            logging.error(f"Failure to query credential database. {e}")
            raise
        for instance in credential_list:
            encrypted_credential = encrypt_string(
                instance.credential_data, encryption_key)
            instance.credential_data = encrypted_credential
        try:
            db.session.commit()
        except Exception as e:
            logging.error(
                f"Failure to commit encrypted credential changes. {e}")
            raise
    set_crypt_key(encryption_key)
    # once all the checks complete we can conclude that the database
    # is now encrypted
    set_credentials_encrypted(True)


def decrypt_credentials(encryption_key):
    with app.app_context():
        try:
            # we do not decrypt group_id of 0 as that's the built-in group
            # to check the validity of encryption password
            credential_list = CredentialStore.query.filter(
                CredentialStore.group_id > 0)
        except exc.InvalidRequestError as e:
            logging.error(f"Failure to query credential database.")
            raise e
        except exc.SQLAlchemyError as e:
            logging.error(f"General DB error.")
            raise e
        for instance in credential_list:
            decrypted_credential = decrypt_string(
                instance.credential_data, encryption_key)
            instance.credential_data = decrypted_credential
        try:
            db.session.commit()
        except exc.InvalidRequestError as e:
            logging.error(
                f"Failure to commit decrypted credential changes.")
            raise e
        except exc.SQLAlchemyError as e:
            logging.error(f"General DB error.")
            raise e
    # once all the checks complete we can conclude that the database
    # is now decrypted
    set_credentials_encrypted(False)


def lock_credentials():
    try:
        environ.unsetenv(Credential.CREDENTIAL_ENVIRONMENT_VAR_NAME)
    except Exception as e:
        logging.error(f'Failed to lock credentials.')
        raise e
    set_credentials_locked(False)


def unlock_credentials(key):
    try:
        hashed_key = CredentialStore.query.filter_by(
            group_id=0).first().credential_data
    except Exception as e:
        logging.error(f"Failure to query credential database \
            while unlocking credentials.")
        raise e
    if not bcrypt.check_password_hash(hashed_key, key):
        logging.error(f"Wrong password provided for credential unlocking")
        raise
    set_crypt_key(key)


def get_crypt_key():
    return environ.get(Credential.CREDENTIAL_ENVIRONMENT_VAR_NAME)


# method used to store the user's cryptographic key for later use
# can be changed if environmental variables are not wanted
def set_crypt_key(key):
    environ[Credential.CREDENTIAL_ENVIRONMENT_VAR_NAME] = key


# stores and encrypts they key in the database using bcrypt
# this way we can see whether the user input the right key
# to unlock the database. 
def store_crypt_key(key):
    with app.app_context():
        try:
            credential = CredentialStore.query.filter_by(
                        credential_role=Credential.CREDENTIAL_KEY_ROLE_NAME,
                        group_id=Credential.CREDENTIAL_KEY_GROUP_NAME).first()
        except exc.InvalidRequestError as e:
            logging.error(f"Failure to query credential database \
                while storing cryptographic key.")
            raise e
        except exc.SQLAlchemyError as e:
            logging.error("General DB error.")
            raise e
        try:
            credential_group = CredentialGroup.query.filter_by(
                        id=0).first()
        except exc.InvalidRequestError as e:
            logging.error(f"Failure to query credential database \
                while storing cryptographic key.")
            raise e
        except exc.SQLAlchemyError as e:
            logging.error("General DB error.")
            raise e
        if credential_group and credential_group.description != \
                Credential.CREDENTIAL_KEY_GROUP_NAME:
            logging.error(f"Wrong item in id=0 location of the \
                credential group table.")
            raise
        else:
            new_credential_group = CredentialGroup(
                id=0,
                description=Credential.CREDENTIAL_KEY_GROUP_NAME)
            try:
                db.session.add(new_credential_group)
            except exc.InvalidRequestError as e:
                logging.error(f"Failure to add new credential group \
                    to the database.")
                raise e
            except exc.SQLAlchemyError as e:
                logging.error("General DB error.")
                raise e
        if not credential:
            new_credential = CredentialStore(
                group_id=0,
                service_name=Credential.CREDENTIAL_KEY_GROUP_NAME,
                credential_role=Credential.CREDENTIAL_KEY_ROLE_NAME,
                credential_data=bcrypt.generate_password_hash(key))
            try:
                db.session.add(new_credential)
            except exc.InvalidRequestError as e:
                logging.error(f"Failure to add the credential password \
                    hash to the credential database.")
                raise e
            except exc.SQLAlchemyError as e:
                logging.error("General DB error.")
                raise e


def encrypt_string(input_string, key):
    enc = AES.new(key, AES.MODE_CFB)
    return enc.encrypt(input_string)


def decrypt_string(input_string, key):
    enc = AES.new(key, AES.MODE_CFB)
    return enc.decrypt(input_string)


# removes all credential keys and groups
# essentially has to be done if user encrypts
# their database and forgets their password
def reset_database():
    with app.app_context():
        try:
            credentials_deleted = CredentialStore.query.filter(
                CredentialStore.group_id > 0).\
                delete(synchronize_session=False)
        except exc.InvalidRequestError as e:
            logging.error(f"Failed to delete CredentialStore entries.")
            raise e
        except exc.SQLAlchemyError as e:
            logging.error("General DB error.")
            raise e
        try:
            credential_group_deleted = CredentialGroup.query.filter(
                CredentialGroup.id > 0).\
                delete(synchronize_session=False)
        except exc.InvalidRequestError as e:
            logging.error(f"Failed to reset CredentialGroup database.")
            raise e
        except exc.SQLAlchemyError as e:
            logging.error("General DB error.")
            raise e
        logging.info(f"[{credentials_deleted}] credentials deleted and \
            [{credential_group_deleted}] credential groups deleted. ")
    set_credentials_encrypted(False)
    set_credentials_locked(False)
    set_crypt_key("")
    store_crypt_key("")


def add_credential(service_name, credential_role, credential_data):
    with app.app_context():
        try:
            credential_group = CredentialGroup.query.filter_by(
                service_name=service_name)
        except exc.InvalidRequestError as e:
            logging.error("Failed to query credential group database \
                while adding new credential.")
            raise e
        except exc.SQLAlchemyError as e:
            logging.error("General DB error.")
            raise e
        if credential_group:
            group_id = credential_group.id
        else:
            credential_group = CredentialGroup(service_name=service_name)
            db.session.add(credential_group)
        new_credential = CredentialStore(
            credential_role=credential_role,
            credential_data=credential_data,
            group_id=group_id)
