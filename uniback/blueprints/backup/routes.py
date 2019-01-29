from flask import render_template, Blueprint
import logging

backup = Blueprint('backup', '__name__')
logger = logging.getLogger('mainLogger')


@backup.route(f'/{backup.name}/saved_jobs')
def saved_jobs():
    return render_template('backup/saved_jobs.html')


@backup.route(f'/{backup.name}/job_history')
def job_history():
    logger.info('entered the job history page')
    return render_template('backup/job_history.html')
