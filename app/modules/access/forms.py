from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField
from wtforms.fields.html5 import DateTimeField
from wtforms.validators import DataRequired
from flask_babel import lazy_gettext as _l
from datetime import datetime
from app.models import User
# from app.modules.access.models import Access
# from app.modules.resource.models import Resouce
from app.modules.role.models import Role


class AccessForm(FlaskForm):
    user = SelectField(_l('User'), coerce=int)
    role = SelectField(_l('Role'), coerce=int)
    start = DateTimeField(_l('Start'), validators=[DataRequired()],
                                  format='%Y-%m-%d', default=datetime.now())
    stop = DateTimeField(_l('Stop'),
                                validators=[DataRequired()], format='%Y-%m-%d',
                                default=datetime.now())
    comment = TextAreaField(_l('Comment'))
    submit = SubmitField(_l('Submit'))
    cancel = SubmitField(_l('Cancel'))
    delete = SubmitField(_l('Delete'))
    logs = SubmitField(_l('Logs'))
    ports = SubmitField(_l('SwitchPorts'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user.choices = [(u.id, u.username) for u in User.query.order_by(User.username).all()]
        self.role.choices = [(r.id, r.name) for r in Role.query.order_by(Role.name).all()]
