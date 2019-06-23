from flask import render_template, Blueprint, request, redirect, url_for, flash
import logging
from uniback.dictionary.uniback_constants import BackupSetList
from uniback.db_interfaces import backup_sets as backup_sets_interface
from uniback.models.general import SavedJobs, JobParameter
from uniback.db_interfaces.job_history import get_jobs, get_job, delete_jobs
import uniback.db_interfaces.saved_backup_jobs as saved_backup_jobs_interface
import uniback.db_interfaces.saved_jobs as saved_jobs_interface
import uniback.db_interfaces.repository_list as repository_interface
import uniback.db_interfaces.backup_sets as backup_sets_interface
from uniback.misc import credential_manager
from uniback.tools import plugin_tools, filesystem_tools
import traceback
import platform
from .forms import BackupSetAddForm, get_add_job_form, get_backup_set_form, get_backup_set_edit_form
import json

backup = Blueprint('backup', '__name__')
logger = logging.getLogger('mainLogger')


@backup.route(f'/{backup.name}/saved_jobs')
def saved_jobs():
    page = request.args.get('page', 1, type=int)
    items = SavedJobs.query.filter_by(engine_class="Backup").order_by(SavedJobs.name.desc()).paginate(page=page, per_page=50)

    return render_template('backup/saved_jobs.html', items=items)


@backup.route(f'/{backup.name}/saved_jobs/_delete', methods=['POST'])
def delete_saved_jobs():
    item_ids = request.get_json().get('item_ids')
    try:
        saved_backup_jobs_interface.delete_jobs(item_ids)
    except Exception as e:
        flash(f"Items not removed: {e}", category="danger")
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
        # logger.debug(group_id)
    flash("Successfully removed items", category="success")
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@backup.route(f'/{backup.name}/saved_jobs/_get_saved_job_info')
def get_saved_job_info():
    info_dict = {}
    id = request.args.get('id', 0, type=int)
    job = SavedJobs.query.filter_by(id=id).first()
    info_dict['name'] = job.name
    info_dict['notes'] = job.notes
    info_dict['engine_name'] = job.engine_name
    info_dict['engine_class'] = job.engine_class
    # info_dict['params'] = job.params
    info_dict['last_attempted_run'] = job.last_attempted_run
    info_dict['last_successful_run'] = job.last_successful_run
    info_dict['time_added'] = job.time_added
    job_params = JobParameter.query.filter_by(job_id=job.id)
    for job_param in job_params:
        info_dict[job_param.param_name] = job_param.param_value
    return render_template('sidebar/saved_jobs.html', info_dict=info_dict)


@backup.route(f'/{backup.name}/saved_jobs/_add', methods=['GET', 'POST'])
def submit_engine_data():

    if request.method == 'POST':
        engine_name = request.form.get('engine-name')
        engine_class = 'Backup'
        return redirect(url_for('backup.add_saved_job', engine_name=engine_name, engine_class=engine_class))

    engines = plugin_tools.get_list_of_engines()
    return render_template('backup/saved_jobs_add.html', engines=engines)


@backup.route(f'/{backup.name}/saved_jobs/_add/<string:engine_name>&<string:engine_class>', methods=['GET', 'POST'])
#@jobs.route(f'/{jobs.name}/saved_jobs/_add?engine=<string:engine_name>', methods=['GET', 'POST'])
def add_saved_job(engine_name, engine_class):
    class_object = plugin_tools.get_engine_class(engine_name, engine_class)
    available_repositories = repository_interface.get_engine_repositories(engine_name)
    if len(available_repositories) < 1:
        available_repositories = [('-1', 'None Available')]
    available_backup_sets = backup_sets_interface.get_backup_sets_tuple()
    if len(available_backup_sets) < 1:
        available_backup_sets = [('-1', 'None Available')]
    class_fields = class_object.fields_request()
    form = get_add_job_form(class_fields)
    form.repository.choices = available_repositories
    form.backup_set.choices = available_backup_sets
    if form.validate_on_submit():
        new_info = {}
        new_info['name'] = form.ub_name.data
        new_info['notes'] = form.ub_description.data
        new_info['engine_name'] = engine_name
        new_info['engine_class'] = engine_class
        param_dict = {}
        credential_dict = {}
        for item in form:
            if item.id != 'csrf_token' and item.id != 'submit' and item.id != 'ub_description' and item.id != 'ub_name':
                if item.type == 'UBCredentialField':
                    credential_dict[item.id] = item.data
                else:
                    param_dict[item.id] = item.data
        if len(credential_dict) > 0:
            credentials_id = credential_manager.add_credentials_from_dict('_'.join(['Job', engine_name, engine_class, form.ub_name.data]), credential_dict)
            param_dict['credentials_id'] = credentials_id
        new_info['params'] = param_dict
        saved_backup_jobs_interface.add_job(new_info)
        flash("Job has been added", category='success')
        return redirect(url_for('backup.saved_jobs'))
    # we can use the same template as it's just going to be the same fields
    # as the fields in the edit form
    return render_template("backup/saved_jobs_add.html", form=form)


@backup.route(f'/{backup.name}/saved_jobs/_run_jobs', methods=['GET', 'POST'])
def run_saved_jobs():
    item_ids = request.get_json().get('item_ids')
    for item_id in item_ids:
        saved_jobs_interface.add_job_to_queue(item_id)
    flash("Job added to queue", category='success')
    return redirect(url_for('backup.saved_jobs'))


