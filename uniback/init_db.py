from uniback import create_app, db
from uniback.tools import credential_tools
from uniback.models.system import CredentialGroup, CredentialStore

def test():
    app = create_app()

    with app.app_context():
        new_group = CredentialGroup(service_name="test service", description="test description")
        new_store = CredentialStore(group_id=1, credential_role="test role", credential_data="test data")
        new_store2 = CredentialStore(group_id=1, credential_role="test role 2", credential_data="test data 2")
        db.session.add(new_group)
        db.session.add(new_store)
        db.session.add(new_store2)
        db.session.commit()
