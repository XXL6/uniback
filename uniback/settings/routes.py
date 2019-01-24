from flask import Blueprint, render_template

settings = Blueprint('settings', '__name__')

@settings.route('/settings')
@settings.route('/settings/account')
def account():
    return render_template('settings/account.html')

@settings.route('/settings/system')
def system():
    return render_template('settings/system.html')