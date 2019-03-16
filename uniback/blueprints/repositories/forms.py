from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, ValidationError, \
    SelectField
from uniback.tools.local_session import LocalSession
from uniback.models.general import PhysicalLocation
from uniback.db_interfaces.physical_location import get_physical_locations
import copy


class EditLocationForm(FlaskForm):
    name = StringField('Name')
    address = StringField('Address')
    type = StringField('Type')
    concurrent_jobs = IntegerField('Concurrent Jobs')
    submit = SubmitField('Submit')


class AddLocationForm(FlaskForm):
    name = StringField('Name')
    address = StringField('Address')
    type = StringField('Type')
    concurrent_jobs = IntegerField('Concurrent Jobs')
    submit = SubmitField('Submit')

    def validate_name(self, name):
        with LocalSession() as session:
            location = session.query(PhysicalLocation).filter_by(name=name.data).first()
            if location:
                raise ValidationError(f"Location with name {name.data} already exists. Please pick a different name.")


class AddRepositoryForm(FlaskForm):
    location = SelectField("Location", coerce=int)
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
            setattr(F, field['name'], StringField(field['label']))
        elif (field['type'] == 'int'):
            setattr(F, field['name'], IntegerField(field['label']))
        elif (field['type'] == 'select'):
            setattr(F, field['name'], SelectField(field['label'], choices=field['values']))
    return F()
