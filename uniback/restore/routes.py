from flask import render_template, Blueprint

restore = Blueprint('restore', '__name__')


@restore.route(f'/{restore.name}/repositories')
def repositories():
    return render_template('restore/repositories.html')
