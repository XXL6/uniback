from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, ValidationError, \
    SelectField, TextAreaField
from wtforms.validators import DataRequired


class AddJobForm(FlaskForm):
    ub_name = StringField('Job Name', validators=[DataRequired()])
    ub_description = TextAreaField('Description')
    submit = SubmitField('Submit')


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

    return F()
