from app import db
from datetime import datetime


class Access(db.Model):
    __tablename__ = "access"
    id = db.Column(db.Integer, primary_key=True)
    user = db.relationship('User')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    resource = db.relationship('Resource')
    resource_id = db.Column(db.Integer, db.ForeignKey('resource.id'))
    from app.modules.assignment.models import Assignment
    assignment = db.relationship('Assignment')
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'))
    status = db.Column(db.String(140))
    requestor = db.Column(db.String(140))
    approver = db.Column(db.String(140))
    implementer = db.Column(db.String(140))
    request_ts = db.Column(db.DateTime)
    approve_ts = db.Column(db.DateTime)
    implement_ts = db.Column(db.DateTime)
    start = db.Column(db.DateTime)
    stop = db.Column(db.DateTime)
    comment = db.Column(db.String(2000))

    def __repr__(self):
        return '<Access {} ({})>'.format(self.user.username, self.resource.name)

    def inventory_id(self):
        return '{}-{}'.format(self.__class__.__name__.lower(), self.id)

    def to_dict(self):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'resource_id': self.resource_id,
            'status': self.status,
            'start': self.start,
            'stop': self.stop,
            'comment': self.comment,
            }
        return data

    def from_dict(self, data, new_work=False):
        for field in ['user_id', 'resource_id', 'status', 'comment',
                      'start', 'stop']:
            if field == "start" or field == "stop":
                date = datetime.strptime(data[field], "%Y-%m-%d")
                setattr(self, field, date)
            else:
                setattr(self, field, data[field])
