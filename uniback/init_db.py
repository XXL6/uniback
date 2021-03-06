from uniback import db, bcrypt
from uniback.models.general import CredentialGroup, CredentialStore, SysVars
from uniback.dictionary.uniback_constants import System, Credential
from uniback.blueprints.users.models import User
from sqlalchemy.exc import OperationalError
import logging
from uniback.dictionary.uniback_exceptions import UBInitFailure


def init_db():
    logger = logging.getLogger("mainLogger")
    try:
        db_initialized = SysVars.query.filter_by(
            var_name=System.DB_INITIALIZED_VAR_NAME).first()
    except OperationalError as e:
        raise UBInitFailure("init_db was called before the databases/tables "
                            f"were created. ---- {e}")
    if db_initialized is None:
        pass  # db not initialized so we can proceed with initialization
    elif db_initialized.var_data == "1":
        return  # we can safely return if the db has been initialized

    # initialize the storage for the credential database encryption key
    credential_key_group = CredentialGroup(
            id=0,
            service_name=Credential.CREDENTIAL_KEY_GROUP_NAME)
    credential_key = CredentialStore(
        group_id=0,
        credential_role=Credential.CREDENTIAL_KEY_ROLE_NAME,
        credential_data=""
    )
    db.session.add(credential_key_group)
    db.session.add(credential_key)

    # initialize the indicator whether or not credential database is encrypted
    cred_db_encrypted = SysVars(
        var_name=Credential.CREDENTIAL_DB_ENCRYPTED,
        var_data="0"
    )
    db.session.add(cred_db_encrypted)

    # add a default username and password for logging in
    user = User(
        username="admin",
        password=bcrypt.generate_password_hash("password").decode('utf-8')
    )
    db.session.add(user)

    # we'll try committing all those objects that we have just added
    try:
        db.session.commit()
    except OperationalError as e:
        logger.error(f"Failed to initialize the database: {e}")
        raise UBInitFailure

    # we can finally declare the database as initialized
    db_initialized = SysVars(
        var_name=System.DB_INITIALIZED_VAR_NAME,
        var_data="1"
    )
    db.session.add(db_initialized)
    db.session.commit()