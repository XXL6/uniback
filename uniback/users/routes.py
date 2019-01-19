from flask import Blueprint, redirect, url_for, flash, render_template
from flask_login import login_user, current_user, logout_user, login_required
from uniback.users.forms import LoginForm, UpdateAccountForm
from uniback.users.models import User
from uniback import bcrypt, db

users = Blueprint('users', '__name__')


@users.route('/login', methods={'GET', 'POST'})
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('main.home'))
        else:
            flash('No user with such name', 'danger')
    return render_template('login.html', form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect('users.login')


@users.route("/account", methods=['GET', 'POST'])
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
        return redirect(url_for('main.home'))
    return render_template('account.html', form=form)
