from flask import Blueprint, render_template

jobs = Blueprint('jobs', '__name__')


@jobs.route(f'/{jobs.name}/')
@jobs.route(f'/{jobs.name}/job_queue')
def job_queue():
    return render_template('jobs/job_queue.html')
