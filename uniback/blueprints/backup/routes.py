from flask import render_template, Blueprint, request, redirect, url_for, flash
import logging
from uniback.dictionary.uniback_constants import BackupSetList
from uniback.db_interfaces.backup_sets import add_backup_set as add_set, get_backup_sets as get_sets, \
    get_backup_set_info as get_set_info
from uniback.db_interfaces.job_history import get_jobs, get_job, delete_jobs
import traceback
from .forms import BackupSetAddForm
import json

backup = Blueprint('backup', '__name__')
logger = logging.getLogger('mainLogger')


@backup.route(f'/{backup.name}/saved_jobs')
def saved_jobs():
    return render_template('backup/saved_jobs.html')


@backup.route(f'/{backup.name}/backup_sets')
def backup_sets():
    items = get_sets()
    return render_template('backup/backup_sets.html', items=items)


@backup.route(f'/{backup.name}/backup_sets/_add/<int:backup_set>', methods=['GET', 'POST'])
def add_backup_set(backup_set):
    # form = get_backup_set_form(backup_set)
    form = BackupSetAddForm()
    if form.validate_on_submit():
        new_info = {}
        new_info['type'] = backup_set
        for item in form:
            if item.id != 'csrf_token' and item.id != 'submit':
                new_info[item.id] = item.data
        try:
            add_set(new_info)
        except Exception:
            flash("Failed to add backup set.", category="danger")
            logger.error("Failed to add backup set.")
            logger.error(traceback.format_exc())
        return redirect(url_for('backup.backup_sets'))
    return render_template("backup/backup_sets_add.html", form=form)


@backup.route(f'/{backup.name}/backup_sets/_add', methods=['GET', 'POST'])
def get_backup_set():
    if request.method == 'POST':
        backup_set = request.form['backup-set-select']
        return redirect(url_for('backup.add_backup_set', backup_set=backup_set))
    available_backup_sets = []
    for key, value in BackupSetList.BACKUP_SETS.items():
        available_backup_sets.append((key, value))
    return render_template("backup/backup_sets_add.html", available_backup_sets=available_backup_sets)


@backup.route(f'/{backup.name}/backup_sets/_get_backup_set_info')
def get_backup_set_info():
    info_dict = {}
    id = request.args.get('id', 0, type=int)
    # info_dict['name'] = get_loc_info(location_id)['name']
    info_dict = get_set_info(id)
    return render_template('sidebar/backup_sets.html', info_dict=info_dict)


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