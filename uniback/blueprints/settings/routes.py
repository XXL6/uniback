from flask import Blueprint, render_template, flash, redirect, \
    url_for, request
from flask_login import login_required, current_user
from .forms import UpdateAccountForm, UnlockCredentialStoreForm, \
    EditCredentialsForm, DecryptCredentialStoreForm, EncryptCredentialStoreForm
from uniback import bcrypt, db, process_manager
from uniback.misc import credential_manager
from uniback.models.general import CredentialGroup
# from uniback.tools.credential_tools import credentials_locked, \
#    get_all_credential_groups, get_group_credentials, remove_credentials, \
#    set_crypt_key
import logging
import json
import traceback

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
    process_list = process_manager.get_process_list()
    return render_template('settings/processes.html', processes=process_list)


@settings.route(f'/{settings.name}/processes/_get_process_info')
def get_process_info():
    info_dict = {}
    process_id = request.args.get('id', 0, type=int)
    info_dict['description'] = process_manager.get_description(process_id)
    return render_template('sidebar/processes.html', info_dict=info_dict)


@settings.route(f'/{settings.name}/credentials', methods=['GET', 'POST'])
def credentials():
    locked = credential_manager.credentials_locked()
    encrypted = credential_manager.credentials_encrypted()
    credential_groups = credential_manager.get_all_credential_groups()
    return render_template(
        'settings/credentials.html',
        credential_database_locked=locked,
        credential_database_encrypted=encrypted,
        credential_groups=credential_groups)


@settings.route(f'/{settings.name}/credentials/_encrypt_credentials', methods=['GET', 'POST'])
def encrypt_credentials():
    form = EncryptCredentialStoreForm()
    if form.validate_on_submit():
        try:
            credential_manager.encrypt_credentials(form.password.data)
        except Exception:
            flash("Failed to encrypt credentials")
            logger.error(traceback.format_exc())
        return redirect(url_for('settings.credentials'))
    return render_template(
        'settings/credentials_encrypt.html',
        form=form
    )


@settings.route(f'/{settings.name}/credentials/_decrypt_credentials', methods=['GET', 'POST'])
def decrypt_credentials():
    form = DecryptCredentialStoreForm()
    if form.validate_on_submit():
        try:
            credential_manager.decrypt_credentials()
        except Exception as e:
            flash("Failed to decrypt credentials")
            logger.error(e)
        return redirect(url_for('settings.credentials'))
    return render_template(
        'settings/credentials_decrypt.html',
        form=form
    )


@settings.route(f'/{settings.name}/credentials/_unlock_credentials', methods=['GET', 'POST'])
def unlock_credentials():
    form = UnlockCredentialStoreForm()
    if form.validate_on_submit():
        try:
            credential_manager.unlock_credentials(form.password.data)
        except Exception:
            flash("Failed to unlock credentials")
            logger.error(traceback.format_exc())
        return redirect(url_for('settings.credentials'))
    return render_template(
        'settings/credentials_unlock.html',
        form=form
    )


@settings.route(f'/{settings.name}/credentials/_lock_credentials', methods=['GET', 'POST'])
def lock_credentials():
    try:
        credential_manager.lock_credentials()
    except Exception:
        logger.error(traceback.format_exc())
        flash("Failed to lock credentials")
    return redirect(url_for('settings.credentials'))

@settings.route(f'/{settings.name}/credentials/_get_item_info')
def get_item_info():
    info_dict = {}
    group_id = request.args.get('id', 0, type=int)
    group = CredentialGroup.query.filter_by(id=group_id).first()
    credential_list = credential_manager.get_group_credentials(group_id)
    info_dict["group_id"] = group_id
    info_dict["description"] = group.description
    info_dict["service_name"] = group.service_name
    info_dict["time_added"] = group.time_added
    info_dict["credentials"] = []
    for cred in credential_list:
        info_dict["credentials"].append(
            dict(role=cred['credential_role'], data=cred['credential_data']))

    # return jsonify(info=info_dict)
    # return json.dumps(info_dict)
    return render_template("sidebar/credentials.html", info_dict=info_dict)


@settings.route(f'/{settings.name}/credentials/_delete', methods=['POST'])
def delete_groups():
    group_id_list = request.get_json().get('item_ids')
    for group_id in group_id_list:
        credential_manager.remove_credentials(group_id)
        # logger.debug(group_id)
    flash("Successfully removed items", category="success")
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@settings.route(f'/{settings.name}/credentials/_edit/<int:group_id>', methods=['GET', 'POST'])
def edit_group(group_id):
    credentials = credential_manager.get_group_credentials(group_id)
    credential_list = []
    for credential in credentials:
        credential_list.append({'credential_role': credential['credential_role']})
    # credential_list = [{'credential': 't4estthingy'}]
    form = EditCredentialsForm(group_credentials=credential_list)
    for credential_form in form.group_credentials:
        credential_form.credential.label.text = credential_form.credential_role.data
    # for credential in credentials:
    #    form.append_field("test", "testy")
    # form = EditCredentialsForm()
    # for credential in credentials:
    #    form.add_field(credential.credential_role, 'testdata')
    # for credential_form in form.group_credentials:
    #    credential_form.credential.label.text
    if form.validate_on_submit():
        credential_manager.set_group_description(group_id, form.group_description.data)
        for credential_form in form.group_credentials:
            credential_manager.set_credential(group_id, credential_form.credential_role.data,
                                              credential_form.credential.data)
        flash("Credentials have been updated", 'success')
        return redirect(url_for('settings.credentials'))
    elif request.method == 'GET':
        form.group_description.data = credential_manager.get_group_description(group_id)
        for credential_form in form.group_credentials:
            # logger.debug("LABEL" + str(credential_form.credential.label.text))
            credential_form.credential.data = credential_manager.get_credential(group_id, credential_form.credential_role.data)
            # logger.debug("DATA" + str(credential_form.credential.data))
        
    return render_template("settings/credentials_edit.html", form=form)