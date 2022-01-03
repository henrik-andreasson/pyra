from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, SelectMultipleField, SelectField
from wtforms.validators import DataRequired
from flask_babel import lazy_gettext as _l
from app.modules.role.models import Role
from app.modules.resource.models import Resource
# from app.models import User, Location
from wtforms.widgets import TextArea

class RoleForm(FlaskForm):
    name = StringField(_l('Name'), validators=[DataRequired()])
    resources = SelectMultipleField(_l('Access to Resources'), coerce=int, render_kw={"size": 15})
    description = TextAreaField(_l('Description'), render_kw={'class': 'form-control', 'rows': 30})
    comment = TextAreaField(_l('Comments'))
    submit = SubmitField(_l('Submit'))
    cancel = SubmitField(_l('Cancel'))
    delete = SubmitField(_l('Delete'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resources.choices = [(r.id, r.name) for r in Resource.query.order_by(Resource.name).all()]


class AuditRoleForm(FlaskForm):
    safe = SelectField(_l('Location'), coerce=int)
    comment = TextAreaField(_l('Audit Comment'))
    approved = SubmitField(_l('Audit Approved'))
    failed = SubmitField(_l('Audit Failed'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role.choices = [(r.id, r.name) for r in Role.query.order_by(Role.name).all()]
