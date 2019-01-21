from flask import render_template, Blueprint

main = Blueprint('main', '__name__')


@main.route('/')
@main.route('/dashboard')
@main.route('/home')
def home():
    return render_template('main.html')
