from app.api import bp
from flask import jsonify, current_app
from app.modules.role.models import Role
from flask import url_for
from app import db
from app.api.errors import bad_request
from flask import request
from app.api.auth import token_auth
from app.main.models import Audit


@bp.route('/role/add', methods=['POST'])
@token_auth.login_required
def create_role():
    data = request.get_json() or {}
    for field in ['name', 'service_id']:
        if field not in data:
            return bad_request('must include field: %s' % field)

    check_role = Role.query.filter_by(name=data['name']).first()
    if check_role is not None:
        return bad_request('HSM Domain already exist with id: %s' % check_role.id)

    role = Role()
    role.from_dict(data)

    db.session.add(role)
    db.session.commit()

    Audit().auditlog_new_post('hsm_domain', original_data=role.to_dict(), record_name=role.name)

    response = jsonify(role.to_dict())

    response.status_code = 201
    response.headers['Role'] = url_for('api.get_role', id=role.id)
    return response


@bp.route('/role/list', methods=['GET'])
@token_auth.login_required
def get_rolelist():

    roles = Role.query.all()

    data = {
        'items': [(item.id,) for item in roles],
    }
    return jsonify(data)


@bp.route('/role/<int:id>', methods=['GET'])
@token_auth.login_required
def get_role(id):
    return jsonify(Role.query.get_or_404(id).to_dict())


@bp.route('/role/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_role(id):
    role = Role.query.get_or_404(id)
    original_data = role.to_dict()
    data = request.get_json() or {}
    role.from_dict(data, new_role=False)
    db.session.commit()
    Audit().auditlog_update_post('hsm_domain', original_data=original_data, updated_data=data)

    return jsonify(role.to_dict())
