from flask import Blueprint, render_template, request, flash, redirect, url_for
from uniback.db_interfaces.physical_location import get_physical_locations, delete_location, set_location_info, get_location_status
from uniback.db_interfaces.physical_location import get_location_info as get_loc_info, add_location as add_loc
import json
from .forms import EditLocationForm, AddLocationForm, AddRepositoryForm, get_add_repository_form
from uniback.tools import plugin_tools
from uniback.misc import job_queue
from uniback.tools.job_tools import JobObject

repositories = Blueprint('repositories', '__name__')


@repositories.route(f'/{repositories.name}')
@repositories.route(f'/{repositories.name}/repository_list')
def repository_list():
    return render_template('repositories/repository_list.html')


@repositories.route(f'/{repositories.name}/physical_locations')
def physical_locations():
    locations = get_physical_locations()
    # for location in locations:
    #    location['status'] = get_location_status(location['id'])
    return render_template('repositories/physical_locations.html', locations=locations)


@repositories.route(f'/{repositories.name}/physical_locations/_delete', methods=['POST'])
def delete_locations():
    location_list = request.get_json().get('item_ids')
    for location_id in location_list:
        delete_location(location_id)
        # logger.debug(group_id)
    flash("Successfully removed items", category="success")
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@repositories.route(f'/{repositories.name}/physical_locations/_get_location_info')
def get_location_info():
    info_dict = {}
    location_id = request.args.get('id', 0, type=int)
    info_dict['name'] = get_loc_info(location_id)['name']
    return render_template('sidebar/physical_locations.html', info_dict=info_dict)


@repositories.route(f'/{repositories.name}/physical_locations/_edit/<int:location_id>', methods=['GET', 'POST'])
def edit_location(location_id):
    form = EditLocationForm()
    if form.validate_on_submit():
        new_info = {}
        new_info['name'] = form.name.data
        new_info['address'] = form.address.data
        new_info['type'] = form.type.data
        new_info['concurrent_jobs'] = form.concurrent_jobs.data
        set_location_info(location_id, new_info)
        flash("Location has been updated", 'success')
        return redirect(url_for('repositories.physical_locations'))
    elif request.method == 'GET':
        current_info = get_loc_info(location_id)
        form.name.data = current_info.get('name')
        form.address.data = current_info.get('address')
        form.type.data = current_info.get('type')
        form.concurrent_jobs.data = current_info.get('concurrent_jobs')
    return render_template("repositories/physical_locations_edit.html", form=form)


@repositories.route(f'/{repositories.name}/physical_locations/_add', methods=['GET', 'POST'])
def add_location():
    form = AddLocationForm()
    if form.validate_on_submit():
        new_info = {}
        new_info['name'] = form.name.data
        new_info['address'] = form.address.data
        new_info['type'] = form.type.data
        new_info['concurrent_jobs'] = form.concurrent_jobs.data
        add_loc(new_info)
        flash("Location has been added", 'success')
        return redirect(url_for('repositories.physical_locations'))
    elif request.method == 'GET':
        form.concurrent_jobs.data = 1
    # we can use the same template as it's just going to be the same fields
    # as the fields in the edit form
    return render_template("repositories/physical_locations_edit.html", form=form)


@repositories.route(f'/{repositories.name}/repository_list/_add/<string:engine>', methods=['GET', 'POST'])
def add_repository(engine):
    form = AddRepositoryForm()
    repository_class = plugin_tools.get_engine_class(engine, 'Repository')
    # form.set_field_list(repository_class.fields_request())
    form = get_add_repository_form(repository_class.fields_request())
    form.location.choices = [(item['id'], item['name']) for item in get_physical_locations() if (item['status'] == 'Online')]
    if form.validate_on_submit():
        new_info = {}
        for item in form:
            print(item.id)
            if item.id != 'csrf_token' and item.id != 'submit':
                new_info[item.id] = item.data
        job_class = plugin_tools.get_engine_class(engine, 'Repository')
        new_object = job_class(address=get_loc_info(form.location.data).get('address'), field_dict=new_info)
        job_object = JobObject(form.name.data, new_object)
        job_queue.add(job=job_object)
        flash("Repository job added to queue", 'success')
        return redirect(url_for('repositories.repository_list'))
    return render_template("repositories/repository_list_add.html", form=form)


@repositories.route(f'/{repositories.name}/repository_list/_add', methods=['GET', 'POST'])
def get_engine():
    if request.method == 'POST':
        engine = request.form['engine-select']
        return redirect(url_for('repositories.add_repository', engine=engine))
    available_engines = plugin_tools.get_list_of_engines()
    return render_template("repositories/repository_list_add.html", available_engines=available_engines)