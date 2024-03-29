from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, DateTimeField
from wtforms.validators import DataRequired
from flask_babel import lazy_gettext as _l
from datetime import datetime
from app.main.models import User
from app.modules.resource.models import Resource
from dateutil.relativedelta import relativedelta


class AccessForm(FlaskForm):
    user = SelectField(_l('User'), coerce=int)
    resource = SelectField(_l('Resource'), coerce=int)
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
        self.resource.choices = [(r.id, r.name)
                                 for r in Resource.query.order_by(Resource.name).all()]


class ImplementAccessForm(FlaskForm):
    user = StringField(_l('User'), render_kw={'readonly': True})
    resource = StringField(_l('Resource'), render_kw={'readonly': True})
    start = DateTimeField(_l('Start'),  render_kw={'readonly': True})
    stop = DateTimeField(_l('Stop'),  render_kw={'readonly': True})
    requestor = StringField(_l('Requested by'),  render_kw={'readonly': True})
    request_ts = DateTimeField(
        _l('Requested At'),  render_kw={'readonly': True})
    approver = StringField(_l('Approved by'),  render_kw={'readonly': True})
    approve_ts = DateTimeField(
        _l('Approved At'),  render_kw={'readonly': True})
    comment = TextAreaField(_l('Comment'))

    approve = SubmitField(_l('Approve'))
    deny = SubmitField(_l('Deny'))
    postpone = SubmitField(_l('Postpone'))
    logs = SubmitField(_l('Logs'))
    view_resource = SubmitField(_l('Resouce'))
    view_user = SubmitField(_l('User'))
