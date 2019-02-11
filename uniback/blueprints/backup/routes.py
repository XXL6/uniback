from flask import render_template, Blueprint
import logging

backup = Blueprint('backup', '__name__')
logger = logging.getLogger('mainLogger')


@backup.route(f'/{backup.name}/saved_jobs')
def saved_jobs():
    return render_template('backup/saved_jobs.html')


@backup.route(f'/{backup.name}/job_history')
def job_history():
    return render_template('backup/job_history.html')


@backup.route(f'/{backup.name}/backup_sets')
def backup_sets():
    return render_template('backup/backup_sets.html')