from os import environ
from uniback.models.system import CredentialStore, SysVars
from uniback.dictionary.uniback_variables import System
from uniback import db
from Crypto.Cipher import AES
from flask import current_app as app
import logging

logging.getLogger('mainLogger')


def get_credential(credential_role, reference_id, service_name=""):
    if credentials_encrypted() and credentials_locked():
        logging.error(f'Could not get credential data for role={credential_role} \
                        service={service_name} as the \
                        credential store is encrypted and locked')
        raise Exception("Database locked.")
    with app.app_context():
        credential = CredentialStore.query.filter_by(
                                            credential_role=credential_role,
                                            reference_id=reference_id).first()
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
        raise("Can't encrypt an encrypted database")
    with app.app_context():
        try:
            # we do not encrypt group_id of 0 as that's the built-in group
            # to check the validity of encryption password
            credential_list = CredentialStore.query.filter(
                CredentialStore.group_id > 0)
        except Exception as e:
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
    # once all the checks complete we can conclude that the database
    # is now encrypted
    set_credentials_encrypted(True)


def lock_credentials():
    environ.unsetenv(System.CREDENTIAL_ENVIRONMENT_VAR_NAME)
    set_credentials_locked(False)


def unlock_credentials():
    pass


def get_crypt_key():
    return environ.get(System.CREDENTIAL_ENVIRONMENT_VAR_NAME)


def set_crypt_key(key):
    environ[System.CREDENTIAL_ENVIRONMENT_VAR_NAME] = key


def encrypt_string(input_string, key):
    enc = AES.new(key, AES.MODE_CFB)
    return enc.encrypt(input_string)


def decrypt_string(input_string, key):
    enc = AES.new(key, AES.MODE_CFB)
    return enc.decrypt(input_string)
