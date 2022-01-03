from flask import render_template, flash, redirect, url_for, request, \
    current_app
from flask_login import login_required, current_user
from app import db, audit
from app.main import bp
from app.models import User
from app.modules.access.models import Access
from app.modules.role.models import Role
from app.modules.resource.models import Resource
from app.modules.role.forms import RoleForm
from app.modules.resource.forms import ResourceForm
from app.modules.access.forms import AccessForm, ApproveAccessForm
from flask_babel import _
from datetime import datetime


@bp.route('/access/add', methods=['GET', 'POST'])
@login_required
def access_add():
    if 'cancel' in request.form:
        return redirect(request.referrer)

    form = AccessForm(formdata=request.form)

    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.get(form.user.data)
        if user is None:
            flash('User is required')
            return redirect(request.referrer)

        role = Role.query.get(form.role.data)
        if role is None:
            flash('User is required')
            return redirect(request.referrer)

        print(f"logged in user {current_user.username}")
        requestor = User.query.filter_by(username=current_user.username).first_or_404()
        if requestor is None:
            flash('logged in user is required')
            return redirect(request.referrer)

        access = Access(comment=form.comment.data,
                        start=form.start.data,
                        stop=form.stop.data
                        )

        access.user = user
        access.role = role
        access.status = "requested"
        access.request_ts = datetime.now()
        print(f'requestor: {requestor.username}')
        access.requestor = requestor.username
        db.session.add(access)
        db.session.commit()
        audit.auditlog_new_post('access', original_data=access.to_dict(), record_name=access.__tablename__)
        flash(_('New access is now posted!'))

        return redirect(url_for('main.index'))

    else:

        return render_template('access.html', title=_('Add Access'),
                               form=form)


@bp.route('/access/edit/', methods=['GET', 'POST'])
@login_required
def access_edit():

    accessid = request.args.get('access')

    if 'cancel' in request.form:
        return redirect(request.referrer)
    if 'delete' in request.form:
        return redirect(url_for('main.access_delete', access=accessid))
    if 'copy' in request.form:
        return redirect(url_for('main.access_copy', copy_from_access=accessid))
    if 'logs' in request.form:
        return redirect(url_for('main.logs_list', module='access', module_id=accessid))
    if 'ports' in request.form:
        return redirect(url_for('main.access_port_list', access=accessid))

    access = Access.query.get(accessid)
    original_data = access.to_dict()

    if access is None:
        render_template('service.html', title=_('Access is not defined'))

    print(f"logged in user {current_user.username}")
    requestor = User.query.filter_by(username=current_user.username).first_or_404()
    if requestor is None:
        flash('logged in user is required')
        return redirect(request.referrer)

    form = AccessForm(formdata=request.form, obj=access)

    if request.method == 'POST' and form.validate_on_submit():

        access.comment = form.comment.data
        user = User.query.get(form.user.data)
        if user is None:
            flash('User is required')
            return redirect(request.referrer)

        role = Role.query.get(form.role.data)
        if role is None:
            flash('User is required')
            return redirect(request.referrer)

        access.comment = form.comment.data
        access.start = form.start.data
        access.stop = form.stop.data
        access.user = user
        access.role = role
        access.status = "requested"
        access.request_ts = datetime.now()
        print(f'requestor: {requestor.username}')
        access.requestor = requestor.username

        db.session.commit()
        audit.auditlog_update_post('access', original_data=original_data, updated_data=access.to_dict(), record_name=access.__tablename__)
        flash(_('Your changes have been saved.'))

        return redirect(url_for('main.index'))

    else:
        form.user.data = access.user_id
        form.role.data = access.role_id
        return render_template('access.html', title=_('Edit Access'),
                               form=form)



@bp.route('/access/approve/', methods=['GET', 'POST'])
@login_required
def access_approve():

    accessid = request.args.get('access')

    if 'cancel' in request.form:
        return redirect(request.referrer)
    if 'logs' in request.form:
        return redirect(url_for('main.logs_list', module='access', module_id=accessid))

    access = Access.query.get(accessid)

    if access is None:
        flash(_('Access is not found'))
        return redirect(url_for('main.index'))

    if 'role' in request.form:
        return redirect(url_for('main.role_view', role=access.role.id))
    if 'user' in request.form:
        return redirect(url_for('main.user', username=access.user.username))

    original_data = access.to_dict()

