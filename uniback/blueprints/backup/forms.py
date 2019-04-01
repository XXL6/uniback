from uniback.dictionary.uniback_constants import BackupSetTypes
from wtforms import StringField, SubmitField, TextField
from flask_wtf import FlaskForm


class BSForm0(FlaskForm):
    name = StringField('Name')
    folder_list = StringField('Folders')
    submit = SubmitField('Submit')


class BackupSetAddForm(FlaskForm):
    name = StringField('Name')
    data = TextField('Data')
    submit = SubmitField('Submit')


def get_backup_set_form(id):
    if id == 0:
        return BSForm0()
