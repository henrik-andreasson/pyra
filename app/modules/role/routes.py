from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from app import db
from app.main import bp
from app.main.models import Location, User
from app.modules.role.models import Role
from app.modules.role.forms import RoleForm
from app.modules.resource.models import Resource
from app.modules.resource.forms import ResourceForm
from flask_babel import _
from datetime import datetime
import markdown
from app.main.models import Audit


@bp.route('/role/add', methods=['GET', 'POST'])
@login_required
def role_add():
    if 'cancel' in request.form:
        return redirect(request.referrer)

    form = RoleForm(formdata=request.form)

    if request.method == 'POST' and form.validate_on_submit():

        role = Role(name=form.name.data)
        for r in form.resources.data:
            resource = Resource.query.get(r)
            print("Adding: Resource: {} to: {}".format(resource.name, role.name))
            role.resources.append(resource)

        role.comment = form.comment.data
        role.description = form.description.data
        db.session.add(role)
        db.session.commit()

        Audit().auditlog_new_post('role', original_data=role.to_dict(), record_name=role.name)

        flash(_('New Role is now posted!'))

        return redirect(url_for('main.index'))

    else:

        return render_template('role.html', title=_('Role'),
                               form=form)


@bp.route('/role/edit/', methods=['GET', 'POST'])
@login_required
def role_edit():

    roleid = request.args.get('role')

    if 'cancel' in request.form:
        return redirect(request.referrer)
    if 'delete' in request.form:
        return redirect(url_for('main.role_delete', role=roleid))

    role = Role.query.get(roleid)
    form = RoleForm(obj=role)

    if role is None:
        flash(_('Role not found'))
        return redirect(request.referrer)

    original_data = role.to_dict()

    if request.method == 'POST' and form.validate_on_submit():

        role.name = form.name.data
        role.description = form.description.data
        role.resources = []
        for r in form.resources.data:
            resource = Resource.query.get(r)
            print("Adding: Resource: {} to: {}".format(resource.name, role.name))
            role.resources.append(resource)

        role.comment = form.comment.data
        db.session.commit()

        Audit().auditlog_update_post('role', original_data=original_data, updated_data=role.to_dict(), record_name=role.name)

        flash(_('Your changes to the role have been saved.'))

        return redirect(url_for('main.index'))

    else:
        pre_selected_resources = [(r.id) for r in role.resources]
        form = RoleForm(resources=pre_selected_resources)
        form.name.data = role.name
        form.comment.data = role.comment
        form.description.data = role.description

        return render_template('role.html', title=_('Edit Role'),
                               form=form)


@bp.route('/role/view/', methods=['GET', 'POST'])
@login_required
def role_view():

    if 'cancel' in request.form:
        return redirect(request.referrer)

    roleid = request.args.get('role')
    if roleid is None:
        flash(_('roleid argument not found'))
        return redirect(request.referrer)

    role = Role.query.get(roleid)

    if role is None:
        flash(_('Role not found'))
        return redirect(request.referrer)

    return render_template('role.html', title=_('View Role'),
                           role=role)


@bp.route('/role/list/', methods=['GET', 'POST'])
@login_required
def role_list():

    page = request.args.get('page', 1, type=int)

    roles = Role.query.order_by(Role.name).paginate(
            page, current_app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('main.role_list', page=roles.next_num) \
        if roles.has_next else None
    prev_url = url_for('main.role_list', page=roles.prev_num) \
        if roles.has_prev else None

    return render_template('role.html', title=_('Role'),
                           roles=roles.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/role/content/', methods=['GET', 'POST'])
@login_required
def role_content():

    roleid = request.args.get('role')
    role = Role.query.get(roleid)
    if role is None:
        flash(_('Role not found'))
        return redirect(request.referrer)

    resources = role.resources

    return render_template('role.html', title=_('Role'),
                           resources=resources)


@bp.route('/role/delete/', methods=['GET', 'POST'])
@login_required
def role_delete():

    roleid = request.args.get('role')
    role = Role.query.get(roleid)

    if role is None:
        flash(_('Role was not deleted, id not found!'))
        return redirect(url_for('main.index'))

    deleted_msg = f'Role deleted: {role.name} {role.comment}'

    db.session.delete(role)
    db.session.commit()

    Audit().auditlog_delete_post('role', data=role.to_dict(), record_name=role.name)
    flash(deleted_msg)

    return redirect(url_for('main.index'))
