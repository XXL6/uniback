from flask import Blueprint, render_template

repositories = Blueprint('repositories', '__name__')


@repositories.route(f'/{repositories.name}')
@repositories.route(f'/{repositories.name}/repository_list')
def repository_list():
    return render_template('repositories/repository_list.html')
