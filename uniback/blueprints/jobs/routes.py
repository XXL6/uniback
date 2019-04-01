from flask import Blueprint, render_template, request, flash, Response, redirect, url_for
from uniback.db_interfaces.job_history import get_jobs, get_job, delete_jobs
from uniback.db_interfaces.saved_jobs import delete_jobs as delete_jobs_s, add_job
from uniback import db
from uniback.misc import job_queue as global_job_queue
from uniback.tools import plugin_tools
from uniback.tools.job_tools import JobObject
from uniback.dictionary.uniback_constants import JobStatusFinishedMap, \
    JobStatusMap
from uniback.models.general import JobQueue, JobHistory, SavedJobs
from .forms import get_add_job_form
import json
from time import sleep

jobs = Blueprint('jobs', '__name__')


@jobs.route(f'/{jobs.name}/')
@jobs.route(f'/{jobs.name}/job_queue')
def job_queue():
    items = global_job_queue.get_job_queue_info()
    for item in items:
        item['status'] = JobStatusMap.JOB_STATUS[item['status']]
    return render_template('jobs/job_queue.html', items=items)


@jobs.route(f'/{jobs.name}/job_queue/_update')
def update_job_queue():
    def update_stream():
        while True:
            job_list = global_job_queue.get_job_queue_info()
            for item in job_list:
                item['status'] = JobStatusMap.JOB_STATUS[item['status']]
                # yield 'data: {' + f'"id": "{item["id"]}", "name": "status", "data": "{global_job_queue.get_job_info(item["id"], 'status')}"' + '}\n\n'
            yield f'data: {json.dumps(job_list)}\n\n'
            sleep(1)
    return Response(update_stream(), mimetype="text/event-stream")


@jobs.route(f'/{jobs.name}/job_queue/_get_job_status')
def get_job_status():
    job_id = request.args.get('id', 0, type=int)
    status = global_job_queue.get_job_info(job_id, 'status')
    if not status:
        return json.dumps({'data': 'deleted', 'name': 'status', 'id': job_id})
    status = JobStatusMap.JOB_STATUS[status]
    return json.dumps({'data': status, 'name': 'status', 'id': job_id})


@jobs.route(f'/{jobs.name}/job_history')
def job_history():
    page = request.args.get('page', 1, type=int)
    items = JobHistory.query.order_by(JobHistory.time_finished.desc()).paginate(page=page, per_page=50)
    for item in items.items:
        item.status = JobStatusFinishedMap.JOB_STATUS_FINISHED[item.status]
    return render_template('jobs/job_history.html', items=items)


@jobs.route(f'/{jobs.name}/job_history/_get_history_info')
def get_history_info():
    id = request.args.get('id', 0, type=int)
    info_dict = JobHistory.query.filter_by(id=id).first()
    if info_dict.log:
        try:
            info_dict.log = json.loads(info_dict.log)
        except json.decoder.JSONDecodeError:
            # if the log is not a list, we just add the whole string
            # to a list so that it's displayed properly
            info_dict.log = [info_dict.log]
    '''
    info_dict = dict(
        name=info_dict.name,
        status=info_dict.status,
        type=info_dict.type,
        log=info_dict.log,
        time_started=info_dict.time_started,
        time_finished=info_dict.time_finished,
        time_elapsed=info_dict.time_elapsed,
        time_added = 
    )
    '''
    return render_template('sidebar/job_history.html', info_dict=info_dict)


@jobs.route(f'/{jobs.name}/job_history/_delete', methods=['POST'])
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


@jobs.route(f'/{jobs.name}/saved_jobs')
def saved_jobs():
    page = request.args.get('page', 1, type=int)
    items = SavedJobs.query.order_by(SavedJobs.name.desc()).paginate(page=page, per_page=50)

    return render_template('jobs/saved_jobs.html', items=items)


@jobs.route(f'/{jobs.name}/saved_jobs/_delete', methods=['POST'])
def delete_saved_jobs():
    item_ids = request.get_json().get('item_ids')
    try:
        delete_jobs_s(item_ids)
    except Exception as e:
        flash("Items not removed", category="danger")
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
        # logger.debug(group_id)
    flash("Successfully removed items", category="success")
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@jobs.route(f'/{jobs.name}/saved_jobs/_get_saved_job_info')
def get_saved_job_info():
    id = request.args.get('id', 0, type=int)
    info_dict = SavedJobs.query.filter_by(id=id).first()
    return render_template('sidebar/saved_jobs.html', info_dict=info_dict)


@jobs.route(f'/{jobs.name}/saved_jobs/_add', methods=['GET', 'POST'])
def add_saved_job():
    form = get_add_job_form()
    form.engine_name.choices = plugin_tools.get_list_of_engines()
    # form.type.choices = [(item['id'], item['name']) for item in get_location_types()]
    if form.validate_on_submit():
        new_info = {}
        new_info['name'] = form.name.data
        new_info['engine_name'] = form.engine_name.data
        new_info['engine_class'] = form.engine_class.data
        add_job(new_info)
        flash("Job has been added", category='success')
        return redirect(url_for('jobs.saved_jobs'))
    elif request.method == 'GET':
        pass
    # we can use the same template as it's just going to be the same fields
    # as the fields in the edit form
    return render_template("jobs/saved_jobs_edit.html", form=form)


@jobs.route(f'/{jobs.name}/saved_jobs/_run_jobs', methods=['GET', 'POST'])
def run_saved_jobs():
    item_ids = request.get_json().get('item_ids')
    for item_id in item_ids:
        job_class = plugin_tools.get_engine_class('testengine', 'Backup')
        new_object = job_class()
        job_object = JobObject(name="Backup TEST", process=new_object, engine='testengine')
        global_job_queue.add(job=job_object)
    flash("Job added to queue", category='success')
    return redirect(url_for('jobs.saved_jobs'))


@jobs.route(f'/{jobs.name}/saved_jobs/_get_engine_classes')
def get_engine_classes():
    engine_name = request.args.get('engine_name', "none", type=str)
    classes = plugin_tools.get_engine_classes(engine_name)
    return json.dumps(classes)
'''
@system.route(f'/{system.name}/processes/_update_queue')
def update_queue():
    def update_stream():
        while True:
            job_list = global_job_queue.get_job_queue_info()
            yield f'data: {json.dumps(job_list)}\n\n'
            sleep(10)
    return Response(update_stream(), mimetype="text/event-stream")
'''