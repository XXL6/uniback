from uniback.dictionary.uniback_constants import BackupSetTypes
from wtforms import StringField, SubmitField, TextField, SelectField,\
    TextAreaField, IntegerField, PasswordField, HiddenField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm


class BSForm0(FlaskForm):
    name = StringField('Name')
    file_list = HiddenField('Files')
    submit = SubmitField('Submit')


class BSForm0Edit(FlaskForm):
    name = StringField('Name')
    file_list = HiddenField('Files')
    source = StringField('Source')
    submit = SubmitField('Submit')


class BackupSetAddForm(FlaskForm):
    name = StringField('Name')
    data = TextField('Data')
    submit = SubmitField('Submit')


class AddJobForm(FlaskForm):
    ub_name = StringField('Job Name', validators=[DataRequired()])
    ub_description = TextAreaField('Description')
    backup_set = SelectField('Backup Set', coerce=int)
    repository = SelectField('Repository', coerce=int)
    submit = SubmitField('Submit')


class UBCredentialField(StringField):
    pass


# we need a separate form generator in order to create the forms dynamically
def get_add_job_form(field_list=[]):
    class F(AddJobForm):
        i = 0
        pass
    # we can assign attributes to this temp class and it won't affect
    # the parent class
    for field in field_list:
        if (field['type'] == 'string'):
            if (field['required']):
                setattr(F, field['name'], StringField(field['label'], [DataRequired()]))
            else:
                setattr(F, field['name'], StringField(field['label']))
        elif (field['type'] == 'int'):
            if (field['required']):
                setattr(F, field['name'], IntegerField(field['label'], [DataRequired()]))
            else:
                setattr(F, field['name'], IntegerField(field['label']))
        elif (field['type'] == 'select'):
            if (field['required']):
                setattr(F, field['name'], SelectField(field['label'], choices=field['values'], validators=[DataRequired()]))
            else:
                setattr(F, field['name'], SelectField(field['label'], choices=field['values']))
        elif (field['type'] == 'text'):
            if (field['required']):
                setattr(F, field['name'], TextAreaField(field['label'], [DataRequired()]))
            else:
                setattr(F, field['name'], TextAreaField(field['label']))
        elif (field['type'] == 'credential'):
            if (field['required']):
                setattr(F, field['name'], UBCredentialField(field['label'], [DataRequired()]))
            else:
                setattr(F, field['name'], UBCredentialField(field['label']))

    return F()


def get_backup_set_form(id):
    if id == 0:
        return BSForm0()


def get_backup_set_edit_form(type):
    if type == BackupSetTypes.BS_TYPE_FILESFOLDERS:
        return BSForm0Edit()
