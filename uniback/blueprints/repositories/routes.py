from flask import Blueprint, render_template, request, flash, redirect, url_for, Response
from uniback.db_interfaces.physical_location import get_physical_locations, delete_location, set_location_info, set_location_type, get_location_status, get_location_types, get_location_type
from uniback.db_interfaces.physical_location import get_location_info as get_loc_info, add_location as add_loc, add_location_type as add_loc_type, delete_location_type as del_location_type
import uniback.db_interfaces.repository_list as repository_interface
from uniback.models.general import PhysicalLocation, PhysicalLocationType, Repository
import json
from .forms import EditLocationForm, AddLocationForm, AddRepositoryForm, get_add_repository_form, AddLocationTypeForm, EditLocationTypeForm
from uniback.tools import plugin_tools
from uniback.misc import job_queue
from uniback.tools.job_tools import JobObject
from time import sleep
from threading import Thread

repositories = Blueprint('repositories', '__name__')


@repositories.route(f'/{repositories.name}')
@repositories.route(f'/{repositories.name}/repository_list')
def repository_list():
    page = request.args.get('page', 1, type=int)
    repositories = Repository.query.paginate(page=page, per_page=50)
    return render_template('repositories/repository_list.html', repositories=repositories)


@repositories.route(f'/{repositories.name}/repository_list/_get_repository_info')
def get_repository_info():
    info_dict = {}
    repository_id = request.args.get('id', 0, type=int)
    info_dict = repository_interface.get_info(repository_id)
    return render_template('sidebar/repository_list.html', info_dict=info_dict)


@repositories.route(f'/{repositories.name}/physical_locations')
def physical_locations():
    page = request.args.get('page', 1, type=int)
    locations = PhysicalLocation.query.paginate(page=page, per_page=50)
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
    form.type.choices = [(item['id'], item['name']) for item in get_location_types()]
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
    form.type.choices = [(item['id'], item['name']) for item in get_location_types()]
    if form.validate_on_submit():
        new_info = {}
        new_info['name'] = form.name.data
        new_info['address'] = form.address.data
        new_info['type'] = form.type.data
        new_info['concurrent_jobs'] = form.concurrent_jobs.data
        add_loc(new_info)
        flash("Location has been added", category='success')
        return redirect(url_for('repositories.physical_locations'))
    elif request.method == 'GET':
        form.concurrent_jobs.data = 1
    # we can use the same template as it's just going to be the same fields
    # as the fields in the edit form
    return render_template("repositories/physical_locations_edit.html", form=form)


@repositories.route(f'/{repositories.name}/physical_locations/_get_location_status')
def get_loc_status():
    location_id = request.args.get('id', 0, type=int)
    status = get_location_status(location_id)
    return json.dumps({'data': status, 'name': 'status', 'id': location_id})


@repositories.route(f'/{repositories.name}/repository_list/_add/<string:engine>', methods=['GET', 'POST'])
def add_repository(engine):
    form = AddRepositoryForm()
    repository_class = plugin_tools.get_engine_class(engine, 'Repository')
    # form.set_field_list(repository_class.fields_request())
    form = get_add_repository_form(repository_class.fields_request())
    form.location.choices = [(item['id'], item['name']) for item in get_physical_locations(get_status=True) if (item['status'] == 'Online')]
    if form.validate_on_submit():
        new_info = {}
        for item in form:
            if item.id != 'csrf_token' and item.id != 'submit':
                new_info[item.id] = item.data
        job_class = plugin_tools.get_engine_class(engine, 'Repository')
        new_object = job_class(address=get_loc_info(form.location.data).get('address'), field_dict=new_info)
        job_object = JobObject(name="Repository create", process=new_object, engine=engine)
        job_queue.add(job=job_object)
        flash("Repository job added to queue", category='success')
        return redirect(url_for('repositories.repository_list'))
    return render_template("repositories/repository_list_add.html", form=form)


@repositories.route(f'/{repositories.name}/repository_list/_add', methods=['GET', 'POST'])
def get_engine():
    if request.method == 'POST':
        engine = request.form['engine-select']
        return redirect(url_for('repositories.add_repository', engine=engine))
    available_engines = plugin_tools.get_list_of_engines()
    return render_template("repositories/repository_list_add.html", available_engines=available_engines)


@repositories.route(f'/{repositories.name}/physical_location_types/_add', methods=['GET', 'POST'])
def add_location_type():
    form = AddLocationTypeForm()
    if form.validate_on_submit():
        new_info = {}
        new_info['name'] = form.name.data
        new_info['subtype'] = form.subtype.data
        new_info['description'] = form.description.data
        add_loc_type(new_info)
        flash("Location has been added", category='success')
        return redirect(url_for('repositories.physical_location_types'))
    # we can use the same template as it's just going to be the same fields
    # as the fields in the edit form
    return render_template("repositories/physical_location_types_edit.html", form=form)


@repositories.route(f'/{repositories.name}/physical_location_types')
def physical_location_types():
    page = request.args.get('page', 1, type=int)
    items = PhysicalLocationType.query.order_by(PhysicalLocationType.name.desc()).paginate(page=page, per_page=50)
    # we can use the same template as it's just going to be the same fields
    # as the fields in the edit form
    return render_template("repositories/physical_location_types.html", items=items)


@repositories.route(f'/{repositories.name}/physical_location_types/_edit/<int:type_id>', methods=['GET', 'POST'])
def edit_location_type(type_id):
    form = EditLocationTypeForm()
    if form.validate_on_submit():
        new_info = {}
        new_info['name'] = form.name.data
        new_info['subtype'] = form.subtype.data
        new_info['description'] = form.description.data
        set_location_type(type_id, new_info)
        flash("Location type has been updated", category='success')
        return redirect(url_for('repositories.physical_location_types'))
    else:
        type = get_location_type(type_id)
        if type:
            form.name.data = type['name']
            form.subtype.data = type['subtype']
            form.description.data = type['description']
    # we can use the same template as it's just going to be the same fields
    # as the fields in the edit form
    return render_template("repositories/physical_location_types_edit.html", form=form)


@repositories.route(f'/{repositories.name}/physical_location_types/_get_type_info')
def get_type_info():
    info_dict = {}
    location_id = request.args.get('id', 0, type=int)
    info_dict['description'] = get_location_type(location_id)['description']
    return render_template('sidebar/physical_location_types.html', info_dict=info_dict)


@repositories.route(f'/{repositories.name}/physical_location_types/_delete', methods=['POST'])
def delete_location_types():
    type_list = request.get_json().get('item_ids')
    for type in type_list:
        del_location_type(type)
        # logger.debug(group_id)
    flash("Successfully removed items", category="success")
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}