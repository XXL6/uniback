from os import environ
from flask.cli import with_appcontext
from uniback.models.system import CredentialStore, SysVars
from uniback.dictionary.uniback_variables import System
from Crypto.Cipher import AES
from flask import current_app as app
from flask.cli import with_appcontext
import logging
logging.getLogger('mainLogger')


def get_credential(_credential_role, _reference_id, _service_name=""):
    if credentials_encrypted() and credentials_locked():
        logging.error(f'Could not get credential data for role={_credential_role} service={_service_name} as the \
                        credential store is encrypted and locked')
        raise Exception("Database locked.")
    credential = CredentialStore.query.filter_by(credential_role=_credential_role,
                                                 reference_id=_reference_id).first()
    if credentials_encrypted():
        decryption_password = environ.get(System.CREDENTIAL_ENVIRONMENT_VAR_NAME)
        if decryption_password is None:
            logging.error(f'Credential database marked as unlocked but no key provided')
            raise Exception("No password specified for credential store")
        obj = AES.new(decryption_password, AES.MODE_CFB)
        decrypted_credential = obj.decrypt(credential.credential_data)
        return decrypted_credential
    return credential.credential_data


def credentials_encrypted():
    encrypted = SysVars.query.filter_by(var_name="CREDENTIAL_DATABASE_ENCRYPTED").first().var_data == 'TRUE'
    return encrypted


def credentials_locked():
    with app.app_context():
        locked = SysVars.query.filter_by(var_name="CREDENTIAL_DATABASE_LOCKED").first().var_data == 'TRUE'
    return locked


def set_credentials_encrypted():
    pass