from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, DateTimeField
from wtforms.validators import DataRequired
from flask_babel import lazy_gettext as _l
from datetime import datetime
from app.main.models import Service
from app.modules.resource.models import Resource


class ResourceForm(FlaskForm):
    name = StringField(_l('Name'), validators=[DataRequired()])
    service = SelectField(_l('Service'), coerce=int)
    environment = SelectField(_l('Environment'), choices=[('not-applicable', 'Not Applicable'),
                                                          ('physical', 'Physical'),
                                                          ('dev', 'Development'),
                                                          ('tools', 'Tools'),
                                                          ('cicd', 'CI/CD'),
                                                          ('st', 'System Testing'),
                                                          ('at', 'Acceptance Testing'),
                                                          ('prod', 'Production'),
                                                          ])
    external_id = StringField(_l('External ID'))
    comment = TextAreaField(_l('Comment'))

    submit = SubmitField(_l('Submit'))
    cancel = SubmitField(_l('Cancel'))
    delete = SubmitField(_l('Delete'))
    logs = SubmitField(_l('Logs'))
    role = SubmitField(_l('Role'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service.choices = [(s.id, s.name) for s in Service.query.order_by(Service.name).all()]
