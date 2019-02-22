from flask import Blueprint, render_template, flash, redirect, \
    url_for, request
from flask_login import login_required, current_user
from .forms import UpdateAccountForm, UnlockCredentialStore, \
    LockCredentialStore
from uniback import bcrypt, db
from uniback.models.system import CredentialGroup
from uniback.tools.credential_tools import credentials_locked, \
    get_all_credential_groups, get_group_credentials, remove_credentials
import logging
import json

settings = Blueprint('settings', '__name__')
logger = logging.getLogger('debugLogger')

@settings.route(f'/{settings.name}', methods=['GET', 'POST'])
@settings.route(f'/{settings.name}/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        if form.password.data != "":
            hashed_password = bcrypt.generate_password_hash(
                form.password.data).decode('utf-8')
            current_user.password = hashed_password
        db.session.commit()
        flash("Account information has been updated", 'success')
        return redirect(url_for('settings.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
    return render_template('settings/account.html', form=form)


@settings.route(f'/{settings.name}/system')
def system():
    return render_template('settings/system.html')


@settings.route(f'/{settings.name}/plugins')
def plugins():
    return render_template('settings/plugins.html')


@settings.route(f'/{settings.name}/processes')
def processes():
    return render_template('settings/processes.html')


@settings.route(f'/{settings.name}/credentials', methods=['GET', 'POST'])
def credentials():
    locked = credentials_locked()
    if locked:
        form = UnlockCredentialStore
    else:
        form = LockCredentialStore
    credential_groups = get_all_credential_groups()

    action_menu_list = {
        '1': [
            {'action_name': 'Delete', 'action': 'delete', 'icon': ''}
            ]
        }
    return render_template(
        'settings/credentials.html',
        credential_database_locked=locked,
        form=form,
        credential_groups=credential_groups,
        action_menu_list=action_menu_list)


@settings.route(f'/{settings.name}/credentials/_get_item_info')
def get_item_info():
    info_dict = {}
    group_id = request.args.get('id', 0, type=int)
    group = CredentialGroup.query.filter_by(id=group_id).first()
    credential_list = get_group_credentials(group_id)
    info_dict["group_id"] = group_id
    info_dict["description"] = group.description
    info_dict["service_name"] = group.service_name
    info_dict["time_added"] = group.time_added
    info_dict["credentials"] = []
    for cred in credential_list:
        info_dict["credentials"].append(
            dict(role=cred.credential_role, data=cred.credential_data))

    # return jsonify(info=info_dict)
    # return json.dumps(info_dict)
    return render_template("sidebar/credentials.html", info_dict=info_dict)


@settings.route(f'/{settings.name}/credentials/_delete', methods=['POST'])
def delete_groups():
    group_id_list = request.get_json().get('group_ids')
    for group_id in group_id_list:
        remove_credentials(group_id)
        # logger.debug(group_id)
    flash("Successfully removed items ayylmao", category="success")
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}