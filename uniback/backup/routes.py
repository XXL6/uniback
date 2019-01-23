from flask import render_template, Blueprint

backup = Blueprint('backup', '__name__')


@backup.route(f'/{backup.name}/job_queue')
def job_queue():
    return render_template('backup/job_queue.html')

@backup.route(f'/{backup.name}/saved_jobs')
def saved_jobs():
    return render_template('backup/saved_jobs.html')

@backup.route(f'/{backup.name}/job_history')
def job_history():
    return render_template('backup/job_history.html')