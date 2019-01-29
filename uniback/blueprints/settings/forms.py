from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from uniback.blueprints.users.models import User


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password')
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('password')])
    submit = SubmitField('Submit')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("Username already in user. Choose a different one.")


class UnlockCredentialStore(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


class LockCredentialStore(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password')
    submit = SubmitField('Submit')
