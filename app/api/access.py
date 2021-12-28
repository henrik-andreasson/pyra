from app.api import bp
from flask import jsonify
from app.modules.access.models import Access
from flask import url_for
from app import db, audit
from app.api.errors import bad_request
from flask import request
from app.api.auth import token_auth


@bp.route('/access/add', methods=['POST'])
@token_auth.login_required
def create_access():
    data = request.get_json() or {}
    for field in ['name', 'status']:
        if field not in data:
            return bad_request('must include %s fields' % field)

    check_access = Access.query.filter_by(name=data['name']).first()
    if check_access is not None:
        return bad_request('Access already exist with id: %s' % check_access.id)

    access = Access()
    access.from_dict(data)

    db.session.add(access)
    db.session.commit()
    audit.auditlog_new_post('access', original_data=access.to_dict(), record_name=access.name)

    response = jsonify(access.to_dict())

    response.status_code = 201
    response.headers['Location'] = url_for('api.get_access', id=access.id)
    return response


@bp.route('/accesslist', methods=['GET'])
@token_auth.login_required
def get_accesslist():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = Access.to_collection_dict(Access.query, page, per_page, 'api.get_access')
    return jsonify(data)


@bp.route('/access/<int:id>', methods=['GET'])
@token_auth.login_required
def get_access(id):
    return jsonify(Access.query.get_or_404(id).to_dict())


@bp.route('/access/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_access(id):
    access = Access.query.get_or_404(id)
    original_data = access.to_dict()

    data = request.get_json() or {}
    access.from_dict(data, new_access=False)
    db.session.commit()
    audit.auditlog_update_post('access', original_data=original_data, updated_data=access.to_dict(), record_name=access.hostname)

    return jsonify(access.to_dict())
