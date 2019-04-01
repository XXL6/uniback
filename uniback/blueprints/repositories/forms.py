from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, ValidationError, \
    SelectField, TextAreaField
from uniback.tools.local_session import LocalSession
from uniback.models.general import PhysicalLocation
from uniback.db_interfaces.physical_location import get_physical_locations
from wtforms.validators import DataRequired


class EditLocationForm(FlaskForm):
    name = StringField('Name')
    address = StringField('Address')
    type = SelectField('Type', coerce=int)
    concurrent_jobs = IntegerField('Concurrent Jobs')
    submit = SubmitField('Submit')

    def validate_name(self, name):
        with LocalSession() as session:
            location = session.query(PhysicalLocation).filter_by(name=name.data).first()
            if location:
                raise ValidationError(f"Location with name {name.data} already exists. Please pick a different name.")


class AddLocationForm(FlaskForm):
    name = StringField('Name')
    address = StringField('Address')
    type = SelectField('Type', coerce=int)
    concurrent_jobs = IntegerField('Concurrent Jobs')
    submit = SubmitField('Submit')

    def validate_name(self, name):
        with LocalSession() as session:
            location = session.query(PhysicalLocation).filter_by(name=name.data).first()
            if location:
                raise ValidationError(f"Location with name {name.data} already exists. Please pick a different name.")


class AddLocationTypeForm(FlaskForm):
    name = StringField('Name')
    subtype = StringField('SubType')
    description = TextAreaField('Description')
    submit = SubmitField('Submit')

    def validate_name(self, name):
        with LocalSession() as session:
            location = session.query(PhysicalLocation).filter_by(name=name.data).first()
            if location:
                raise ValidationError(f"Location with name {name.data} already exists. Please pick a different name.")


class EditLocationTypeForm(FlaskForm):
    name = StringField('Name')
    subtype = StringField('SubType')
    description = TextAreaField('Description')
    submit = SubmitField('Submit')
    
    def validate_name(self, name):
        with LocalSession() as session:
            location = session.query(PhysicalLocation).filter_by(name=name.data).first()
            if location:
                raise ValidationError(f"Location with name {name.data} already exists. Please pick a different name.")


class AddRepositoryForm(FlaskForm):
    location = SelectField("Location", coerce=int)
    ub_name = StringField("Internal Name")
    ub_description = TextAreaField("Internal Description")
    submit = SubmitField("Submit")


# we need a separate form generator in order to create the forms dynamically
def get_add_repository_form(field_list):
    class F(AddRepositoryForm):
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