# todo add admin check

    form = ApproveAccessForm(formdata=request.form, obj=access)

    if request.method == 'POST' and form.validate_on_submit():

        if 'deny' in request.form:
            access.status = "denied-by-approver"
            access.approver = current_user.username
            db.session.commit()
            flash(f"Pending Access to role: {access.role.name} for: {access.user.username} was denied")
        elif 'approve' in request.form:
            access.status = "approved"
            access.approver = current_user.username
            db.session.commit()
            flash(f"Pending Access to role: {access.role.name} for: {access.user.username} was approved")
        elif 'postpone' in request.form:
            access.status = "postponed-by-approver"
            access.approver = current_user.username
            flash(f"Pending Access to role: {access.role.name} for: {access.user.username} was postponed")
            return redirect(request.referrer)

        audit.auditlog_update_post('access', original_data=original_data, updated_data=access.to_dict(), record_name=access.__tablename__)
        return redirect(url_for('main.index'))

    else:
        form.user.data = access.user.username
        form.role.data = access.role.name
        return render_template('access.html', title=_('Approved Access'),
                               form=form)



@bp.route('/access/implement/', methods=['GET', 'POST'])
@login_required
def access_implement():

    accessid = request.args.get('access')

    if 'cancel' in request.form:
        return redirect(request.referrer)
    if 'logs' in request.form:
        return redirect(url_for('main.logs_list', module='access', module_id=accessid))

    access = Access.query.get(accessid)
    original_data = access.to_dict()

    if access is None:
        flash(_('Access is not found'))
        return redirect(url_for('main.index'))

    if 'role' in request.form:
        return redirect(url_for('main.role_view', role=access.role.id))
    if 'user' in request.form:
        return redirect(url_for('main.user', username=access.user.username))

# todo add admin check

    form = ApproveAccessForm(formdata=request.form, obj=access)

    if request.method == 'POST' and form.validate_on_submit():

        if 'deny' in request.form:
            access.status = "denied-by-implementer"
            access.implementer = current_user.username
            db.session.commit()
            flash(f"Pending Access to role: {access.role.name} for: {access.user.username} was denied")
        elif 'approve' in request.form:
            access.status = "implemented"
            access.approver = current_user.username
            db.session.commit()
            flash(f"Pending Access to role: {access.role.name} for: {access.user.username} was implemented")
        elif 'postpone' in request.form:
            access.status = "postponed-by-implementer"
            access.approver = current_user.username
            flash(f"Pending Access to role: {access.role.name} for: {access.user.username} was postponed")
            return redirect(request.referrer)

        audit.auditlog_update_post('access', original_data=original_data, updated_data=access.to_dict(), record_name=access.__tablename__)
        return redirect(url_for('main.index'))

    else:
        form.user.data = access.user.username
        form.role.data = access.role.name
        return render_template('access.html', title=_('Approved Access'),
                               form=form)


@bp.route('/access/list/', methods=['GET', 'POST'])
@login_required
def access_list():

    page = request.args.get('page', 1, type=int)
    ac = Access.query.order_by(Access.id).paginate(
                page, current_app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('main.access_list', page=ac.next_num) \
        if ac.has_next else None
    prev_url = url_for('main.access_list', page=ac.prev_num) \
        if ac.has_prev else None

    return render_template('access.html', title=_('List Access'),
                           accesses=ac.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/access/delete/', methods=['GET', 'POST'])
@login_required
def access_delete():

    accessid = request.args.get('access')
    access = Access.query.get(accessid)

    if access is None:
        flash(_('Access was not deleted, id not found!'))
        return redirect(url_for('main.index'))

    # check if pyraadmin
    deleted_msg = f'Access deleted for: {access.user.username} to: {access.role.name}\n'
    flash(deleted_msg)
    db.session.delete(access)
    db.session.commit()
    audit.auditlog_delete_post('access', data=access.to_dict(), record_name=access.__class__.__name__.lower())

    return redirect(url_for('main.index'))
