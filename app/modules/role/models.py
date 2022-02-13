from app import db
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

resource_role = db.Table('resource_role',
                         db.Column('role_id', db.Integer,
                                   db.ForeignKey('role.id')),
                         db.Column('resource_id', db.Integer,
                                   db.ForeignKey('resource.id'))
                         )


class Role(db.Model):
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140), unique=True)
    resources = db.relationship('Resource', secondary=resource_role)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    service = db.relationship('Service')
    status = db.Column(db.String(20))
    description = db.Column(db.TEXT)
    comment = db.Column(db.String(255))

    def __repr__(self):
        return '<Safe {}>'.format(self.name)

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            'service_id': self.service_id,
            'description': self.description,
            'comment': self.comment
            }
        return data

    def from_dict(self, data, new_work=False):

        for field in ['name', 'status', 'comment']:
            if field in data:
                setattr(self, field, data[field])

    def inventory_id(self):
        return '{}-{}'.format(self.__class__.__name__.lower(), self.id)
