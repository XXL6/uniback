from flask import Blueprint, render_template

settings = Blueprint('settings', '__name__')


@settings.route(f'/{settings.name}')
@settings.route(f'/{settings.name}/account')
def account():
    return render_template('settings/account.html')


@settings.route(f'/{settings.name}/system')
def system():
    return render_template('settings/system.html')
