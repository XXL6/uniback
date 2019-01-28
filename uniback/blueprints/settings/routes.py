from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from .forms import UpdateAccountForm
from uniback import bcrypt, db

settings = Blueprint('settings', '__name__')


@settings.route(f'/{settings.name}', methods=['GET', 'POST'])
@settings.route(f'/{settings.name}/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        if form.password.data is not "":
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            current_user.password = hashed_password
        db.session.commit()
        flash("Account information has been updated", 'success')
        return redirect(url_for('settings.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
    return render_template('settings/account.html', form=form)


@settings.route(f'/{settings.name}/system')
def system():
    return render_template('settings/system.html')


@settings.route(f'/{settings.name}/plugins')
def plugins():
    return render_template('settings/plugins.html')
