from flask import render_template, Blueprint, url_for
from flask_login import login_required, current_user

main = Blueprint('main', '__name__')


@main.route('/dashboard')
@main.route('/home')
#@login_required
def home():
    return render_template('main.html')

