from app import db
from datetime import datetime


class Resource(db.Model):
    __tablename__ = "resource"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140), unique=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    service = db.relationship('Service')
    external_id = db.Column(db.String(140))
    environment = db.Column(db.String(140))
    comment = db.Column(db.String(2000))
  
    def __repr__(self):
        return '<Switch {} ({})>'.format(self.name, self.alias)

    def inventory_id(self):
        return '{}-{}'.format(self.__class__.__name__.lower(), self.id)

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'service_id': self.service_id,
            'external_id': self.external_id,
            'environment': self.environment,
            'comment': self.comment,
            }
        return data

    def from_dict(self, data, new_work=False):
        from app.models import Service

        for field in ['name', 'comment', 'external_id', 'environment']:
            if field not in data:
                return {'msg': "must include field: %s" % field, 'success': False}
            else:
                setattr(self, field, data[field])

        if 'service_id' in data:
            service = Service.query.get(data['service_id'])
        elif 'service_name' in data:
            service = Service.query.filter_by(name=data['service_name']).first()

        if service is None:
            return {'msg': "no service found via service_name nor id", 'success': False}
        else:
            setattr(self, 'service_id', service.id)

        return {'msg': "object loaded ok", 'success': True}