@backup.route(f'/{backup.name}/backup_sets')
def backup_sets():
    items = backup_sets_interface.get_backup_sets()
    return render_template('backup/backup_sets.html', items=items)


@backup.route(f'/{backup.name}/backup_sets/_add/<int:backup_set>', methods=['GET', 'POST'])
def add_backup_set(backup_set):
    form = get_backup_set_form(backup_set)
    # form = BackupSetAddForm()
    if form.validate_on_submit():
        new_info = {}
        new_info['type'] = backup_set
        new_info['name'] = form.name.data
        new_info['source'] = platform.node()
        new_info['backup_object_data'] = {}
        for item in form:
            if item.id != 'csrf_token' and item.id != 'submit' and item.id != 'name':
                new_info['backup_object_data'][item.id] = item.data
        try:
            backup_sets_interface.add_backup_set(new_info)
        except Exception as e:
            flash(f"Failed to add backup set. {e}", category="danger")
            logger.error("Failed to add backup set.")
            logger.error(traceback.format_exc())
        return redirect(url_for('backup.backup_sets'))
    return render_template(f"backup/backup_sets_add_{backup_set}.html", form=form)


@backup.route(f'/{backup.name}/backup_sets/_edit/<int:backup_set>', methods=['GET', 'POST'])
def edit_backup_set(backup_set):
    current_info, current_object_list = backup_sets_interface.get_backup_set_info(backup_set)
    form = get_backup_set_edit_form(current_info['type'])
    if form.validate_on_submit():
        pass
    elif request.method == 'GET':
        form.name.data = current_info.get('name')
        form.source.data = current_info.get('source')
        if current_info.get('source') != platform.node():
            current_object_list = -1
            current_info['data'] = -1
        return render_template(f"backup/backup_sets_edit_{current_info.get('type')}.html", form=form, current_object_list=json.dumps(current_object_list), backup_set_data=current_info['data'])


@backup.route(f'/{backup.name}/backup_sets/_add', methods=['GET', 'POST'])
def get_backup_set():
    if request.method == 'POST':
        backup_set = request.form['backup-set-select']
        return redirect(url_for('backup.add_backup_set', backup_set=backup_set))
    available_backup_sets = []
    for key, value in BackupSetList.BACKUP_SETS.items():
        available_backup_sets.append((key, value))
    return render_template("backup/backup_sets_add.html", available_backup_sets=available_backup_sets)


@backup.route(f'/{backup.name}/backup_sets/_delete', methods=['GET', 'POST'])
def delete_backup_set():
    item_ids = request.get_json().get('item_ids')
    try:
        backup_sets_interface.delete_backup_sets(item_ids)
    except Exception as e:
        flash(f"Items not removed: {e}", category="danger")
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
        # logger.debug(group_id)
    flash("Successfully removed items", category="success")
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@backup.route(f'/{backup.name}/backup_sets/_get_backup_set_info')
def get_backup_set_info():
    info_dict = {}
    id = request.args.get('id', 0, type=int)
    # info_dict['name'] = get_loc_info(location_id)['name']
    info_dict, set_items = backup_sets_interface.get_backup_set_info(id)
    return render_template('sidebar/backup_sets.html', info_dict=info_dict, set_items=set_items)


@backup.route(f'/{backup.name}/backup_sets/_get_directory_listing')
def get_directory_listing():
    id = request.args.get('id', "none", type=str)
    #id = id.replace("\|\|", " ")
    path = request.args.get('path', 'none', type=str)
    # if id is # then it means we do not really have anything selected
    # and we can return a list of root nodes
    if id == "#":
        root_nodes = []
        for item in filesystem_tools.get_system_drives():
            root_nodes.append({
                'id': item['device'],
                'parent': '#',
                'text': item['device'].replace('\\', ""),
                'children': True})
        return json.dumps(root_nodes)
    else:
        file_nodes = []
        try:
            for item in filesystem_tools.get_directory_contents(path):
                file_nodes.append({
                    'id': item['path'].replace(" ", ""),
                    'text': item['name'],
                    'children': True if item['is_dir'] else False,
                    'icon': 'jstree-folder' if item['is_dir'] else 'jstree-file'})
            return json.dumps(file_nodes)
        except PermissionError as e:
            return json.dumps({'success': False, 'errormsg': e.strerror}), 500, {'ContentType': 'application/json'}
        # return json.dumps({'id': 'childnode', 'parent': 'rootnode', 'text': 'Simple test child OwO', 'fqpn': 'C:\\Toptest\\Ayylmao'})

@backup.route(f'/{backup.name}/job_history')
def job_history():
    items = get_jobs(type='Backup')
    return render_template('backup/job_history.html', items=items)


@backup.route(f'/{backup.name}/job_history/_get_history_info')
def get_history_info():
    id = request.args.get('id', 0, type=int)
    info_dict = get_job(id)
    return render_template('sidebar/job_history.html', info_dict=info_dict)


@backup.route(f'/{backup.name}/job_history/_delete', methods=['POST'])
def delete_job_history():
    job_list = request.get_json().get('item_ids')
    try:
        delete_jobs(job_list)
    except Exception as e:
        flash("Items not removed", category="danger")
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
        # logger.debug(group_id)
    flash("Successfully removed items", category="success")
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}