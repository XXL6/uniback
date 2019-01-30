from os import environ
from uniback.models.system import CredentialStore, SysVars
from uniback.dictionary.uniback_variables import System
from uniback import db
from Crypto.Cipher import AES
from flask import current_app as app
import logging

logging.getLogger('mainLogger')


def get_credential(_credential_role, _reference_id, _service_name=""):
    if credentials_encrypted() and credentials_locked():
        logging.error(f'Could not get credential data for role={_credential_role} \
                        service={_service_name} as the \
                        credential store is encrypted and locked')
        raise Exception("Database locked.")
    with app.app_context():
        credential = CredentialStore.query.filter_by(
                                            credential_role=_credential_role,
                                            reference_id=_reference_id).first()
    if credentials_encrypted():
        decryption_key = environ.get(
                                System.CREDENTIAL_ENVIRONMENT_VAR_NAME)
        if decryption_key is None:
            logging.error(f'Credential database marked as \
                            unlocked but no key provided')
            raise Exception("No password specified for credential store")
        obj = AES.new(decryption_key, AES.MODE_CFB)
        decrypted_credential = obj.decrypt(credential.credential_data)
        return decrypted_credential
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


def set_credentials_encrypted(_set_encrypted):
    with app.app_context():
        encrypted = SysVars.query.filter_by(
            var_name="CREDENTIAL_DATABASE_ENCRYPTED").first()
        encrypted.var_data = '1' if _set_encrypted else '0'
        db.session.commit()


def set_credentials_locked(_set_locked):
    with app.app_context():
        locked = SysVars.query.filter_by(
            var_name="CREDENTIAL_DATABASE_LOCKED").first()
        locked.var_data = '1' if _set_locked else '0'
        db.session.commit()


def encrypt_credentials(encryption_key):
    if credentials_encrypted() or credentials_locked():
        logging.error("Credential database encryption was attempted, \
                        however, the database is already encrypted or locked")
        raise("Can't encrypt an encrypted database")
    with app.app_context():
        credential_list = CredentialStore.query.filter(CredentialStore.reference_id > 0)