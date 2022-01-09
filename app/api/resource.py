from app.api import bp
from flask import jsonify, current_app
from app.modules.resource.models import Resource
from flask import url_for
from app import db
from app.api.errors import bad_request
from flask import request
from app.api.auth import token_auth
from app.main.models import Audit


@bp.route('/resource/add', methods=['POST'])
@token_auth.login_required
def create_resource():
    data = request.get_json() or {}

    if 'serial' not in data:
        return bad_request('must include field: serial')

    hsm_pci_card = Resource.query.filter_by(serial=data['serial']).first()
    if hsm_pci_card is not None:
        msg = 'Card already exist: %s' % hsm_pci_card.id
        return bad_request(msg)

    resource = Resource()
    status = resource.from_dict(data)
    if status['success'] is False:
        return bad_request(status['msg'])

    db.session.add(resource)
    db.session.commit()

    Audit().auditlog_new_post('hsm_pci_card', original_data=resource.to_dict(), record_name=resource.name)

    response = jsonify(resource.to_dict())

    response.status_code = 201
    response.headers['Resource'] = url_for('api.get_resource', id=resource.id)
    return response


@bp.route('/resource/list', methods=['GET'])
@token_auth.login_required
def get_resourcelist():

    resources = Resource.query.all()

    data = {
        'items': [(item.id, item.keysn) for item in resources],
    }
    return jsonify(data)


@bp.route('/resource/<int:id>', methods=['GET'])
@token_auth.login_required
def get_resource(id):
    return jsonify(Resource.query.get_or_404(id).to_dict())


@bp.route('/resource/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_resource(id):
    resource = Resource.query.get_or_404(id)
    original_data = resource.to_dict()

    data = request.get_json() or {}
    resource.from_dict(data)
    db.session.commit()

    Audit().auditlog_update_post('hsm_pci_card', original_data=original_data, updated_data=data, record_name=resource.name)

    return jsonify(resource.to_dict())
