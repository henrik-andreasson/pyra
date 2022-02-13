from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, DateTimeField
from wtforms.validators import DataRequired
from flask_babel import lazy_gettext as _l
from datetime import datetime
from app.main.models import User
# from app.modules.access.models import Access
# from app.modules.resource.models import Resouce
from app.modules.role.models import Role
from dateutil.relativedelta import relativedelta


class AssignmentForm(FlaskForm):
    user = SelectField(_l('User'), coerce=int)
    role = SelectField(_l('Role'), coerce=int)
    start = DateTimeField(_l('Start'), validators=[DataRequired()],
                          format='%Y-%m-%d', default=datetime.now())
    stop = DateTimeField(_l('Stop'),
                         validators=[DataRequired()], format='%Y-%m-%d',
                         default=datetime.now() + relativedelta(years=1))
    comment = TextAreaField(_l('Comment'))
    submit = SubmitField(_l('Submit'))
    cancel = SubmitField(_l('Cancel'))
    delete = SubmitField(_l('Delete'))
    logs = SubmitField(_l('Logs'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user.choices = [(u.id, u.username)
                             for u in User.query.order_by(User.username).all()]
        self.role.choices = [(r.id, r.name)
                             for r in Role.query.order_by(Role.name).all()]


class ApproveAssignmentForm(FlaskForm):
    user = StringField(_l('User'), render_kw={'readonly': True})
    role = StringField(_l('Role'), render_kw={'readonly': True})
    start = DateTimeField(_l('Start'),  render_kw={'readonly': True})
    stop = DateTimeField(_l('Stop'),  render_kw={'readonly': True})
    requestor = StringField(_l('Requested by'),  render_kw={'readonly': True})
    request_ts = DateTimeField(
        _l('Requested At'),  render_kw={'readonly': True})
    comment = TextAreaField(_l('Comment'))
    approve = SubmitField(_l('Approve'))
    deny = SubmitField(_l('Deny'))
    postpone = SubmitField(_l('Postpone'))
    logs = SubmitField(_l('Logs'))
    view_role = SubmitField(_l('Role'))
    view_user = SubmitField(_l('User'))
